import re
import string


def slugify(text: str, max_length: int | None = None) -> str:
    """Convert a string to a URL-friendly slug."""
    # Lowercase and split into words (alphanumeric sequences)
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    # Join with hyphens
    slug = '-'.join(words)
    # If max_length is set, truncate at a hyphen boundary
    if max_length is not None:
        if len(slug) > max_length:
            slug = slug[:max_length]
            # Cut back to the last hyphen to avoid partial words
            if not slug.endswith('-') and '-' in slug:
                slug = slug[:slug.rfind('-')]
            # If the truncated string still exceeds or ends with hyphen, strip
            slug = slug.rstrip('-')
    return slug
