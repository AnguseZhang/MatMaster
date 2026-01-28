from typing import List

from google.genai.types import Content


def is_content_has_keywords(content: Content, keywords: List[str]) -> bool:
    tokens = [f'[{k}]' if k.endswith('agent') else f'`{k}`' for k in keywords]

    return any(
        isinstance((text := getattr(part, 'text', None)), str)
        and any(token in text for token in tokens)
        for part in content.parts
    )
