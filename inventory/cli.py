"""CLI front-end for the inventory store."""

import argparse
import sys

from inventory.store import Store


class _ExitOnErrorParser(argparse.ArgumentParser):
    """Parser that raises SystemExit(2) on error instead of exiting."""

    def error(self, message):
        raise argparse.ArgumentError(None, message)


def main(argv=None):
    parser = _ExitOnErrorParser(prog="inventory")
    parser.add_argument("--file", required=True)
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add")
    add_p.add_argument("name")
    add_p.add_argument("qty")

    rm_p = sub.add_parser("remove")
    rm_p.add_argument("name")
    rm_p.add_argument("qty")

    sub.add_parser("show")

    try:
        args = parser.parse_args(argv)
    except Exception:
        print("error: unknown command", file=sys.stderr)
        return 1

    if args.command is None:
        print("error: no command given", file=sys.stderr)
        return 1

    store = _load(args.file)

    try:
        if args.command == "add":
            store.add(args.name, int(args.qty))
            _save(args.file, store)
        elif args.command == "remove":
            store.remove(args.name, int(args.qty))
            _save(args.file, store)
        elif args.command == "show":
            for name in sorted(store._data):
                print(f"{name}: {store._data[name]}")
        else:
            print(f"error: unknown command '{args.command}'", file=sys.stderr)
            return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


def _load(path):
    try:
        with open(path, "r") as f:
            return Store.from_json(f.read())
    except FileNotFoundError:
        return Store()


def _save(path, store):
    with open(path, "w") as f:
        f.write(store.to_json())
