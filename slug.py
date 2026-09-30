import re


def slugify(text: str, max_length: int | None = None) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    slug = "-".join(words)
    if max_length is not None and len(slug) > max_length:
        if max_length <= 0:
            return ""
        truncated = slug[: max_length + 1]
        last_hyphen = truncated.rfind("-")
        if last_hyphen != -1:
            slug = slug[:last_hyphen]
        else:
            slug = slug[:max_length]
    return slug
