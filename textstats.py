def count_words(text: str) -> int:
    """Return the number of words in *text*.

    A word is a run of non-whitespace characters.
    Returns 0 for empty or whitespace-only strings.
    """
    if not text or not text.strip():
        return 0
    return len(text.split())
