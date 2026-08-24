from __future__ import annotations
from dataclasses import dataclass
import hashlib, json
from pathlib import Path
import subprocess, tempfile

class TraceMillError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class MillResult:
    original_events: int
    minimized_events: int
    predicate_runs: int
    events: tuple[str, ...]

def load_jsonl(path: str | Path) -> list[str]:
    try:
        lines = [line for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError as exc:
        raise TraceMillError(f"cannot read trace: {path}") from exc
    if not lines:
        raise TraceMillError("trace contains no events")
    for number, line in enumerate(lines, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            raise TraceMillError(f"line {number} is not JSON: {exc.msg}") from exc
    return lines

def _parts(length: int, count: int) -> list[tuple[int, int]]:
    return [(length * i // count, length * (i + 1) // count) for i in range(count)]

def minimize(events: list[str], command: list[str], *, timeout: float = 30.0, failing_code: int | None = None, max_runs: int = 500) -> MillResult:
    if not events or not command:
        raise ValueError("events and predicate command cannot be empty")
    if timeout <= 0 or max_runs < 1:
        raise ValueError("timeout and max_runs must be positive")
    runs = 0
    cache: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="tracemill-") as temporary:
        candidate_path = Path(temporary) / "candidate.jsonl"

        def fails(candidate: list[str]) -> bool:
            nonlocal runs
            content = "\n".join(candidate) + "\n"
            key = hashlib.sha256(content.encode()).hexdigest()
            if key in cache:
                return cache[key]
            if runs >= max_runs:
                raise TraceMillError(f"predicate run limit reached: {max_runs}")
            candidate_path.write_text(content, encoding="utf-8")
            resolved = [str(candidate_path) if item == "{trace}" else item for item in command]
            if "{trace}" not in command:
                resolved.append(str(candidate_path))
            try:
                completed = subprocess.run(resolved, capture_output=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired as exc:
                raise TraceMillError(f"predicate timed out after {timeout:g}s") from exc
            runs += 1
            outcome = completed.returncode != 0 if failing_code is None else completed.returncode == failing_code
            cache[key] = outcome
            return outcome

        current = list(events)
        if not fails(current):
            raise TraceMillError("the original trace does not reproduce the requested failure")
        granularity = 2
        while len(current) >= 2:
            reduced = False
            for start, end in _parts(len(current), min(granularity, len(current))):
                candidate = current[:start] + current[end:]
                if candidate and fails(candidate):
                    current = candidate
                    granularity = max(2, granularity - 1)
                    reduced = True
                    break
            if reduced:
                continue
            if granularity >= len(current):
                break
            granularity = min(len(current), granularity * 2)
    return MillResult(len(events), len(current), runs, tuple(current))
