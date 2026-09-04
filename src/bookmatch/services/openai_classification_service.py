from openai import OpenAI

from bookmatch.models.book import BookInput
from bookmatch.models.classification import BookClassification
from bookmatch.services.classification_service import ClassificationService


class OpenAIClassificationService(ClassificationService):
    """Classify books using an OpenAI language model."""

    def __init__(self, client: OpenAI) -> None:
        self.client = client

    def classify(self, book: BookInput) -> BookClassification:
        raise NotImplementedError