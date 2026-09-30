"""Tests for the inventory package."""

import json
import os
import tempfile
import unittest

from inventory.cli import main
from inventory.store import Store


class TestStoreAdd(unittest.TestCase):
    """Tests for Store.add()."""

    def setUp(self) -> None:
        self.store = Store()

    def test_add_positive(self) -> None:
        self.store.add("apple", 5)
        self.assertEqual(self.store.quantity("apple"), 5)

    def test_add_case_insensitive(self) -> None:
        self.store.add("Apple", 3)
        self.assertEqual(self.store.quantity("apple"), 3)
        self.assertEqual(self.store.quantity("APPLE"), 3)

    def test_add_existing_item(self) -> None:
        self.store.add("banana", 2)
        self.store.add("banana", 3)
        self.assertEqual(self.store.quantity("banana"), 5)

    def test_add_non_positive_qty_zero(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("pear", 0)

    def test_add_non_positive_qty_negative(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("pear", -1)

    def test_add_bool_qty_rejected(self) -> None:
        # bool is a subclass of int; should be rejected.
        with self.assertRaises(ValueError):
            self.store.add("pear", True)

    def test_add_non_int_qty(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("pear", 2.5)

        with self.assertRaises(ValueError):
            self.store.add("pear", "3")


class TestStoreRemove(unittest.TestCase):
    """Tests for Store.remove()."""

    def setUp(self) -> None:
        self.store = Store()
        self.store.add("apple", 10)

    def test_remove_exact(self) -> None:
        self.store.remove("apple", 10)
        self.assertEqual(self.store.quantity("apple"), 0)

    def test_remove_partial(self) -> None:
        self.store.remove("apple", 3)
        self.assertEqual(self.store.quantity("apple"), 7)

    def test_remove_leaves_zero(self) -> None:
        """An item that reaches zero is deleted."""
        self.store.remove("apple", 10)
        self.assertNotIn("apple", self.store._items)

    def test_remove_nonexistent(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("banana", 1)

    def test_remove_too_much(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("apple", 11)

    def test_remove_non_positive(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("apple", 0)

        with self.assertRaises(ValueError):
            self.store.remove("apple", -5)

    def test_remove_bool_qty(self) -> None:
        with self.assertRaises(ValueError):
            self.store.remove("apple", True)


class TestStoreQuantity(unittest.TestCase):
    """Tests for Store.quantity()."""

    def setUp(self) -> None:
        self.store = Store()

    def test_existing(self) -> None:
        self.store.add("cherry", 4)
        self.assertEqual(self.store.quantity("cherry"), 4)

    def test_absent_returns_zero(self) -> None:
        self.assertEqual(self.store.quantity("nope"), 0)

    def test_case_insensitive(self) -> None:
        self.store.add("Cherry", 4)
        self.assertEqual(self.store.quantity("cherry"), 4)
        self.assertEqual(self.store.quantity("CHERRY"), 4)


class TestStoreSerialization(unittest.TestCase):
    """Tests for Store.to_json() and Store.from_json()."""

    def test_roundtrip_empty(self) -> None:
        s = Store()
        j = s.to_json()
        s2 = Store.from_json(j)
        self.assertEqual(s2.to_json(), j)

    def test_roundtrip_single(self) -> None:
        s = Store()
        s.add("apple", 5)
        j = s.to_json()
        s2 = Store.from_json(j)
        self.assertEqual(s2.to_json(), j)

    def test_roundtrip_multiple(self) -> None:
        s = Store()
        s.add("banana", 3)
        s.add("apple", 7)
        s.add("cherry", 1)
        j = s.to_json()
        data = json.loads(j)
        # Keys should be sorted
        self.assertEqual(list(data.keys()), ["apple", "banana", "cherry"])
        s2 = Store.from_json(j)
        self.assertEqual(s2.to_json(), j)

    def test_roundtrip_with_removal(self) -> None:
        s = Store()
        s.add("apple", 2)
        s.remove("apple", 2)  # item should be gone
        j = s.to_json()
        s2 = Store.from_json(j)
        self.assertEqual(s2.to_json(), j)
        self.assertEqual(s2.quantity("apple"), 0)

    def test_json_is_valid_object(self) -> None:
        s = Store()
        s.add("x", 1)
        j = s.to_json()
        data = json.loads(j)
        self.assertIsInstance(data, dict)
        self.assertEqual(data, {"x": 1})


class TestCli(unittest.TestCase):
    """Tests for inventory.cli.main()."""

    def _tempfile(self, content: str = "") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        if content:
            with open(path, "w") as f:
                f.write(content)
        return path

    def test_show_empty(self) -> None:
        path = self._tempfile()
        rc = main(["--file", path, "show"])
        self.assertEqual(rc, 0)
        os.unlink(path)

    def test_add_and_show(self) -> None:
        path = self._tempfile()
        rc = main(["--file", path, "add", "apple", "5"])
        self.assertEqual(rc, 0)
        rc = main(["--file", path, "show"])
        self.assertEqual(rc, 0)
        os.unlink(path)

    def test_remove_and_show(self) -> None:
        path = self._tempfile()
        main(["--file", path, "add", "apple", "5"])
        rc = main(["--file", path, "remove", "apple", "3"])
        self.assertEqual(rc, 0)
        os.unlink(path)

    def test_remove_to_zero_deletes(self) -> None:
        path = self._tempfile()
        main(["--file", path, "add", "apple", "2"])
        main(["--file", path, "remove", "apple", "2"])
        rc = main(["--file", path, "show"])
        self.assertEqual(rc, 0)
        os.unlink(path)

    def test_add_value_error(self) -> None:
        path = self._tempfile()
        rc = main(["--file", path, "add", "apple", "0"])
        self.assertEqual(rc, 2)
        os.unlink(path)

    def test_remove_value_error(self) -> None:
        path = self._tempfile()
        rc = main(["--file", path, "remove", "nonexistent", "1"])
        self.assertEqual(rc, 2)
        os.unlink(path)

    def test_unknown_command(self) -> None:
        path = self._tempfile()
        rc = main(["--file", path, "foobar"])
        self.assertEqual(rc, 1)
        os.unlink(path)

    def test_file_created_if_missing(self) -> None:
        path = self._tempfile()
        os.unlink(path)  # remove it
        rc = main(["--file", path, "add", "apple", "3"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(data, {"apple": 3})
        os.unlink(path)

    def test_show_sorted(self) -> None:
        path = self._tempfile()
        main(["--file", path, "add", "cherry", "1"])
        main(["--file", path, "add", "apple", "2"])
        main(["--file", path, "add", "banana", "3"])
        rc = main(["--file", path, "show"])
        self.assertEqual(rc, 0)
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
