"""Comprehensive tests for the inventory store module."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from inventory.store import Store
from inventory.cli import main


# =====================================================================
# Store unit tests
# =====================================================================

class TestStoreAdd(unittest.TestCase):
    """Tests for Store.add()."""

    def test_add_positive_qty(self):
        store = Store()
        store.add("apple", 5)
        self.assertEqual(store.quantity("apple"), 5)

    def test_add_case_insensitive(self):
        store = Store()
        store.add("Apple", 3)
        self.assertEqual(store.quantity("apple"), 3)
        self.assertEqual(store.quantity("APPLE"), 3)

    def test_add_stored_lowercase(self):
        store = Store()
        store.add("Banana", 2)
        self.assertIn("banana", store._items)
        self.assertNotIn("Banana", store._items)

    def test_add_accumulates(self):
        store = Store()
        store.add("milk", 3)
        store.add("milk", 4)
        self.assertEqual(store.quantity("milk"), 7)

    def test_add_negative_qty_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("bread", -1)

    def test_add_zero_qty_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("bread", 0)

    def test_add_float_qty_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("bread", 1.5)

    def test_add_string_qty_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("bread", "two")

    def test_add_bool_qty_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("bread", True)


class TestStoreRemove(unittest.TestCase):
    """Tests for Store.remove()."""

    def test_remove_reduces_qty(self):
        store = Store({"apple": 5})
        store.remove("apple", 2)
        self.assertEqual(store.quantity("apple"), 3)

    def test_remove_item_not_found_raises(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.remove("apple", 1)

    def test_remove_exceeds_qty_raises(self):
        store = Store({"apple": 3})
        with self.assertRaises(ValueError):
            store.remove("apple", 5)

    def test_remove_to_zero_deletes(self):
        store = Store({"apple": 3})
        store.remove("apple", 3)
        self.assertEqual(store.quantity("apple"), 0)
        self.assertNotIn("apple", store._items)

    def test_remove_case_insensitive(self):
        store = Store({"apple": 3})
        store.remove("Apple", 3)
        self.assertNotIn("apple", store._items)

    def test_remove_negative_qty_raises(self):
        store = Store({"apple": 3})
        with self.assertRaises(ValueError):
            store.remove("apple", -1)

    def test_remove_zero_qty_raises(self):
        store = Store({"apple": 3})
        with self.assertRaises(ValueError):
            store.remove("apple", 0)

    def test_remove_bool_qty_raises(self):
        store = Store({"apple": 3})
        with self.assertRaises(ValueError):
            store.remove("apple", True)


class TestStoreQuantity(unittest.TestCase):
    """Tests for Store.quantity()."""

    def test_existing_item(self):
        store = Store({"apple": 4})
        self.assertEqual(store.quantity("apple"), 4)

    def test_absent_item_returns_zero(self):
        store = Store()
        self.assertEqual(store.quantity("milk"), 0)

    def test_quantity_case_insensitive(self):
        store = Store({"apple": 4})
        self.assertEqual(store.quantity("Apple"), 4)


class TestStoreJson(unittest.TestCase):
    """Tests for to_json / from_json round-tripping."""

    def test_empty_store_json(self):
        store = Store()
        self.assertEqual(store.to_json(), "{}")

    def test_json_round_trip(self):
        s1 = Store({"apple": 3, "banana": 5})
        json_str = s1.to_json()
        s2 = Store.from_json(json_str)
        self.assertEqual(s2.quantity("apple"), 3)
        self.assertEqual(s2.quantity("banana"), 5)

    def test_json_keys_sorted(self):
        store = Store({"zebra": 1, "apple": 2, "mango": 3})
        result = json.loads(store.to_json())
        keys = list(result.keys())
        self.assertEqual(keys, ["apple", "mango", "zebra"])

    def test_from_json_loads_lowercase(self):
        s = Store.from_json('{"Apple": 1, "BANANA": 2}')
        self.assertEqual(s.quantity("apple"), 1)
        self.assertEqual(s.quantity("banana"), 2)

    def test_from_json_empty(self):
        s = Store.from_json("{}")
        self.assertEqual(s.quantity("x"), 0)


class TestStoreInit(unittest.TestCase):
    """Tests for Store.__init__ with data parameter."""

    def test_init_with_data(self):
        store = Store({"apple": 3, "banana": 2})
        self.assertEqual(store.quantity("apple"), 3)
        self.assertEqual(store.quantity("banana"), 2)

    def test_init_converts_names_to_lower(self):
        store = Store({"Apple": 3})
        self.assertEqual(store.quantity("apple"), 3)
        self.assertNotIn("Apple", store._items)


# =====================================================================
# CLI tests
# =====================================================================

class TestCliMain(unittest.TestCase):
    """Tests for cli.main()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _path(self, name: str) -> str:
        return os.path.join(self.tmpdir, name)

    def test_add_command(self):
        path = self._path("inv.json")
        code = main(["--file", path, "add", "apple", "5"])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            data = json.loads(f.read())
        self.assertEqual(data["apple"], 5)

    def test_add_invalid_qty(self):
        path = self._path("inv2.json")
        with patch("sys.stderr", new_callable=lambda: open(os.devnull, "w")):
            code = main(["--file", path, "add", "apple", "-1"])
        self.assertEqual(code, 2)

    def test_remove_command(self):
        path = self._path("inv3.json")
        with open(path, "w") as f:
            f.write('{"apple": 5}')
        code = main(["--file", path, "remove", "apple", "2"])
        self.assertEqual(code, 0)
        with open(path) as f:
            data = json.loads(f.read())
        self.assertEqual(data["apple"], 3)

    def test_remove_missing_item(self):
        path = self._path("inv4.json")
        code = main(["--file", path, "remove", "apple", "1"])
        self.assertEqual(code, 2)

    def test_show_command(self):
        path = self._path("inv5.json")
        with open(path, "w") as f:
            f.write('{"zebra": 1, "apple": 2}')
        with patch("builtins.print") as mock_print:
            code = main(["--file", path, "show"])
        self.assertEqual(code, 0)
        calls = [c[0][0] for c in mock_print.call_args_list]
        self.assertEqual(calls, ["apple: 2", "zebra: 1"])

    def test_show_sorted(self):
        path = self._path("inv6.json")
        with open(path, "w") as f:
            f.write('{"milk": 3, "bread": 2, "apple": 1}')
        with patch("builtins.print") as mock_print:
            main(["--file", path, "show"])
        calls = [c[0][0] for c in mock_print.call_args_list]
        self.assertEqual(calls, ["apple: 1", "bread: 2", "milk: 3"])

    def test_no_command_returns_1(self):
        code = main(["--file", "dummy.json"])
        self.assertEqual(code, 1)

    def test_unknown_command_returns_1(self):
        code = main(["--file", "dummy.json", "delete"])
        self.assertEqual(code, 1)

    def test_file_created_if_missing(self):
        path = self._path("new_inv.json")
        self.assertFalse(os.path.exists(path))
        code = main(["--file", path, "add", "apple", "3"])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(path))


# =====================================================================
# Integration / end-to-end
# =====================================================================

class TestIntegration(unittest.TestCase):
    """End-to-end tests exercising Store + CLI together."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _path(self, name: str) -> str:
        return os.path.join(self.tmpdir, name)

    def test_add_and_show_round_trip(self):
        path = self._path("round.json")
        main(["--file", path, "add", "Apple", "5"])
        main(["--file", path, "add", "banana", "3"])
        with patch("builtins.print") as mock_print:
            main(["--file", path, "show"])
        calls = [c[0][0] for c in mock_print.call_args_list]
        self.assertEqual(calls, ["apple: 5", "banana: 3"])

    def test_remove_to_zero_deletes_from_file(self):
        path = self._path("delete.json")
        main(["--file", path, "add", "apple", "2"])
        main(["--file", path, "remove", "apple", "2"])
        with open(path) as f:
            data = json.loads(f.read())
        self.assertEqual(data, {})

    def test_store_to_json_from_json_consistency(self):
        s1 = Store()
        s1.add("Cherry", 10)
        s1.add("apple", 3)
        j = s1.to_json()
        s2 = Store.from_json(j)
        j2 = s2.to_json()
        self.assertEqual(j, j2)


if __name__ == "__main__":
    unittest.main()
