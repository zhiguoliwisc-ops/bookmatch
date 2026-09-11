from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.services.book_classifier_agent import (
    BookClassifierAgent,
)


class FakeBookClassifierAgent(BookClassifierAgent):
    def classify(
        self,
        book: EnrichedBook,
    ) -> BookClassification:
        return BookClassification(
            recommended_age_group=AgeGroup.ELEMENTARY,
            minimum_age=6,
            maximum_age=10,
            reading_difficulty=ReadingDifficulty.EASY,
            genre="Children's Fiction",
            confidence=0.9,
        )


def test_book_classifier_agent_is_abstract() -> None:
    assert BookClassifierAgent.__abstractmethods__ == {
        "classify"
    }


def test_book_classifier_agent_classifies_enriched_book() -> None:
    agent = FakeBookClassifierAgent()

    book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about Dog Man.",
        source="Test",
    )

    result = agent.classify(book)

    assert isinstance(result, BookClassification)