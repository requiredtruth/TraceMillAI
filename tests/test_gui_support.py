import unittest

from tracemillai.gui_support import analysis_action


class GuiSupportTests(unittest.TestCase):
    def test_empty_arguments_select_bundled_demo(self) -> None:
        self.assertEqual(analysis_action(""), ("demo.sh", ()))

    def test_operator_arguments_are_preserved(self) -> None:
        self.assertEqual(
            analysis_action('"my trace.jsonl" --out "small trace.jsonl" -- tool'),
            (
                "cli.sh",
                ("my trace.jsonl", "--out", "small trace.jsonl", "--", "tool"),
            ),
        )

    def test_malformed_arguments_fail_instead_of_being_reinterpreted(self) -> None:
        with self.assertRaises(ValueError):
            analysis_action('"unterminated')


if __name__ == "__main__":
    unittest.main()
