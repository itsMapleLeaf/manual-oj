import re


def to_snake_case(text: str):
    words = re.findall(r"[A-Z]?[a-z]+", text)
    return "_".join(words).lower()
