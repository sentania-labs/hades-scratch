"""Inventory store module."""

import json
from typing import Dict, List, Optional, Tuple


class Store:
    """Holds item names to integer quantities."""

    def __init__(self, items: Optional[Dict[str, int]] = None) -> None:
        self._items: Dict[str, int] = {}
        if items is not None:
            if not isinstance(items, dict):
                raise ValueError("Initial items must be a dictionary")
            for k, v in items.items():
                self.add(k, v)

    def add(self, name: str, qty: int) -> None:
        """Add quantity to an item.

        qty must be a positive int, else ValueError.
        Names are case-insensitive and stored lowercase.
        """
        if not isinstance(name, str):
            raise ValueError("Item name must be a string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")

        key = name.lower()
        self._items[key] = self._items.get(key, 0) + qty

    def remove(self, name: str, qty: int) -> None:
        """Remove quantity from an item.

        ValueError if the item is missing or would go below zero.
        An item that reaches zero is deleted.
        """
        if not isinstance(name, str):
            raise ValueError("Item name must be a string")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")

        key = name.lower()
        if key not in self._items:
            raise ValueError(f"Item '{name}' not found in inventory")

        current = self._items[key]
        if current < qty:
            raise ValueError(
                f"Cannot remove {qty} of '{name}'; only {current} available"
            )

        new_qty = current - qty
        if new_qty == 0:
            del self._items[key]
        else:
            self._items[key] = new_qty

    def quantity(self, name: str) -> int:
        """Return the quantity of name, or 0 if absent."""
        if not isinstance(name, str):
            return 0
        return self._items.get(name.lower(), 0)

    def to_json(self) -> str:
        """Serialize store to a JSON string.

        JSON object of name to quantity, keys sorted.
        """
        return json.dumps(self._items, sort_keys=True)

    @classmethod
    def from_json(cls, s: str) -> "Store":
        """Deserialize store from JSON string.

        Must round-trip exactly with to_json().
        """
        if not isinstance(s, str):
            raise ValueError("JSON input must be a string")
        try:
            data = json.loads(s)
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("JSON data must be an object")

        store = cls()
        for k, v in data.items():
            store.add(k, v)
        return store

    def items(self) -> List[Tuple[str, int]]:
        """Return list of (name, quantity) sorted by name."""
        return sorted(self._items.items())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, name: str) -> bool:
        if not isinstance(name, str):
            return False
        return name.lower() in self._items

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Store):
            return False
        return self._items == other._items

    def __repr__(self) -> str:
        return f"Store({self._items!r})"
