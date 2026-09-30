"""CLI front-end for the inventory store."""

import argparse
import json
import os
import sys

from inventory.store import Store

_VALID_COMMANDS = frozenset(("add", "remove", "show"))


def _parse(argv):
    """Parse *argv* into (options_dict, command_or_None, sub_args).

    Returns (opts, cmd, args) where *opts* is a dict with at least
    'file', *cmd* is the subcommand string or *None*, and *args* are
    the remaining tokens after the command name.
    On parse failure returns (None, None, None).
    """
    opts = {}
    i = 0
    tokens = argv if argv else []

    while i < len(tokens):
        if tokens[i] == "--file":
            if i + 1 >= len(tokens):
                print("error: --file requires a value", file=sys.stderr)
                return None, None, None
            opts["file"] = tokens[i + 1]
            i += 2
            continue
        # Not an option – must be a subcommand or garbage
        break

    cmd = tokens[i] if i < len(tokens) else None
    sub = tokens[i + 1:] if cmd else []
    return opts, cmd, sub


def main(argv=None):
    """Parse *argv* and execute inventory commands.

    Returns an exit code (0 = success, 1 = unknown command, 2 = ValueError).
    """
    opts, cmd, sub_args = _parse(argv)

    if opts is None:
        return 2  # general parse error

    store_path = opts.get("file")
    if store_path is None:
        print("error: --file PATH is required", file=sys.stderr)
        return 2

    if cmd is None:
        print("error: no command provided", file=sys.stderr)
        return 1

    if cmd not in _VALID_COMMANDS:
        print(f"error: unknown command {cmd!r}", file=sys.stderr)
        return 1

    if cmd in ("add", "remove"):
        if len(sub_args) < 2:
            print(f"error: {cmd} requires NAME and QTY", file=sys.stderr)
            return 2
        name = sub_args[0]
        try:
            qty = int(sub_args[1])
        except ValueError:
            print(f"error: QTY must be an integer", file=sys.stderr)
            return 2

    # Load or create the store file.
    if os.path.exists(store_path):
        with open(store_path, "r") as f:
            store = Store.from_json(f.read())
    else:
        store = Store()

    if cmd == "add":
        try:
            store.add(name, qty)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    elif cmd == "remove":
        try:
            store.remove(name, qty)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    # "show" needs no args

    # Persist to disk.
    with open(store_path, "w") as f:
        f.write(store.to_json())

    # Print for the `show` command.
    if cmd == "show":
        for name in sorted(store._items):
            print(f"{name}: {store._items[name]}")

    return 0
