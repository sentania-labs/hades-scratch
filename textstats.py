"""Minimal text statistics helpers."""


def count_words(text: str) -> int:
    """Return the number of words in *text*.

    A word is defined as a run of non-whitespace characters (equivalent
    to ``str.split()`` semantics).  Empty or whitespace-only input
    yields ``0``.
    """
    return len(text.split())
