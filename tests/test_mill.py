import json
import sys
import unittest

from tracemillai.mill import TraceMillError, minimize

PREDICATE = "import json,sys; kinds={json.loads(line)['kind'] for line in open(sys.argv[1])}; sys.exit(1 if {'trigger','crash'} <= kinds else 0)"

class MillTests(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
