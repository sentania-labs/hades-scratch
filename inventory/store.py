"""Inventory storage and JSON serialization."""

import json


class Store:
    """A case-insensitive mapping of item names to positive quantities."""

    def __init__(self):
        self._items = {}

    @staticmethod
    def _name(name):
        return name.lower()

    @staticmethod
    def _validate_quantity(qty):
        if type(qty) is not int or qty <= 0:
            raise ValueError("quantity must be a positive integer")

    def add(self, name, qty):
        """Add a positive quantity of an item."""
        self._validate_quantity(qty)
        key = self._name(name)
        self._items[key] = self._items.get(key, 0) + qty

    def remove(self, name, qty):
        """Remove a positive quantity, deleting items that reach zero."""
        self._validate_quantity(qty)
        key = self._name(name)
        current = self._items.get(key)
        if current is None:
            raise ValueError("item is not in inventory")
        if qty > current:
            raise ValueError("quantity would go below zero")
        if qty == current:
            del self._items[key]
        else:
            self._items[key] = current - qty

    def quantity(self, name):
        """Return an item's quantity, or zero when it is absent."""
        return self._items.get(self._name(name), 0)

    def to_json(self):
        """Serialize the inventory as a deterministically ordered JSON object."""
        return json.dumps(self._items, sort_keys=True)

    @classmethod
    def from_json(cls, text):
        """Construct a store from its JSON object representation."""
        try:
            items = json.loads(text)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid inventory JSON") from exc
        if not isinstance(items, dict):
            raise ValueError("inventory JSON must be an object")

        store = cls()
        for name, qty in items.items():
            if not isinstance(name, str):
                raise ValueError("inventory item name must be a string")
            store.add(name, qty)
        return store
