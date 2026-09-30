"""Tests for the inventory module."""

import io
import json
import os
import tempfile
import unittest
import unittest.mock

from inventory.store import Store
from inventory.cli import main


# ── Store unit tests ──────────────────────────────────────────────────────

class TestStoreAdd(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def test_add_basic(self):
        self.store.add("apple", 5)
        self.assertEqual(self.store.quantity("apple"), 5)

    def test_add_case_insensitive(self):
        self.store.add("Apple", 5)
        self.assertEqual(self.store.quantity("apple"), 5)
        self.assertEqual(self.store.quantity("APPLE"), 5)

    def test_add_lowercase_stored(self):
        self.store.add("Banana", 3)
        self.assertIn("banana", self.store._items)
        self.assertNotIn("Banana", self.store._items)

    def test_add_accumulates(self):
        self.store.add("apple", 5)
        self.store.add("apple", 3)
        self.assertEqual(self.store.quantity("apple"), 8)

    def test_add_different_items(self):
        self.store.add("apple", 5)
        self.store.add("banana", 3)
        self.assertEqual(self.store.quantity("apple"), 5)
        self.assertEqual(self.store.quantity("banana"), 3)

    def test_add_zero_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("apple", 0)

    def test_add_negative_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("apple", -1)

    def test_add_float_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("apple", 1.5)

    def test_add_string_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("apple", "5")

    def test_add_bool_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("apple", True)


class TestStoreRemove(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def test_remove_basic(self):
        self.store.add("apple", 5)
        self.store.remove("apple", 2)
        self.assertEqual(self.store.quantity("apple"), 3)

    def test_remove_case_insensitive(self):
        self.store.add("apple", 5)
        self.store.remove("APPLE", 2)
        self.assertEqual(self.store.quantity("apple"), 3)

    def test_remove_to_zero_deletes(self):
        self.store.add("apple", 2)
        self.store.remove("apple", 2)
        self.assertEqual(self.store.quantity("apple"), 0)
        self.assertNotIn("apple", self.store._items)

    def test_remove_missing_raises(self):
        with self.assertRaises(ValueError):
            self.store.remove("apple", 1)

    def test_remove_exceeds_quantity_raises(self):
        self.store.add("apple", 2)
        with self.assertRaises(ValueError):
            self.store.remove("apple", 5)

    def test_remove_zero_raises(self):
        self.store.add("apple", 5)
        with self.assertRaises(ValueError):
            self.store.remove("apple", 0)

    def test_remove_negative_raises(self):
        self.store.add("apple", 5)
        with self.assertRaises(ValueError):
            self.store.remove("apple", -1)


class TestStoreQuantity(unittest.TestCase):
    def test_quantity_absent_returns_zero(self):
        self.assertEqual(Store().quantity("apple"), 0)

    def test_quantity_present(self):
        s = Store()
        s.add("apple", 4)
        self.assertEqual(s.quantity("apple"), 4)

    def test_quantity_case_insensitive(self):
        s = Store()
        s.add("apple", 4)
        self.assertEqual(s.quantity("APPLE"), 4)


class TestStoreSerialization(unittest.TestCase):
    def test_to_json_empty(self):
        self.assertEqual(Store().to_json(), "{}")

    def test_to_json_single_item(self):
        s = Store()
        s.add("banana", 3)
        self.assertEqual(s.to_json(), '{"banana": 3}')

    def test_to_json_sorted_keys(self):
        s = Store()
        s.add("cherry", 1)
        s.add("apple", 2)
        s.add("banana", 3)
        self.assertEqual(s.to_json(), '{"apple": 2, "banana": 3, "cherry": 1}')

    def test_roundtrip_single_item(self):
        s = Store()
        s.add("apple", 5)
        json_str = s.to_json()
        s2 = Store.from_json(json_str)
        self.assertEqual(s2.quantity("apple"), 5)

    def test_roundtrip_multiple_items(self):
        s = Store()
        s.add("cherry", 1)
        s.add("apple", 2)
        s.add("banana", 3)
        json_str = s.to_json()
        s2 = Store.from_json(json_str)
        self.assertEqual(s2.quantity("apple"), 2)
        self.assertEqual(s2.quantity("banana"), 3)
        self.assertEqual(s2.quantity("cherry"), 1)

    def test_roundtrip_empty(self):
        self.assertEqual(Store.from_json("{}").to_json(), "{}")

    def test_from_json_creates_store(self):
        s = Store.from_json('{"x": 1}')
        self.assertEqual(s.quantity("x"), 1)


# ── CLI unit tests ────────────────────────────────────────────────────────

class TestCliMain(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    def _path(self, name="inv.json"):
        return os.path.join(self.tmpdir, name)

    def test_show_empty_file(self):
        code = main(["--file", self._path(), "show"])
        self.assertEqual(code, 0)

    def test_show_after_add(self):
        main(["--file", self._path(), "add", "apple", "5"])
        code = main(["--file", self._path(), "show"])
        self.assertEqual(code, 0)

    def test_add(self):
        code = main(["--file", self._path(), "add", "apple", "3"])
        self.assertEqual(code, 0)
        with open(self._path()) as f:
            data = json.load(f)
        self.assertEqual(data["apple"], 3)

    def test_remove(self):
        main(["--file", self._path(), "add", "apple", "5"])
        code = main(["--file", self._path(), "remove", "apple", "2"])
        self.assertEqual(code, 0)
        with open(self._path()) as f:
            data = json.load(f)
        self.assertEqual(data["apple"], 3)

    def test_remove_to_zero(self):
        main(["--file", self._path(), "add", "apple", "2"])
        code = main(["--file", self._path(), "remove", "apple", "2"])
        self.assertEqual(code, 0)
        with open(self._path()) as f:
            data = json.load(f)
        self.assertNotIn("apple", data)

    def test_unknown_command(self):
        code = main(["--file", self._path(), "unknown"])
        self.assertEqual(code, 1)

    def test_no_command(self):
        code = main(["--file", self._path()])
        self.assertEqual(code, 1)

    def test_add_invalid_qty_returns_2(self):
        with unittest.mock.patch.object(Store, "add", side_effect=ValueError("qty must be a positive int")):
            code = main(["--file", self._path(), "add", "apple", "5"])
        self.assertEqual(code, 2)

    def test_remove_invalid_returns_2(self):
        with unittest.mock.patch.object(Store, "remove", side_effect=ValueError("item 'apple' is not in the store")):
            code = main(["--file", self._path(), "remove", "apple", "1"])
        self.assertEqual(code, 2)

    def test_show_prints_sorted(self):
        main(["--file", self._path(), "add", "cherry", "1"])
        main(["--file", self._path(), "add", "apple", "2"])
        main(["--file", self._path(), "add", "banana", "3"])
        captured = io.StringIO()
        with unittest.mock.patch("sys.stdout", captured):
            code = main(["--file", self._path(), "show"])
            self.assertEqual(code, 0)
        output = captured.getvalue()
        self.assertIn("apple: 2\n", output)
        self.assertIn("banana: 3\n", output)
        self.assertIn("cherry: 1\n", output)
        # Verify order
        lines = [l.strip() for l in output.strip().splitlines()]
        self.assertEqual(lines, ["apple: 2", "banana: 3", "cherry: 1"])

    def test_file_created_if_missing(self):
        path = self._path("missing.json")
        self.assertFalse(os.path.exists(path))
        code = main(["--file", path, "add", "apple", "1"])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(path))


# ── Makefile lint scope test (verify py_compile works) ───────────────────

class TestLintScope(unittest.TestCase):
    def test_all_python_files_compile(self):
        import py_compile
        import pathlib

        repo = pathlib.Path(__file__).resolve().parent.parent
        inv_py = repo / "inventory" / "store.py"
        cli_py = repo / "inventory" / "cli.py"
        init_py = repo / "inventory" / "__init__.py"

        for fpath in [inv_py, cli_py, init_py]:
            self.assertTrue(fpath.exists(), f"{fpath} should exist")
            try:
                py_compile.compile(str(fpath), doraise=True)
            except py_compile.PyCompileError as exc:
                self.fail(f"{fpath} failed to compile: {exc}")


if __name__ == "__main__":
    unittest.main()
