from openai import OpenAI

from bookmatch.services.classification_service import ClassificationService
from bookmatch.services.openai_classification_service import (
    OpenAIClassificationService,
)


def test_openai_classification_service_implements_interface():
    client = OpenAI(api_key="test-key")

    service = OpenAIClassificationService(client)

    assert isinstance(service, ClassificationService)