"""Inventory store: name -> quantity mapping."""

import json


class Store:
    """Hold item names to integer quantities."""

    def __init__(self):
        self._data = {}  # type: dict[str, int]

    def add(self, name: str, qty: int):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("quantity must be a positive integer")
        self._data[name.lower()] = self._data.get(name.lower(), 0) + qty

    def remove(self, name: str, qty: int):
        key = name.lower()
        if key not in self._data:
            raise ValueError(f"item '{name}' not found")
        if self._data[key] < qty:
            raise ValueError(f"not enough '{name}' in stock")
        self._data[key] -= qty
        if self._data[key] == 0:
            del self._data[key]

    def quantity(self, name: str) -> int:
        return self._data.get(name.lower(), 0)

    def to_json(self) -> str:
        return json.dumps(
            {k: v for k, v in sorted(self._data.items())},
            sort_keys=True,
        )

    @staticmethod
    def from_json(s: str) -> "Store":
        store = Store()
        store._data = dict(json.loads(s))
        return store
