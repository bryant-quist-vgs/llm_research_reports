#!/usr/bin/env python3
# rdm.py — recursive decision tree runner over a POST /v1/systemone endpoint.
# Built against contract v0 (rdm_contract.md). PROPOSAL: never executed.
"""Recursive decision models, minimal reference implementation.

A tree is a table of nodes. Each node asks ONE typed Choice question of a
non-generative decision model; the chosen option may name the next node. Code owns
context, control flow, depth limit and stopping rule. No generative model is called.

Module use:
    result = decide(tree, state, HttpBackend("https://api.typesafe.ai", key, "jev-latest"))

CLI use:
    python rdm.py --tree trees/pr_triage.json --state diff.txt --min-prob 0.7

Through the LM Studio inference tunnel (LOCAL_LLM_SERVER and EXPECTED_LMSTUDIO_MODEL
are the tunnel scripts' own variables; see README.md):
    LOCAL_LLM_SERVER=http://localhost:1234 EXPECTED_LMSTUDIO_MODEL=<decision-model-key> \
        python rdm.py --tree trees/pr_triage.json --state state.json
"""
from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

NONE_OPTION = "__none__"
NONE_DESCRIPTION = "None of the listed options fits."
RESOLVE_NODE = "__resolve__"  # trace name of the final "which leaf" question
PATH_SEPARATOR = " > "
DEFAULT_BASE_URL = "https://api.typesafe.ai"
DEFAULT_HOSTED_MODEL = "jev-latest"
TYPESAFE_HOST = "api.typesafe.ai"
RETRYABLE_STATUS = (429, 500, 502, 503, 504)

# A backend takes (state, instructions, criteria) and returns
# (probabilities by option name, input token count).
Backend = Callable[[Any, str, dict[str, str]], tuple[dict[str, float], int]]


class TreeError(ValueError):
    """The tree definition is invalid. Raised before any model request."""


class BackendError(RuntimeError):
    """The endpoint failed or returned something that is not a valid answer."""


@dataclass(frozen=True)
class _Path:
    steps: tuple[dict[str, Any], ...]  # accepted {"node", "option", "probability"}
    node: str | None  # next node to ask; None once a leaf has been reached
    value: Any = None  # leaf value, set when node is None
    reason: str = ""  # why a partial path stopped

    @property
    def joint(self) -> float:
        return math.prod(step["probability"] for step in self.steps)


# --------------------------------------------------------------------------- tree


def validate_tree(tree: Any, max_options: int = 255) -> None:
    """Contract behavior 1. Raises TreeError; makes no network call."""
    if not isinstance(tree, dict) or not isinstance(tree.get("nodes"), dict):
        raise TreeError('tree must be an object with "root" and "nodes"')
    nodes = tree["nodes"]
    if tree.get("root") not in nodes:
        raise TreeError('"root" must name a node in "nodes"')
    resolve = tree.get("resolve_instructions")
    if resolve is not None and not (isinstance(resolve, str) and resolve):
        raise TreeError('"resolve_instructions" must be a non-empty string')
    for node_id, node in nodes.items():
        where = f"node {node_id!r}"
        if not isinstance(node, dict):
            raise TreeError(f"{where}: must be an object")
        if not isinstance(node.get("instructions"), str) or not node["instructions"]:
            raise TreeError(f"{where}: instructions must be a non-empty string")
        options = node.get("options")
        if not isinstance(options, dict):
            raise TreeError(f"{where}: options must be an object")
        if NONE_OPTION in options:
            raise TreeError(f"{where}: {NONE_OPTION!r} is reserved; use allow_none")
        count = len(options) + (1 if node.get("allow_none") else 0)
        if not 2 <= count <= max_options:
            raise TreeError(f"{where}: needs 2..{max_options} options, has {count}")
        for name, option in options.items():
            if not isinstance(option, dict) or not isinstance(
                option.get("description"), str
            ):
                raise TreeError(f"{where}: option {name!r} needs a string description")
            if "next" in option and option["next"] not in nodes:
                raise TreeError(f"{where}: option {name!r} points to an unknown node")
        min_prob = node.get("min_prob")
        if min_prob is not None and not _is_probability(min_prob, allow_zero=False):
            raise TreeError(f"{where}: min_prob must be in (0, 1]")
        keys = node.get("state_keys")
        if keys is not None and not (
            isinstance(keys, list) and all(isinstance(k, str) for k in keys)
        ):
            raise TreeError(f"{where}: state_keys must be an array of strings")


def _is_probability(x: Any, allow_zero: bool = True) -> bool:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        return False
    return (0 <= x <= 1) if allow_zero else (0 < x <= 1)


def _check_probabilities(probs: Any, names: list[str], node_id: str) -> None:
    """Contract behavior 10: the answer must cover exactly the options sent."""
    if not isinstance(probs, dict) or set(probs) != set(names):
        raise BackendError(f"node {node_id!r}: answer options differ from those sent")
    if not all(_is_probability(p) for p in probs.values()):
        raise BackendError(f"node {node_id!r}: probability is not a number in [0, 1]")


def _view(state: Any, node: dict[str, Any]) -> Any:
    """Contract behavior 2: code chooses what context a node sees."""
    if isinstance(state, dict) and node.get("state_keys") is not None:
        return {k: state[k] for k in node["state_keys"] if k in state}
    return state


# ------------------------------------------------------------------------- decide


def decide(
    tree: dict[str, Any],
    state: Any,
    backend: Backend,
    *,
    min_prob: float = 0.70,
    max_depth: int = 8,
    max_calls: int = 64,
    beam_width: int = 1,
    branch_ratio: float = 0.0,
    max_options: int = 255,
) -> dict[str, Any]:
    """Run one recursive decision. Returns the result object described in the contract."""
    validate_tree(tree, max_options)
    if not _is_probability(min_prob, allow_zero=False):
        raise TreeError("min_prob must be in (0, 1]")
    if max_depth < 1 or max_calls < 1 or beam_width < 1:
        raise TreeError("max_depth, max_calls and beam_width must be >= 1")
    if not _is_probability(branch_ratio):
        raise TreeError("branch_ratio must be in [0, 1]")
    ratio_mode = branch_ratio > 0
    if ratio_mode and beam_width > 1:
        raise TreeError("branch_ratio and beam_width > 1 are mutually exclusive")

    nodes = tree["nodes"]
    live: list[_Path] = [_Path(steps=(), node=tree["root"])]
    finished: list[_Path] = []  # reached a leaf
    stopped: list[_Path] = []  # abstained, hit the depth limit, or ran out of budget
    trace: list[dict[str, Any]] = []
    calls = 0
    input_tokens = 0
    budget_hit = False

    while live:
        # Joint probability only falls with depth, so a finished leaf that already
        # beats every live path cannot be overtaken (behavior 7). Ratio mode does not
        # rank by joint probability, so it explores every followed branch (behavior 12).
        if (
            not ratio_mode
            and finished
            and max(f.joint for f in finished) >= max(p.joint for p in live)
        ):
            break
        candidates: list[_Path] = []
        for path in live:
            depth = len(path.steps) + 1
            if depth > max_depth:  # behavior 5
                stopped.append(_Path(path.steps, None, reason="depth_exceeded"))
                continue
            if calls >= max_calls:  # behavior 6
                budget_hit = True
                stopped.append(_Path(path.steps, None, reason="budget_exceeded"))
                continue

            node_id = path.node
            node = nodes[node_id]
            criteria = {n: o["description"] for n, o in node["options"].items()}
            if node.get("allow_none"):
                criteria[NONE_OPTION] = NONE_DESCRIPTION
            names = list(criteria)

            probs, used = backend(_view(state, node), node["instructions"], criteria)
            calls += 1
            input_tokens += used
            _check_probabilities(probs, names, node_id)

            # behavior 3: arg-max of probabilities, ties by declaration order
            ranked = sorted(names, key=lambda n: (-probs[n], names.index(n)))
            top = ranked[0]
            threshold = node.get("min_prob", min_prob)
            accepted = top != NONE_OPTION and probs[top] >= threshold  # behavior 4
            trace.append(
                {
                    "node": node_id,
                    "depth": depth,
                    "probabilities": {n: probs[n] for n in names},
                    "top": top,
                    "top_probability": probs[top],
                    "accepted": accepted,
                    "input_tokens": used,
                }
            )
            if not accepted:
                stopped.append(_Path(path.steps, None, reason="abstained"))
                continue

            # Options followed: those meeting the threshold (greedy and beam), or
            # those at least branch_ratio times as likely as the top (ratio mode).
            floor = probs[top] * branch_ratio if ratio_mode else threshold
            for name in ranked:
                if probs[name] < floor:
                    break
                if name == NONE_OPTION:
                    continue
                option = node["options"][name]
                step = {"node": node_id, "option": name, "probability": probs[name]}
                steps = path.steps + (step,)
                if "next" in option:
                    candidates.append(_Path(steps, option["next"]))
                else:
                    candidates.append(_Path(steps, None, option.get("value", name)))

        candidates.sort(key=lambda p: -p.joint)  # stable: earlier candidates win ties
        kept = candidates if ratio_mode else candidates[:beam_width]
        live = [p for p in kept if p.node is not None]
        finished.extend(p for p in kept if p.node is None)

    resolve_probability = None
    if finished:  # behavior 8
        finished.sort(key=lambda p: -p.joint)  # stable
        best = finished[0]
        status, value = "decided", best.value
        labels = [PATH_SEPARATOR.join(s["option"] for s in p.steps) for p in finished]
        if (  # behavior 12: more than one leaf came back, so ask again among those
            ratio_mode
            and len(finished) > 1
            and calls < max_calls
            and len(finished) <= max_options
            and len(set(labels)) == len(labels)
        ):
            root = nodes[tree["root"]]
            criteria = {
                label: nodes[p.steps[-1]["node"]]["options"][p.steps[-1]["option"]]["description"]
                for label, p in zip(labels, finished)
            }
            instructions = tree.get("resolve_instructions", root["instructions"])
            probs, used = backend(_view(state, root), instructions, criteria)
            calls += 1
            input_tokens += used
            _check_probabilities(probs, labels, RESOLVE_NODE)
            top = min(labels, key=lambda n: (-probs[n], labels.index(n)))
            best = finished[labels.index(top)]
            resolve_probability = probs[top]
            accepted = probs[top] >= min_prob
            trace.append(
                {
                    "node": RESOLVE_NODE,
                    "depth": 0,
                    "probabilities": {n: probs[n] for n in labels},
                    "top": top,
                    "top_probability": probs[top],
                    "accepted": accepted,
                    "input_tokens": used,
                }
            )
            status, value = ("decided", best.value) if accepted else ("abstained", None)
    else:
        best = max(stopped, key=lambda p: (len(p.steps), p.joint))
        value = None
        if budget_hit:
            status = "budget_exceeded"
        elif any(p.reason == "depth_exceeded" for p in stopped):
            status = "depth_exceeded"
        else:
            status = "abstained"

    return {
        "status": status,
        "value": value,
        "path": list(best.steps),
        "joint_probability": best.joint,
        "resolve_probability": resolve_probability,
        "calls": calls,
        "input_tokens": input_tokens,
        "trace": trace,
    }


# ----------------------------------------------------------------------- endpoint


def _split(base_url: str) -> urllib.parse.SplitResult:
    try:
        return urllib.parse.urlsplit(base_url)
    except ValueError:
        raise TreeError("base URL must be http(s)://host[:port]") from None


def _is_loopback(host: str | None) -> bool:
    if not host:
        return False
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def resolve_endpoint(
    base_url: str | None, model: str | None, environ: Any = None
) -> tuple[str, str, str | None]:
    """Contract behavior 13: choose base URL, model and key. Makes no request.

    The inference tunnel's own variables are honored: LOCAL_LLM_SERVER for the base
    URL and, for a loopback endpoint only, EXPECTED_LMSTUDIO_MODEL for the model.
    TYPESAFE_API_KEY is never sent anywhere but api.typesafe.ai.
    """
    env = os.environ if environ is None else environ
    base_url = (
        base_url or env.get("RDM_BASE_URL") or env.get("LOCAL_LLM_SERVER") or DEFAULT_BASE_URL
    )
    host = _split(base_url).hostname
    if _is_loopback(host):
        model = model or env.get("RDM_MODEL") or env.get("EXPECTED_LMSTUDIO_MODEL")
        if not model:
            raise TreeError(
                "a local endpoint needs a model: pass --model, or set RDM_MODEL or "
                "EXPECTED_LMSTUDIO_MODEL to the server's decision-model key"
            )
    else:
        model = model or env.get("RDM_MODEL") or DEFAULT_HOSTED_MODEL
    api_key = env.get("RDM_API_KEY") or (
        env.get("TYPESAFE_API_KEY") if host == TYPESAFE_HOST else None
    )
    return base_url, model, api_key or None


# --------------------------------------------------------------------------- http


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so the bearer token is never forwarded to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


class HttpBackend:
    """POST {base_url}/v1/systemone with one choice question named "q"."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        model: str,
        *,
        timeout: float = 30.0,
        retries: int = 2,
    ) -> None:
        parts = _split(base_url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise TreeError("base URL must be http(s)://host[:port]")
        self.url = base_url.rstrip("/") + "/v1/systemone"
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retries = retries
        handlers: list[Any] = [_NoRedirect]
        if _is_loopback(parts.hostname):
            # Behavior 14: a localhost tunnel is reached directly. An explicit empty
            # ProxyHandler replaces the default one that reads proxy settings.
            handlers.append(urllib.request.ProxyHandler({}))
        self._opener = urllib.request.build_opener(*handlers)

    def __call__(
        self, state: Any, instructions: str, criteria: dict[str, str]
    ) -> tuple[dict[str, float], int]:
        body = {
            "model": self.model,
            "state": state,
            "questions": {
                "q": {"type": "choice", "instructions": instructions, "criteria": criteria}
            },
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            self.url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
        )

        delay = 0.5
        for attempt in range(self.retries + 1):  # behavior 9
            last = attempt == self.retries
            try:
                with self._opener.open(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as err:
                if err.code == 501:
                    raise BackendError(
                        "HTTP 501 from endpoint: the server does not answer decision "
                        "questions with this model (is it a decision model?)"
                    ) from None
                if last or err.code not in RETRYABLE_STATUS:
                    raise BackendError(f"HTTP {err.code} from endpoint") from None
                wait = _retry_after(err.headers.get("Retry-After"), delay)
            except (urllib.error.URLError, http.client.HTTPException, OSError):
                if last:
                    raise BackendError("could not reach endpoint") from None
                wait = delay
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise BackendError("endpoint returned non-JSON") from None
            time.sleep(wait)
            delay *= 2

        try:
            probs = payload["answers"]["q"]["probabilities"]
        except (KeyError, TypeError):
            raise BackendError("response lacks answers.q.probabilities") from None
        usage = payload.get("usage") if isinstance(payload, dict) else None
        used = usage.get("input_tokens", 0) if isinstance(usage, dict) else 0
        return probs, used if isinstance(used, int) and not isinstance(used, bool) else 0


def _retry_after(header: str | None, default: float) -> float:
    try:
        return min(max(float(header), 0.0), 10.0) if header else default
    except ValueError:
        return default


# ---------------------------------------------------------------------------- cli


def _read_state(path: str) -> Any:
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tree", required=True)
    parser.add_argument("--state", required=True, help="path, or - for stdin")
    parser.add_argument("--base-url", help="default: RDM_BASE_URL, LOCAL_LLM_SERVER, TypeSafe")
    parser.add_argument("--model", help="default: RDM_MODEL, EXPECTED_LMSTUDIO_MODEL (local)")
    parser.add_argument("--min-prob", type=float, default=0.70)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--max-calls", type=int, default=64)
    parser.add_argument("--beam-width", type=int, default=1)
    parser.add_argument("--branch-ratio", type=float, default=0.0)
    parser.add_argument("--max-options", type=int, default=255)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--trace-out")
    args = parser.parse_args(argv)

    try:
        base_url, model, api_key = resolve_endpoint(args.base_url, args.model)
        with open(args.tree, encoding="utf-8") as handle:
            tree = json.load(handle)
        state = _read_state(args.state)
        backend = HttpBackend(
            base_url, api_key, model, timeout=args.timeout, retries=args.retries
        )
        result = decide(
            tree,
            state,
            backend,
            min_prob=args.min_prob,
            max_depth=args.max_depth,
            max_calls=args.max_calls,
            beam_width=args.beam_width,
            branch_ratio=args.branch_ratio,
            max_options=args.max_options,
        )
    except (TreeError, OSError, json.JSONDecodeError) as err:
        print(f"rdm: {err}", file=sys.stderr)
        return 2
    except BackendError as err:
        print(f"rdm: backend error: {err}", file=sys.stderr)
        return 4

    text = json.dumps(result)
    print(text)
    if args.trace_out:
        try:
            with open(args.trace_out, "w", encoding="utf-8") as handle:
                handle.write(text + "\n")
        except OSError as err:
            print(f"rdm: could not write trace: {err}", file=sys.stderr)
            return 2
    return 0 if result["status"] == "decided" else 3


if __name__ == "__main__":
    sys.exit(main())
