"""CLI entry point for the inventory tool."""

import argparse
import json
import sys
from pathlib import Path

from inventory.store import Store


def main(argv: list[str] | None = None) -> int:
    """CLI handler.  Returns an exit code.

    Commands
    --------
    add NAME QTY
    remove NAME QTY
    show

    Options
    -------
    --file PATH      JSON file to persist the store (created if missing).
    """
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--file", required=True, help="JSON file for the store")
    parser.add_argument("command", nargs="?", default=None, help="add|remove|show")
    parser.add_argument("name", nargs="?", default=None, help="item name")
    parser.add_argument("qty", nargs="?", default=None, help="quantity")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse calls sys.exit on errors; map to our codes.
        code = exc.code if isinstance(exc.code, int) else 2
        return code

    path = Path(args.file)
    store = Store()
    if path.exists() and path.stat().st_size > 0:
        store = Store.from_json(path.read_text())

    if args.command is None:
        print("error: command is required (add|remove|show)", file=sys.stderr)
        return 1

    try:
        if args.command == "add":
            if args.name is None or args.qty is None:
                print("error: add requires NAME and QTY", file=sys.stderr)
                return 1
            store.add(args.name, int(args.qty))

        elif args.command == "remove":
            if args.name is None or args.qty is None:
                print("error: remove requires NAME and QTY", file=sys.stderr)
                return 1
            store.remove(args.name, int(args.qty))

        elif args.command == "show":
            for name in sorted(store._items):
                print(f"{name}: {store._items[name]}")
            return 0

        else:
            print(f"error: unknown command {args.command!r}", file=sys.stderr)
            return 1

    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Write back
    path.write_text(store.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
