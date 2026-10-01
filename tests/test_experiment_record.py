import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORD = ROOT / "experiments" / "codex-external-auth.md"


class ExperimentRecordTest(unittest.TestCase):
    def test_required_answer_is_first_line(self):
        first = RECORD.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(
            first,
            "Codex 0.156.0 supports external auth in app-server mode via "
            "account/chatgptAuthTokens/refresh.",
        )

    def test_record_has_timestamped_observations_and_hashes(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertGreaterEqual(len(re.findall(r"2026-10-01T\d\d:\d\d:\d\d\+00:00", text)), 8)
        self.assertIn("SHA-256", text)
        self.assertIn("turn/completed", text)


if __name__ == "__main__":
    unittest.main()
