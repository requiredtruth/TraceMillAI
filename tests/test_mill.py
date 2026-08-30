from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

from tracemillai.cli import main
from tracemillai.mill import TraceMillError, minimize

PREDICATE = "import json,sys; kinds={json.loads(line)['kind'] for line in open(sys.argv[1])}; sys.exit(1 if {'trigger','crash'} <= kinds else 0)"

class MillTests(unittest.TestCase):
    def test_help_does_not_require_predicate_delimiter(self) -> None:
        with redirect_stdout(StringIO()), self.assertRaises(SystemExit) as raised:
            main(["--help"])
        self.assertEqual(raised.exception.code, 0)

    def test_removes_irrelevant_events(self) -> None:
        kinds = ["noise", "trigger", "more", "crash", "tail"]
        events = [json.dumps({"kind": kind, "n": i}) for i, kind in enumerate(kinds)]
        result = minimize(events, [sys.executable, "-c", PREDICATE, "{trace}"])
        self.assertEqual(result.minimized_events, 2)
        self.assertEqual({json.loads(line)["kind"] for line in result.events}, {"trigger", "crash"})
        self.assertGreater(result.predicate_runs, 1)

    def test_requires_original_failure(self) -> None:
        with self.assertRaisesRegex(TraceMillError, "does not reproduce"):
            minimize([json.dumps({"kind": "noise"})], [sys.executable, "-c", PREDICATE, "{trace}"])

    def test_documented_option_order_writes_minimized_trace(self) -> None:
        events = [
            json.dumps({"kind": kind})
            for kind in ("noise", "trigger", "extra", "crash")
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "failure.jsonl"
            output = root / "minimal.jsonl"
            source.write_text("\n".join(events) + "\n", encoding="utf-8")
            with redirect_stdout(StringIO()):
                status = main(
                    [
                        str(source),
                        "--out",
                        str(output),
                        "--",
                        sys.executable,
                        "-c",
                        PREDICATE,
                        "{trace}",
                    ]
                )
            minimized = [json.loads(line) for line in output.read_text().splitlines()]
        self.assertEqual(status, 0)
        self.assertEqual({event["kind"] for event in minimized}, {"trigger", "crash"})

if __name__ == "__main__":
    unittest.main()
