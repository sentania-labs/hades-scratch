"""Inventory store: item names mapped to integer quantities."""

import json


class Store:
    """Holds item names to integer quantities."""

    def __init__(self, data: dict[str, int] | None = None) -> None:
        if data is None:
            self._items: dict[str, int] = {}
        else:
            self._items = dict(data)

    # -- mutation -----------------------------------------------------------

    def add(self, name: str, qty: int) -> None:
        """Add *qty* units of *name*.

        Raises ``ValueError`` if *qty* is not a positive integer.
        """
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError(f"qty must be a positive integer, got {qty!r}")
        self._items[name.lower()] = self._items.get(name.lower(), 0) + qty

    def remove(self, name: str, qty: int) -> None:
        """Remove *qty* units of *name*.

        Raises ``ValueError`` if the item is missing or the removal would
        drive the quantity below zero.  An item that reaches exactly zero is
        deleted from the store.
        """
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError(f"qty must be a positive integer, got {qty!r}")
        key = name.lower()
        if key not in self._items:
            raise ValueError(f"item {name!r} not found in store")
        if self._items[key] < qty:
            raise ValueError(
                f"not enough of {name!r}: have {self._items[key]}, need {qty}"
            )
        self._items[key] -= qty
        if self._items[key] == 0:
            del self._items[key]

    # -- query --------------------------------------------------------------

    def quantity(self, name: str) -> int:
        """Return the quantity of *name*, or ``0`` if absent."""
        return self._items.get(name.lower(), 0)

    # -- serialisation ------------------------------------------------------

    def to_json(self) -> str:
        """Return a JSON string of the store (keys sorted)."""
        return json.dumps(
            dict(sorted(self._items.items())), sort_keys=True
        )

    @classmethod
    def from_json(cls, s: str) -> "Store":
        """Create a ``Store`` from a JSON string (keys sorted in the string)."""
        data = json.loads(s)
        return cls(data)
