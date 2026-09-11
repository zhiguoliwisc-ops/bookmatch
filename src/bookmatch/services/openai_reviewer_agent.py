from openai import OpenAI

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.classification_review import ClassificationReview
from bookmatch.services.book_reviewer_agent import BookReviewerAgent


class OpenAIReviewerAgent(BookReviewerAgent):
    """Review book classifications using an OpenAI language model."""

    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = client
        self.model = model

    def review(
        self,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        completion = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful book classification reviewer. "
                        "Review the proposed classification against the "
                        "available bibliographic information and description. "
                        "\n\n"
                        "Determine whether the classification is consistent "
                        "with the evidence provided. "
                        "\n\n"
                        "Review the recommended age group, recommended age "
                        "range, reading difficulty, and primary genre. "
                        "Consider the intended readership, vocabulary, "
                        "sentence complexity, narrative complexity, subject "
                        "matter, and overall genre. "
                        "\n\n"
                        "Do not reclassify the book simply because you would "
                        "choose a slightly different classification. "
                        "Approve classifications that are reasonably "
                        "supported by the available evidence. "
                        "Request revision when there is a clear or material "
                        "inconsistency between the classification and the "
                        "book evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Book information:\n"
                        f"Title: {book.title}\n"
                        f"Author: {book.author}\n"
                        f"Publication date: {book.publication_date}\n"
                        f"ISBN: {book.isbn}\n"
                        f"Description: {book.description}\n\n"
                        f"Proposed classification:\n"
                        f"Age group: "
                        f"{classification.recommended_age_group.value}\n"
                        f"Age range: "
                        f"{classification.minimum_age}–"
                        f"{classification.maximum_age}\n"
                        f"Reading difficulty: "
                        f"{classification.reading_difficulty.value} / 5\n"
                        f"Genre: {classification.genre}"
                    ),
                },
            ],
            response_format=ClassificationReview,
        )

        result = completion.choices[0].message.parsed

        if result is None:
            raise ValueError(
                "OpenAI did not return a valid classification review."
            )

        return result