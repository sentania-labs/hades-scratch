"""Tests for inventory module and CLI."""

import io
import json
import os
import shutil
import sys
import tempfile
import unittest

from inventory.cli import main
from inventory.store import Store


class TestStoreBasics(unittest.TestCase):
    """Test basic Store operations."""

    def test_init_empty(self) -> None:
        store = Store()
        self.assertEqual(len(store), 0)
        self.assertEqual(store.quantity("anything"), 0)
        self.assertEqual(store.to_json(), "{}")

    def test_init_with_dict(self) -> None:
        store = Store({"apple": 3, "Banana": 5})
        self.assertEqual(store.quantity("apple"), 3)
        self.assertEqual(store.quantity("banana"), 5)
        self.assertEqual(len(store), 2)

    def test_init_with_invalid(self) -> None:
        with self.assertRaises(ValueError):
            Store("not a dict")  # type: ignore[arg-type]


class TestStoreAdd(unittest.TestCase):
    """Test Store.add requirements."""

    def setUp(self) -> None:
        self.store = Store()

    def test_add_positive_int(self) -> None:
        self.store.add("widget", 10)
        self.assertEqual(self.store.quantity("widget"), 10)

    def test_add_accumulates(self) -> None:
        self.store.add("widget", 10)
        self.store.add("widget", 5)
        self.assertEqual(self.store.quantity("widget"), 15)

    def test_add_case_insensitive_and_stored_lowercase(self) -> None:
        self.store.add("Widget", 10)
        self.assertEqual(self.store.quantity("WIDGET"), 10)
        self.assertEqual(self.store.quantity("widget"), 10)
        self.store.add("WIDGET", 5)
        self.assertEqual(self.store.quantity("WiDgEt"), 15)
        # Verify stored lowercase in JSON
        data = json.loads(self.store.to_json())
        self.assertIn("widget", data)
        self.assertNotIn("Widget", data)
        self.assertNotIn("WIDGET", data)

    def test_add_qty_zero_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("item", 0)

    def test_add_qty_negative_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("item", -5)

    def test_add_qty_float_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("item", 3.14)  # type: ignore[arg-type]

    def test_add_qty_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("item", "10")  # type: ignore[arg-type]

    def test_add_qty_bool_raises_value_error(self) -> None:
        # bool is an int subclass in Python; it must be rejected
        with self.assertRaises(ValueError):
            self.store.add("item", True)  # type: ignore[arg-type]

    def test_add_name_non_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add(123, 5)  # type: ignore[arg-type]


class TestStoreRemove(unittest.TestCase):
    """Test Store.remove requirements."""

    def setUp(self) -> None:
        self.store = Store()
        self.store.add("gadget", 10)

    def test_remove_partial(self) -> None:
        self.store.remove("gadget", 4)
        self.assertEqual(self.store.quantity("gadget"), 6)

    def test_remove_case_insensitive(self) -> None:
        self.store.remove("GADGET", 3)
        self.assertEqual(self.store.quantity("gadget"), 7)

    def test_remove_exact_deletes_item(self) -> None:
        self.store.remove("gadget", 10)
        self.assertEqual(self.store.quantity("gadget"), 0)
        self.assertNotIn("gadget", self.store)
        self.assertEqual(self.store.to_json(), "{}")
        # Removing again must raise ValueError because it is missing
        with self.assertRaises(ValueError):
            self.store.remove("gadget", 1)

    def test_remove_missing_item_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("nonexistent", 1)

    def test_remove_below_zero_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("gadget", 11)
        # Quantity should remain untouched on failure
        self.assertEqual(self.store.quantity("gadget"), 10)

    def test_remove_invalid_qty_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("gadget", 0)
        with self.assertRaises(ValueError):
            self.store.remove("gadget", -2)
        with self.assertRaises(ValueError):
            self.store.remove("gadget", 2.5)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.store.remove("gadget", True)  # type: ignore[arg-type]

    def test_remove_invalid_name_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove(None, 1)  # type: ignore[arg-type]


class TestStoreQuantity(unittest.TestCase):
    """Test Store.quantity requirements."""

    def test_quantity_existing_and_missing(self) -> None:
        store = Store()
        store.add("ItemA", 42)
        self.assertEqual(store.quantity("ItemA"), 42)
        self.assertEqual(store.quantity("itema"), 42)
        self.assertEqual(store.quantity("ITEMA"), 42)
        self.assertEqual(store.quantity("ItemB"), 0)
        self.assertEqual(store.quantity(""), 0)
        self.assertEqual(store.quantity(123), 0)  # type: ignore[arg-type]


class TestStoreJson(unittest.TestCase):
    """Test Store to_json and from_json round-trip."""

    def test_empty_json(self) -> None:
        store = Store()
        self.assertEqual(store.to_json(), "{}")
        restored = Store.from_json("{}")
        self.assertEqual(restored.to_json(), "{}")
        self.assertEqual(len(restored), 0)

    def test_to_json_keys_sorted(self) -> None:
        store = Store()
        store.add("zebra", 1)
        store.add("apple", 2)
        store.add("mango", 3)
        expected = '{"apple": 2, "mango": 3, "zebra": 1}'
        self.assertEqual(store.to_json(), expected)

    def test_round_trip_exact(self) -> None:
        store = Store()
        store.add("charlie", 3)
        store.add("alpha", 1)
        store.add("bravo", 2)
        serialized = store.to_json()
        restored = Store.from_json(serialized)
        self.assertEqual(restored.to_json(), serialized)
        self.assertEqual(restored.quantity("alpha"), 1)
        self.assertEqual(restored.quantity("bravo"), 2)
        self.assertEqual(restored.quantity("charlie"), 3)

    def test_from_json_case_normalizing(self) -> None:
        raw = '{"Orange": 5, "pear": 2}'
        restored = Store.from_json(raw)
        self.assertEqual(restored.quantity("orange"), 5)
        self.assertEqual(restored.to_json(), '{"orange": 5, "pear": 2}')

    def test_from_json_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            Store.from_json("not valid json")
        with self.assertRaises(ValueError):
            Store.from_json("[1, 2, 3]")
        with self.assertRaises(ValueError):
            Store.from_json('{"item": -1}')
        with self.assertRaises(ValueError):
            Store.from_json('{"item": 0}')
        with self.assertRaises(ValueError):
            Store.from_json('{"item": "five"}')
        with self.assertRaises(ValueError):
            Store.from_json(123)  # type: ignore[arg-type]


class TestCli(unittest.TestCase):
    """Test CLI commands and requirements."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.temp_dir, "inventory.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_cli(self, argv: list) -> tuple:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        out = io.StringIO()
        err = io.StringIO()
        try:
            sys.stdout = out
            sys.stderr = err
            code = main(argv)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        return code, out.getvalue(), err.getvalue()

    def test_add_creates_file_if_missing(self) -> None:
        self.assertFalse(os.path.exists(self.file_path))
        code, out, err = self.run_cli(["add", "screws", "100", "--file", self.file_path])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(self.file_path))

        # Check content
        with open(self.file_path, "r", encoding="utf-8") as f:
            store = Store.from_json(f.read())
        self.assertEqual(store.quantity("screws"), 100)

    def test_add_accumulates_and_case_insensitive(self) -> None:
        self.run_cli(["--file", self.file_path, "add", "Nails", "50"])
        self.run_cli(["add", "nails", "25", "--file", self.file_path])
        with open(self.file_path, "r", encoding="utf-8") as f:
            store = Store.from_json(f.read())
        self.assertEqual(store.quantity("nails"), 75)

    def test_remove_success_and_delete_at_zero(self) -> None:
        self.run_cli(["--file", self.file_path, "add", "bolts", "20"])
        code, out, err = self.run_cli(["remove", "bolts", "5", "--file", self.file_path])
        self.assertEqual(code, 0)
        with open(self.file_path, "r", encoding="utf-8") as f:
            store = Store.from_json(f.read())
        self.assertEqual(store.quantity("bolts"), 15)

        # Remove remaining
        code, out, err = self.run_cli(["--file", self.file_path, "remove", "bolts", "15"])
        self.assertEqual(code, 0)
        with open(self.file_path, "r", encoding="utf-8") as f:
            store = Store.from_json(f.read())
        self.assertEqual(store.quantity("bolts"), 0)
        self.assertEqual(len(store), 0)

    def test_show_prints_sorted(self) -> None:
        self.run_cli(["--file", self.file_path, "add", "banana", "10"])
        self.run_cli(["--file", self.file_path, "add", "apple", "5"])
        self.run_cli(["--file", self.file_path, "add", "cherry", "20"])

        code, out, err = self.run_cli(["show", "--file", self.file_path])
        self.assertEqual(code, 0)
        expected = "apple: 5\nbanana: 10\ncherry: 20\n"
        self.assertEqual(out, expected)

    def test_show_creates_file_if_missing(self) -> None:
        self.assertFalse(os.path.exists(self.file_path))
        code, out, err = self.run_cli(["show", "--file", self.file_path])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertTrue(os.path.exists(self.file_path))
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), "{}")

    def test_file_arg_with_equals(self) -> None:
        code, out, err = self.run_cli([f"--file={self.file_path}", "add", "pencil", "3"])
        self.assertEqual(code, 0)
        code, out, err = self.run_cli(["show", f"--file={self.file_path}"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "pencil: 3\n")

    def test_unknown_command_returns_1(self) -> None:
        code, out, err = self.run_cli(["destroy", "all", "--file", self.file_path])
        self.assertEqual(code, 1)

        code, out, err = self.run_cli(["unknown"])
        self.assertEqual(code, 1)

        code, out, err = self.run_cli([])
        self.assertEqual(code, 1)

    def test_value_error_invalid_quantity_returns_2(self) -> None:
        code, out, err = self.run_cli(["add", "apple", "abc", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

        code, out, err = self.run_cli(["add", "apple", "-5", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

        code, out, err = self.run_cli(["add", "apple", "0", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

    def test_value_error_missing_item_returns_2(self) -> None:
        code, out, err = self.run_cli(["remove", "nonexistent", "1", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

    def test_value_error_remove_below_zero_returns_2(self) -> None:
        self.run_cli(["add", "pen", "5", "--file", self.file_path])
        code, out, err = self.run_cli(["remove", "pen", "10", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

    def test_value_error_missing_file_returns_2(self) -> None:
        code, out, err = self.run_cli(["add", "apple", "5"])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

    def test_value_error_missing_arguments_returns_2(self) -> None:
        code, out, err = self.run_cli(["add", "apple", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

        code, out, err = self.run_cli(["remove", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

        code, out, err = self.run_cli(["show", "extra", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))

    def test_value_error_corrupt_file_returns_2(self) -> None:
        with open(self.file_path, "w") as f:
            f.write("{invalid json")
        code, out, err = self.run_cli(["show", "--file", self.file_path])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: "))


if __name__ == "__main__":
    unittest.main()
