import pytest
from unittest.mock import Mock

from openai import OpenAI

from bookmatch.models.book import BookInput
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.services.classification_service import ClassificationService
from bookmatch.services.openai_classification_service import (
    OpenAIClassificationService,
)


def test_openai_classification_service_implements_interface():
    client = OpenAI(api_key="test-key")

    service = OpenAIClassificationService(client)

    assert isinstance(service, ClassificationService)


def test_openai_classification_service_returns_classification():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=7,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.MODERATE,
        genre="Children's Fiction",
        confidence=0.9,
    )

    parsed_message = Mock()
    parsed_message.parsed = classification

    choice = Mock()
    choice.message = parsed_message

    completion = Mock()
    completion.choices = [choice]

    client = Mock(spec=OpenAI)
    client.chat.completions.parse.return_value = completion

    service = OpenAIClassificationService(client)

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        description="A children's novel about a pig and a spider.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.ELEMENTARY
    assert result.minimum_age == 7
    assert result.maximum_age == 10
    assert result.reading_difficulty == ReadingDifficulty.MODERATE
    assert result.genre == "Children's Fiction"
    assert result.confidence == 0.9

def test_openai_classification_service_raises_when_parsed_result_is_none():
    parsed_message = Mock()
    parsed_message.parsed = None

    choice = Mock()
    choice.message = parsed_message

    completion = Mock()
    completion.choices = [choice]

    client = Mock(spec=OpenAI)
    client.chat.completions.parse.return_value = completion

    service = OpenAIClassificationService(client)

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with pytest.raises(
        ValueError,
        match="OpenAI did not return a valid book classification.",
    ):
        service.classify(book)