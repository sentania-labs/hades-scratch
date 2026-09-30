"""Command-line interface for the local inventory store."""

import sys

from inventory.store import Store


def _load(path):
    try:
        with open(path, encoding="utf-8") as inventory_file:
            return Store.from_json(inventory_file.read())
    except FileNotFoundError:
        return Store()


def _save(path, store):
    with open(path, "w", encoding="utf-8") as inventory_file:
        inventory_file.write(store.to_json())


def _parse_quantity(value):
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError("quantity must be a positive integer") from exc


def main(argv):
    """Run an inventory command and return its process-style exit code."""
    if len(argv) < 3 or argv[0] != "--file":
        return 1

    path = argv[1]
    command = argv[2]
    arguments = argv[3:]
    if command not in {"add", "remove", "show"}:
        return 1

    try:
        store = _load(path)
        if command == "show":
            if arguments:
                return 1
            for name in sorted(store._items):
                print(f"{name}: {store.quantity(name)}")
            _save(path, store)
            return 0

        if len(arguments) != 2:
            return 1
        name, quantity_text = arguments
        quantity = _parse_quantity(quantity_text)
        if command == "add":
            store.add(name, quantity)
        else:
            store.remove(name, quantity)
        _save(path, store)
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
