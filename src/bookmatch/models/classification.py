from enum import Enum

from pydantic import BaseModel, Field


class AgeGroup(str, Enum):
    PRESCHOOL = "Preschool"
    EARLY_ELEMENTARY = "Early Elementary"
    ELEMENTARY = "Elementary"
    MIDDLE_SCHOOL = "Middle School"
    HIGH_SCHOOL = "High School"
    ADULT = "Adult"


class ReadingDifficulty(int, Enum):
    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    CHALLENGING = 4
    ADVANCED = 5


class BookClassification(BaseModel):
    """Classification result for a book."""

    recommended_age_group: AgeGroup
    reading_difficulty: ReadingDifficulty

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        exclude=True,
        description="Internal confidence score.",
    )