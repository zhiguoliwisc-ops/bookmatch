from google import genai
from google.genai import types

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.classification_review import ClassificationReview
from bookmatch.services.book_reviewer_agent import BookReviewerAgent


class GeminiReviewerAgent(BookReviewerAgent):
    """Review book classifications using a Google Gemini model."""

    def __init__(
        self,
        client: genai.Client,
        model: str = "gemini-3.6-flash",
    ) -> None:
        self.client = client
        self.model = model

    def review(
        self,
        original_input: BookInput,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        prompt = (
            "You are an independent reviewer of a book classification. "
            "Do not assume the proposed classification is correct. "
            "Evaluate it against the original user input and the selected "
            "book information.\n\n"
            "Review the following:\n"
            "1. Whether the selected book is consistent with the original "
            "user input.\n"
            "2. Whether the recommended age group and age range are "
            "consistent with the book and its intended readership.\n"
            "3. Whether the reading difficulty is reasonable for the book.\n"
            "4. Whether the proposed primary genre is appropriate.\n\n"
            "Approve the classification when it is reasonably supported by "
            "the evidence. Request revision when there is a clear or "
            "material inconsistency.\n\n"
            f"Original user input:\n"
            f"Title: {original_input.title}\n"
            f"Author: {original_input.author}\n"
            f"ISBN: {original_input.isbn}\n\n"
            f"Selected book:\n"
            f"Title: {book.title}\n"
            f"Author: {book.author}\n"
            f"Publication date: {book.publication_date}\n"
            f"ISBN: {book.isbn}\n"
            f"Description: {book.description}\n\n"
            f"Proposed classification:\n"
            f"Age group: {classification.recommended_age_group.value}\n"
            f"Age range: "
            f"{classification.minimum_age}–"
            f"{classification.maximum_age}\n"
            f"Reading difficulty: "
            f"{classification.reading_difficulty.value} / 5\n"
            f"Genre: {classification.genre}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClassificationReview,
            ),
        )

        result = response.parsed

        if result is None:
            raise ValueError(
                "Gemini did not return a valid classification review."
            )

        return result