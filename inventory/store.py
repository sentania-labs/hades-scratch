"""Inventory store: name -> integer quantity mapping."""

import json


class Store:
    """A case-insensitive inventory store.

    Names are stored in lowercase.  Quantities must be positive integers.
    Items that reach zero quantity are removed.
    """

    def __init__(self, data: dict[str, int] | None = None):
        self._items: dict[str, int] = {}
        if data is not None:
            for name, qty in data.items():
                self._items[name.lower()] = qty

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, name: str, qty: int) -> None:
        """Add *qty* units of *name*.

        Raises ``ValueError`` when *qty* is not a positive integer.
        """
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("qty must be a positive integer")
        key = name.lower()
        self._items[key] = self._items.get(key, 0) + qty

    def remove(self, name: str, qty: int) -> None:
        """Remove *qty* units of *name*.

        Raises ``ValueError`` when the item is absent or the removal would
        drive the quantity below zero.  When the quantity reaches zero the
        item is deleted from the store.
        """
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("qty must be a positive integer")
        key = name.lower()
        if key not in self._items:
            raise ValueError(f"item '{key}' not found")
        if self._items[key] < qty:
            raise ValueError(
                f"removing {qty} would drive '{key}' below zero"
            )
        self._items[key] -= qty
        if self._items[key] == 0:
            del self._items[key]

    def quantity(self, name: str) -> int:
        """Return the current quantity of *name*, or 0 when absent."""
        return self._items.get(name.lower(), 0)

    def to_json(self) -> str:
        """Serialise the store to a sorted JSON string."""
        return json.dumps(
            dict(sorted(self._items.items())), sort_keys=True
        )

    @classmethod
    def from_json(cls, s: str) -> "Store":
        """Deserialise a *Store* from a JSON string."""
        data = json.loads(s)
        return cls(data)
