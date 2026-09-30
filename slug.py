import re


def slugify(text: str, max_length: int | None = None) -> str:
    """Convert a string into a URL-friendly slug.

    - Lowercases the text.
    - Replaces any sequence of non-alphanumeric characters (excluding hyphens
      and underscores) with a single hyphen.
    - Strips leading/trailing hyphens.
    - Optionally truncates to *max_length* characters, cutting at the last
      hyphen so words are not split mid-way.
    """
    # Normalize: lowercase
    text = text.lower()

    # Replace any run of non-alphanumeric characters (except hyphens and
    # underscores which we treat as separators too) with a single hyphen.
    # We first convert underscores and hyphens to spaces so they are
    # treated the same way as any other separator, ensuring uniform
    # collapsing.
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Strip leading/trailing hyphens
    text = text.strip('-')

    if max_length is not None:
        if len(text) > max_length:
            text = text[:max_length]
            # Cut at the last hyphen so we don't break a word
            last_hyphen = text.rfind('-')
            if last_hyphen > 0:
                text = text[:last_hyphen]
            else:
                text = ''

    return text
