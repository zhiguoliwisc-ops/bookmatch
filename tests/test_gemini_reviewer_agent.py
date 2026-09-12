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
from bookmatch.services.gemini_reviewer_agent import (
    GeminiReviewerAgent,
)


def test_gemini_reviewer_agent_returns_review() -> None:
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

    mock_interaction = Mock()
    mock_interaction.output_text = parsed_review.model_dump_json()

    mock_client = Mock()
    mock_client.interactions.create.return_value = mock_interaction

    agent = GeminiReviewerAgent(client=mock_client)

    result = agent.review(
        original_input,
        book,
        classification,
    )

    assert isinstance(result, ClassificationReview)
    assert result.decision == ReviewDecision.APPROVED
    assert result.confidence == 0.95


def test_gemini_reviewer_agent_raises_when_output_text_is_none() -> None:
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

    mock_interaction = Mock()
    mock_interaction.output_text = None

    mock_client = Mock()
    mock_client.interactions.create.return_value = mock_interaction

    agent = GeminiReviewerAgent(client=mock_client)

    with pytest.raises(ValueError, match="valid classification review"):
        agent.review(
            original_input,
            book,
            classification,
        )


def test_gemini_reviewer_agent_sends_review_input() -> None:
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

    mock_interaction = Mock()
    mock_interaction.output_text = parsed_review.model_dump_json()

    mock_client = Mock()
    mock_client.interactions.create.return_value = mock_interaction

    agent = GeminiReviewerAgent(client=mock_client)

    agent.review(
        original_input,
        book,
        classification,
    )

    mock_client.interactions.create.assert_called_once()

    call_kwargs = (
        mock_client.interactions.create.call_args.kwargs
    )

    prompt = call_kwargs["input"]

    assert "Dog Man" in prompt
    assert "Dav Pilkey" in prompt
    assert "Original user input" in prompt
    assert "Selected book" in prompt
    assert "Elementary" in prompt
    assert "6–10" in prompt
    assert "Graphic Novel" in prompt

    response_format = call_kwargs["response_format"]

    assert response_format["type"] == "text"
    assert response_format["mime_type"] == "application/json"
    assert (
        response_format["schema"]
        == ClassificationReview.model_json_schema()
    )