import argparse
import json
import os
import sys

from inventory.store import Store


def main(argv=None):
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--file", required=True, help="Path to inventory JSON file")
    parser.add_argument("command", nargs="?", help="Command: add, remove, show")
    parser.add_argument("name", nargs="?", default=None, help="Item name")
    parser.add_argument("qty", nargs="?", default=None, help="Quantity")

    args = parser.parse_args(argv)

    store = _load(args.file)

    try:
        if args.command is None:
            print("error: no command specified", file=sys.stderr)
            return 1
        elif args.command == "add":
            _cmd_add(store, args.file, args.name, args.qty)
        elif args.command == "remove":
            _cmd_remove(store, args.file, args.name, args.qty)
        elif args.command == "show":
            _cmd_show(store)
        else:
            print(f"error: unknown command '{args.command}'", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    return 0


def _load(path):
    if not os.path.isfile(path):
        return Store({})
    with open(path, "r") as f:
        return Store.from_json(f.read())


def _save(store, path):
    with open(path, "w") as f:
        f.write(store.to_json())


def _cmd_add(store, path, name, qty):
    if name is None or qty is None:
        print("error: add requires NAME and QTY", file=sys.stderr)
        return 2
    store.add(name, int(qty))
    _save(store, path)


def _cmd_remove(store, path, name, qty):
    if name is None or qty is None:
        print("error: remove requires NAME and QTY", file=sys.stderr)
        return 2
    store.remove(name, int(qty))
    _save(store, path)


def _cmd_show(store):
    for name in sorted(store._data):
        print(f"{name}: {store._data[name]}")


if __name__ == "__main__":
    sys.exit(main())
