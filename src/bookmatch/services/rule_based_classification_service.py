from bookmatch.models.book import BookInput
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.services.classification_service import ClassificationService
from bookmatch.services.exceptions import InsufficientBookInformationError


class RuleBasedClassificationService(ClassificationService):
    """Simple rule-based baseline for book classification."""

    def classify(self, book: BookInput) -> BookClassification:
        if not book.description:
            raise InsufficientBookInformationError(
                "A book description is required for rule-based classification."
            )

        description = book.description.lower()

        if "picture book" in description:
            return BookClassification(
                recommended_age_group=AgeGroup.PRESCHOOL,
                reading_difficulty=ReadingDifficulty.VERY_EASY,
                confidence=0.9,
            )

        if "early reader" in description:
            return BookClassification(
                recommended_age_group=AgeGroup.EARLY_ELEMENTARY,
                reading_difficulty=ReadingDifficulty.EASY,
                confidence=0.9,
            )

        if "young adult" in description:
            return BookClassification(
                recommended_age_group=AgeGroup.HIGH_SCHOOL,
                reading_difficulty=ReadingDifficulty.CHALLENGING,
                confidence=0.9,
            )

        raise InsufficientBookInformationError(
            "The available book information is insufficient for classification."
        )