"""Inventory store: maps item names to integer quantities."""


class Store:
    """Holds item names (lowercase) to integer quantities."""

    def __init__(self, data=None):
        """Create a Store from an optional dict of {name: qty}."""
        self._items = {}
        if data:
            for name, qty in data.items():
                self._items[name.lower()] = qty

    # -- mutators ---------------------------------------------------------

    def add(self, name, qty):
        """Add *qty* units of *name* to the store.

        Raises ``ValueError`` if *qty* is not a positive integer.
        Names are stored lowercase.
        """
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError(f"qty must be a positive int, got {qty!r}")
        self._items[name.lower()] = self._items.get(name.lower(), 0) + qty

    def remove(self, name, qty):
        """Subtract *qty* units of *name* from the store.

        Raises ``ValueError`` if the item is missing or the removal
        would bring the quantity below zero.  When quantity reaches
        exactly zero the item is deleted.
        """
        key = name.lower()
        if key not in self._items:
            raise ValueError(f"item {name!r} is not in the store")
        if qty <= 0:
            raise ValueError(f"qty must be a positive int, got {qty!r}")
        if self._items[key] < qty:
            raise ValueError(
                f"cannot remove {qty}: only {self._items[key]} remaining"
            )
        new_qty = self._items[key] - qty
        if new_qty == 0:
            del self._items[key]
        else:
            self._items[key] = new_qty

    # -- query ------------------------------------------------------------

    def quantity(self, name):
        """Return the quantity for *name*, or 0 if absent."""
        return self._items.get(name.lower(), 0)

    # -- serialization ----------------------------------------------------

    def to_json(self):
        """Return a sorted JSON string of {name: qty}."""
        import json
        return json.dumps(dict(sorted(self._items.items())))

    @staticmethod
    def from_json(s):
        """Create a Store from a JSON string."""
        import json
        data = json.loads(s)
        return Store(data)
