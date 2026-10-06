import re


def slugify(text: str, max_length: int | None = None) -> str:
    """Convert a string to a URL-friendly slug."""
    # Lowercase
    text = text.lower()
    # Replace any non-alphanumeric character with a space
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    # Split into words and join with hyphens
    words = [w for w in text.split() if w]
    result = '-'.join(words)
    # Apply max_length: cut at the last hyphen before the limit
    if max_length is not None and len(result) > max_length:
        truncated = result[:max_length]
        # Find the last hyphen so we cut cleanly
        last_hyphen = truncated.rfind('-')
        if last_hyphen > 0:
            result = truncated[:last_hyphen]
        else:
            result = truncated
    return result
