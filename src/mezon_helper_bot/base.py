"""Core types shared by every bot."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Post:
    """What a bot wants to say: text plus an optional local image."""

    text: str
    image: Path | None = None


# A bot is just a function that builds today's post.
Bot = Callable[[], Post]
