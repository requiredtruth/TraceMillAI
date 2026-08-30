from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
from .mill import TraceMillError, load_jsonl, minimize

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reduce JSONL traces while preserving an external failure.")
    parser.add_argument("trace")
    parser.add_argument("--out", default="minimized.jsonl")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-runs", type=int, default=500)
    parser.add_argument("--failing-code", type=int)
    raw_arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        delimiter = raw_arguments.index("--")
    except ValueError:
        if any(argument in {"-h", "--help"} for argument in raw_arguments):
            parser.parse_args(raw_arguments)
        parser.error("provide the replay predicate after --")
    args = parser.parse_args(raw_arguments[:delimiter])
    command = raw_arguments[delimiter + 1 :]
    if not command:
        parser.error("provide the replay predicate after --")
    try:
        result = minimize(load_jsonl(args.trace), command, timeout=args.timeout, failing_code=args.failing_code, max_runs=args.max_runs)
        Path(args.out).write_text("\n".join(result.events) + "\n", encoding="utf-8")
    except (OSError, ValueError, TraceMillError) as exc:
        print(f"tracemillai: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"original_events": result.original_events, "minimized_events": result.minimized_events, "predicate_runs": result.predicate_runs, "output": args.out}, indent=2))
    return 0
