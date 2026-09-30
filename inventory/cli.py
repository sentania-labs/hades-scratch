"""CLI front-end for the inventory store."""

import argparse
import json
import sys
from pathlib import Path

from inventory.store import Store


def main(argv: list[str] | None = None) -> int:
    """Entry point for the inventory CLI.

    Returns an exit code:  0 on success, 1 on unknown command,
    2 on ValueError (with an *error: \<message\>* line on stderr).
    """
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--file", required=True, help="Path to JSON store")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add")
    add_p.add_argument("name")
    add_p.add_argument("qty", type=int)

    rm_p = sub.add_parser("remove")
    rm_p.add_argument("name")
    rm_p.add_argument("qty", type=int)

    sub.add_parser("show")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("error: unknown or invalid command", file=sys.stderr)
        return 1

    if args.command is None:
        print("error: no command given", file=sys.stderr)
        return 1

    store_path = Path(args.file)
    if store_path.exists():
        data = json.loads(store_path.read_text())
        store = Store(data)
    else:
        store = Store()

    try:
        if args.command == "add":
            store.add(args.name, args.qty)
        elif args.command == "remove":
            store.remove(args.name, args.qty)
        elif args.command == "show":
            for name in sorted(store._items):
                print(f"{name}: {store._items[name]}")
            return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Persist
    store_path.write_text(store.to_json() + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
