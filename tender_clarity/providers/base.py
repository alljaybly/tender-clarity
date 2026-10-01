"""Provider-independent base contract marker."""

from typing import Protocol


class Provider(Protocol):
    def analyze(self, page_text: str) -> dict: ...
