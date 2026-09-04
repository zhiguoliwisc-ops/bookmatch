from openai import OpenAI

from bookmatch.models.book import BookInput
from bookmatch.models.classification import BookClassification
from bookmatch.services.classification_service import ClassificationService


class OpenAIClassificationService(ClassificationService):
    """Classify books using an OpenAI language model."""

    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = client
        self.model = model

    def classify(self, book: BookInput) -> BookClassification:
        completion = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a book classification assistant. "
                        "Classify the book based on the information provided. "
                        "Determine the most appropriate reader age group and "
                        "reading difficulty."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Title: {book.title}\n"
                        f"Author: {book.author}\n"
                        f"Publication date: {book.publication_date}\n"
                        f"ISBN: {book.isbn}\n"
                        f"Description: {book.description}"
                    ),
                },
            ],
            response_format=BookClassification,
        )

        result = completion.choices[0].message.parsed

        if result is None:
            raise ValueError(
                "OpenAI did not return a valid book classification."
            )

        return result