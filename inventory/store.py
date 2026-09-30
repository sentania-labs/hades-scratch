import json


class Store:
    """Simple inventory store mapping item names (lowercase) to integer quantities."""

    def __init__(self):
        self._items = {}

    def add(self, name, qty):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError(f"quantity must be a positive int, got {qty}")
        key = name.lower()
        self._items[key] = self._items.get(key, 0) + qty

    def remove(self, name, qty):
        key = name.lower()
        if key not in self._items:
            raise ValueError(f"item '{key}' not found")
        if self._items[key] < qty:
            raise ValueError(
                f"cannot remove {qty} of '{key}': only {self._items[key]} in stock"
            )
        self._items[key] -= qty
        if self._items[key] == 0:
            del self._items[key]

    def quantity(self, name):
        return self._items.get(name.lower(), 0)

    def to_json(self):
        return json.dumps(dict(sorted(self._items.items())))

    @staticmethod
    def from_json(s):
        store = Store()
        data = json.loads(s)
        for name, qty in data.items():
            store._items[name] = qty
        return store
