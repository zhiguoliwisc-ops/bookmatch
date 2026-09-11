from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.models.classification_review import (
    ClassificationReview,
    ReviewDecision,
)
from bookmatch.services.book_reviewer_agent import (
    BookReviewerAgent,
)


class FakeBookReviewerAgent(BookReviewerAgent):
    def review(
        self,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        return ClassificationReview(
            decision=ReviewDecision.APPROVED,
            confidence=0.95,
            reason="The classification is consistent with the book evidence.",
        )


def test_book_reviewer_agent_is_abstract() -> None:
    assert BookReviewerAgent.__abstractmethods__ == {
        "review"
    }


def test_book_reviewer_agent_reviews_classification() -> None:
    agent = FakeBookReviewerAgent()

    book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about Dog Man.",
        source="Test",
    )

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Graphic Novel",
        confidence=0.9,
    )

    result = agent.review(book, classification)

    assert isinstance(result, ClassificationReview)
    assert result.decision == ReviewDecision.APPROVED