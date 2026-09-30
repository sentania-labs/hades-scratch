import argparse
import json
import sys

from inventory.store import Store


def main(argv):
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--file", required=True, help="Path to the JSON inventory file")
    parser.add_argument("command", nargs="?", default=None, help="Command: add, remove, show")
    parser.add_argument("name", nargs="?", default=None, help="Item name")
    parser.add_argument("qty", nargs="?", default=None, help="Quantity")

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code != 0 else 0

    command = args.command
    if command is None:
        return 1

    # Load or create store
    store_path = args.file
    if store_path is not None:
        try:
            with open(store_path, "r") as f:
                store = Store.from_json(f.read())
        except FileNotFoundError:
            store = Store()
        except json.JSONDecodeError:
            store = Store()
    else:
        store = Store()

    if command == "add":
        if args.name is None or args.qty is None:
            print("error: add requires NAME and QTY", file=sys.stderr)
            return 2
        try:
            qty = int(args.qty)
        except ValueError:
            print(f"error: invalid quantity '{args.qty}'", file=sys.stderr)
            return 2
        try:
            store.add(args.name, qty)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        _save(store, store_path)
        return 0

    elif command == "remove":
        if args.name is None or args.qty is None:
            print("error: remove requires NAME and QTY", file=sys.stderr)
            return 2
        try:
            qty = int(args.qty)
        except ValueError:
            print(f"error: invalid quantity '{args.qty}'", file=sys.stderr)
            return 2
        try:
            store.remove(args.name, qty)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        _save(store, store_path)
        return 0

    elif command == "show":
        lines = []
        for name in sorted(store._items):
            lines.append(f"{name}: {store._items[name]}")
        print("\n".join(lines))
        return 0

    else:
        return 1


def _save(store, path):
    if path is None:
        return
    with open(path, "w") as f:
        f.write(store.to_json())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
