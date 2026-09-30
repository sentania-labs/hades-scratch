import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from inventory.cli import main
from inventory.store import Store


class StoreTest(unittest.TestCase):
    def test_add_is_case_insensitive(self):
        s = Store()
        s.add("Apple", 2)
        s.add("apple", 3)
        self.assertEqual(s.quantity("APPLE"), 5)

    def test_add_rejects_non_positive(self):
        with self.assertRaises(ValueError):
            Store().add("x", 0)

    def test_remove_to_zero_deletes(self):
        s = Store()
        s.add("x", 2)
        s.remove("x", 2)
        self.assertEqual(s.quantity("x"), 0)
        self.assertEqual(json.loads(s.to_json()), {})

    def test_remove_below_zero_raises(self):
        s = Store()
        s.add("x", 1)
        with self.assertRaises(ValueError):
            s.remove("x", 2)

    def test_json_round_trip_sorted(self):
        s = Store()
        s.add("pear", 1)
        s.add("apple", 2)
        text = s.to_json()
        self.assertEqual(list(json.loads(text)), ["apple", "pear"])
        self.assertEqual(Store.from_json(text).to_json(), text)


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_add_show_remove(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "inv.json")
            self.assertEqual(self.run_cli("--file", path, "add", "Pear", "2")[0], 0)
            self.assertEqual(self.run_cli("--file", path, "add", "apple", "1")[0], 0)
            code, out, _ = self.run_cli("--file", path, "show")
            self.assertEqual((code, out), (0, "apple: 1\npear: 2\n"))
            code, _, err = self.run_cli("--file", path, "remove", "pear", "5")
            self.assertEqual(code, 2)
            self.assertTrue(err.startswith("error: "))

    def test_unknown_command(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli("--file", os.path.join(d, "i.json"), "fly")[0], 1)


if __name__ == "__main__":
    unittest.main()
