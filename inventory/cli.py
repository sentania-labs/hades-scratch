"""Inventory command-line interface."""

import os
import sys
from typing import List, Optional, Tuple

from inventory.store import Store


def parse_args(argv: List[str]) -> Tuple[Optional[str], List[str], Optional[str]]:
    """Parse command line arguments.

    Returns (file_path, positional_args, option_error).
    """
    file_path: Optional[str] = None
    positional: List[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--file":
            i += 1
            if i >= len(argv):
                raise ValueError("Option --file requires a PATH argument")
            file_path = argv[i]
        elif arg.startswith("--file="):
            file_path = arg[len("--file="):]
            if not file_path:
                raise ValueError("Option --file requires a PATH argument")
        elif arg.startswith("-") and not (len(arg) > 1 and arg[1:].isdigit()):
            return None, [], f"Unknown option: {arg}"
        else:
            positional.append(arg)
        i += 1
    return file_path, positional, None


def load_store(file_path: str) -> Store:
    """Load store from JSON file, returning an empty store if the file is missing."""
    if not os.path.exists(file_path):
        return Store()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise ValueError(f"Failed to read file '{file_path}': {e}") from e

    if not content.strip():
        return Store()
    return Store.from_json(content)


def save_store(store: Store, file_path: str) -> None:
    """Save store to JSON file."""
    try:
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(store.to_json())
    except OSError as e:
        raise ValueError(f"Failed to write file '{file_path}': {e}") from e


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint.

    Returns exit code (0 for success, 1 for unknown command, 2 for ValueError).
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        file_path, positional, opt_error = parse_args(argv)
    except ValueError as e:
        sys.stderr.write(f"error: {e}\n")
        return 2

    if opt_error is not None:
        sys.stderr.write(f"error: {opt_error}\n")
        return 1

    if not positional:
        sys.stderr.write("error: No command specified\n")
        return 1

    cmd = positional[0]
    if cmd not in ("add", "remove", "show"):
        sys.stderr.write(f"error: Unknown command '{cmd}'\n")
        return 1

    if file_path is None:
        sys.stderr.write("error: Option --file PATH is required\n")
        return 2

    try:
        if cmd == "add":
            if len(positional) != 3:
                raise ValueError("Usage: add NAME QTY")
            name = positional[1]
            try:
                qty = int(positional[2])
            except ValueError:
                raise ValueError(f"Quantity must be an integer, got '{positional[2]}'")
            store = load_store(file_path)
            store.add(name, qty)
            save_store(store, file_path)
            return 0

        elif cmd == "remove":
            if len(positional) != 3:
                raise ValueError("Usage: remove NAME QTY")
            name = positional[1]
            try:
                qty = int(positional[2])
            except ValueError:
                raise ValueError(f"Quantity must be an integer, got '{positional[2]}'")
            store = load_store(file_path)
            store.remove(name, qty)
            save_store(store, file_path)
            return 0

        elif cmd == "show":
            if len(positional) != 1:
                raise ValueError("Usage: show")
            store = load_store(file_path)
            if not os.path.exists(file_path):
                save_store(store, file_path)
            for name, qty in store.items():
                print(f"{name}: {qty}")
            return 0

    except ValueError as e:
        sys.stderr.write(f"error: {e}\n")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
