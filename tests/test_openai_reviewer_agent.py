from unittest.mock import Mock
import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.models.classification_review import (
    ClassificationReview,
    ReviewDecision,
)
from bookmatch.services.openai_reviewer_agent import (
    OpenAIReviewerAgent,
)


def test_openai_reviewer_agent_returns_review() -> None:
    original_input = BookInput(
        title="Dog Man",
    )

    book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about a dog-headed police officer.",
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

    parsed_review = ClassificationReview(
        decision=ReviewDecision.APPROVED,
        confidence=0.95,
        reason="The classification is consistent with the book evidence.",
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                parsed=parsed_review,
            )
        )
    ]

    mock_client = Mock()
    mock_client.chat.completions.parse.return_value = mock_response

    agent = OpenAIReviewerAgent(client=mock_client)

    result = agent.review(
        original_input,
        book,
        classification,
    )

    assert isinstance(result, ClassificationReview)
    assert result.decision == ReviewDecision.APPROVED
    assert result.confidence == 0.95


def test_openai_reviewer_agent_raises_when_parsed_review_is_none() -> None:
    original_input = BookInput(
        title="Dog Man",
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                parsed=None,
            )
        )
    ]

    mock_client = Mock()
    mock_client.chat.completions.parse.return_value = mock_response

    agent = OpenAIReviewerAgent(client=mock_client)

    book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about a dog-headed police officer.",
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

    with pytest.raises(ValueError, match="valid classification review"):
        agent.review(
            original_input,
            book,
            classification,
        )


def test_openai_reviewer_agent_sends_book_and_classification_to_openai() -> None:
    original_input = BookInput(
        title="Dog Man",
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                parsed=ClassificationReview(
                    decision=ReviewDecision.APPROVED,
                    confidence=0.95,
                    reason="The classification is consistent with the book evidence.",
                )
            )
        )
    ]

    mock_client = Mock()
    mock_client.chat.completions.parse.return_value = mock_response

    agent = OpenAIReviewerAgent(client=mock_client)

    book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about a dog-headed police officer.",
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

    agent.review(
        original_input,
        book,
        classification,
    )

    mock_client.chat.completions.parse.assert_called_once()

    call_kwargs = mock_client.chat.completions.parse.call_args.kwargs

    user_message = call_kwargs["messages"][1]["content"]

    assert "Dog Man" in user_message
    assert "Dav Pilkey" in user_message
    assert "Elementary" in user_message
    assert "6–10" in user_message
    assert "Graphic Novel" in user_message

    assert "Original user input:" in user_message
    assert "Selected book:" in user_message

    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["response_format"] is ClassificationReview


def test_openai_reviewer_agent_returns_needs_revision() -> None:
    original_input = BookInput(
        title="Charlotte's Web",
    )

    parsed_review = ClassificationReview(
        decision=ReviewDecision.NEEDS_REVISION,
        confidence=0.80,
        reason="The proposed genre is not well supported by the available evidence.",
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                parsed=parsed_review,
            )
        )
    ]

    mock_client = Mock()
    mock_client.chat.completions.parse.return_value = mock_response

    agent = OpenAIReviewerAgent(client=mock_client)

    book = EnrichedBook(
        title="A Literature Kit For Charlottes Web By Eb White",
        author="Brenda Rollins",
        publication_date="2008",
        isbn=None,
        description="An educational resource for teaching Charlotte's Web.",
        source="Test",
    )

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Literary Analysis",
        confidence=0.9,
    )

    result = agent.review(
        original_input,
        book,
        classification,
    )

    assert isinstance(result, ClassificationReview)
    assert result.decision == ReviewDecision.NEEDS_REVISION
    assert result.confidence == 0.80
    assert "genre" in result.reason.lower()