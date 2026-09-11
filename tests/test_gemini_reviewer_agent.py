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


def test_gemini_reviewer_agent_returns_review() -> None:
    from bookmatch.services.gemini_reviewer_agent import (
        GeminiReviewerAgent,
    )

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
    mock_response.parsed = parsed_review

    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    agent = GeminiReviewerAgent(client=mock_client)

    result = agent.review(
        original_input,
        book,
        classification,
    )

    assert isinstance(result, ClassificationReview)
    assert result.decision == ReviewDecision.APPROVED
    assert result.confidence == 0.95


def test_gemini_reviewer_agent_raises_when_parsed_review_is_none() -> None:
    from bookmatch.services.gemini_reviewer_agent import (
        GeminiReviewerAgent,
    )

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

    mock_response = Mock()
    mock_response.parsed = None

    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    agent = GeminiReviewerAgent(client=mock_client)

    with pytest.raises(ValueError, match="valid classification review"):
        agent.review(
            original_input,
            book,
            classification,
        )


def test_gemini_reviewer_agent_sends_review_input() -> None:
    from bookmatch.services.gemini_reviewer_agent import (
        GeminiReviewerAgent,
    )

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
    mock_response.parsed = parsed_review

    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    agent = GeminiReviewerAgent(client=mock_client)

    agent.review(
        original_input,
        book,
        classification,
    )

    mock_client.models.generate_content.assert_called_once()

    call_kwargs = (
        mock_client.models.generate_content.call_args.kwargs
    )

    prompt = call_kwargs["contents"]

    assert "Dog Man" in prompt
    assert "Dav Pilkey" in prompt
    assert "Original user input" in prompt
    assert "Selected book" in prompt
    assert "Elementary" in prompt
    assert "6–10" in prompt
    assert "Graphic Novel" in prompt