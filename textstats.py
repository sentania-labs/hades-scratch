"""Text statistics helpers."""


def count_words(text: str) -> int:
    """Return the number of words in *text*.

    Words are runs of non-whitespace characters.
    Empty or whitespace-only text returns 0.
    """
    return len(text.split())
