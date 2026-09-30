import re


def slugify(text: str, max_length: int | None = None) -> str:
    # Split on whitespace first
    words = text.split()
    # Split each word on non-alphanumeric characters (this keeps digits separate)
    result = []
    for w in words:
        parts = re.split(r'[^a-zA-Z0-9]+', w)
        for part in parts:
            if part:
                result.append(part.lower())
    # Join all with hyphens
    full = '-'.join(result)
    if max_length is not None:
        if len(full) > max_length:
            full = full[:max_length]
            if full and full[-1] != '-':
                cut = full.rfind('-')
                if cut != -1:
                    full = full[:cut]
                else:
                    full = ''
    return full
