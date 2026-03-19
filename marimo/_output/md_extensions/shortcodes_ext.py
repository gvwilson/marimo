# Copyright 2026 Marimo. All rights reserved.
from __future__ import annotations

from typing import Callable

import markdown  # type: ignore
import markdown.preprocessors  # type: ignore
import shortcodes  # type: ignore

# Module-level parser singleton -- lives for the lifetime of the process.
# Users register handlers on this object via mo.register_shortcode().
_parser = shortcodes.Parser()


class ShortcodesPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)
        text = _parser.parse(text)
        return text.split("\n")


class ShortcodesExtension(markdown.Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        # Priority 40 -- runs before PyconDetector (30) and DisplayMath (24),
        # so shortcode output is visible to all later processors.
        md.preprocessors.register(ShortcodesPreprocessor(md), "shortcodes", 40)


def register_shortcode(tag: str) -> Callable[..., Callable[..., str]]:
    """Decorator: register a shortcode handler for use in mo.md().

    The decorated function receives three arguments:
    - pargs: list of positional arguments from the shortcode tag
    - kwargs: dict of keyword arguments from the shortcode tag
    - context: arbitrary context object (None by default)

    It must return a string of HTML or markdown text to be inserted in place
    of the shortcode tag before markdown processing.

    Example::

        @mo.register_shortcode("alert")
        def alert(pargs, kwargs, context):
            level = kwargs.get("level", "info")
            body = pargs[0] if pargs else ""
            return f'<div class="alert alert-{level}">{body}</div>'

    Then in a notebook cell::

        mo.md("[% alert 'This is important!' level=warning %]")
    """

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        _parser.register(func, tag)
        return func

    return decorator
