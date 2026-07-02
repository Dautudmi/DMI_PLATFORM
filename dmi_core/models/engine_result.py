from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class EngineResult:
    engine: str
    ticker: str
    score: float
    max_score: float
    confidence: float
    signals: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalized_score(self) -> float:
        if self.max_score == 0:
            return 0
        return round(self.score / self.max_score * 100, 2)

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "ticker": self.ticker,
            "score": self.score,
            "max_score": self.max_score,
            "normalized_score": self.normalized_score(),
            "confidence": self.confidence,
            "signals": self.signals,
            "risks": self.risks,
            "metadata": self.metadata,
        }