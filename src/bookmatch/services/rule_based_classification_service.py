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
                minimum_age=3,
                maximum_age=5,
                reading_difficulty=ReadingDifficulty.VERY_EASY,
                genre="Children's Fiction",
                confidence=0.9,
            )

        if "early reader" in description:
            return BookClassification(
                recommended_age_group=AgeGroup.EARLY_ELEMENTARY,
                minimum_age=5,
                maximum_age=7,
                reading_difficulty=ReadingDifficulty.EASY,
                genre="Children's Fiction",
                confidence=0.9,
            )

        if "young adult" in description:
            return BookClassification(
                recommended_age_group=AgeGroup.HIGH_SCHOOL,
                minimum_age=14,
                maximum_age=18,
                reading_difficulty=ReadingDifficulty.CHALLENGING,
                genre="Young Adult Fiction",
                confidence=0.9,
            )

        raise InsufficientBookInformationError(
            "The available book information is insufficient for classification."
        )