from dataclasses import dataclass


@dataclass(slots=True)
class Recommendation:
    title: str
    action: str
    priority: int = 1