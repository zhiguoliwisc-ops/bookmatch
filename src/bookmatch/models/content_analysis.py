from dataclasses import dataclass


@dataclass
class BookContentAnalysis:
    themes: list[str]
    subject_maturity: int
    emotional_complexity: int
    conceptual_complexity: int
    sensitive_topics: list[str]
    summary: str