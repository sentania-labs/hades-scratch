import json


class Store:
    def __init__(self, data=None):
        if data is None:
            self._data = {}
        else:
            self._data = dict(data)

    def add(self, name, qty):
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"Quantity must be a positive integer, got {qty}")
        key = name.lower()
        self._data[key] = self._data.get(key, 0) + qty

    def remove(self, name, qty):
        key = name.lower()
        if key not in self._data:
            raise ValueError(f"Item '{key}' not found in store")
        if self._data[key] < qty:
            raise ValueError(f"Not enough of '{key}' in store: have {self._data[key]}, need {qty}")
        self._data[key] -= qty
        if self._data[key] == 0:
            del self._data[key]

    def quantity(self, name):
        return self._data.get(name.lower(), 0)

    def to_json(self):
        return json.dumps(dict(sorted(self._data.items())), indent=2)

    @staticmethod
    def from_json(s):
        data = json.loads(s)
        return Store(data)
