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
                        "You are a careful book classification assistant. "
                        "Classify the book using the available bibliographic information "
                        "and description. "
                        "\n\n"
                        "For recommended age group and age range, prioritize the book's "
                        "intended and typical readership rather than simply the maturity "
                        "of individual themes. Consider the combination of vocabulary, "
                        "sentence complexity, narrative complexity, subject matter, "
                        "and the book's likely intended audience. "
                        "\n\n"
                        "Use the following age-group definitions: "
                        "Preschool: approximately ages 3–5. "
                        "Early Elementary: approximately ages 5–7. "
                        "Elementary: approximately ages 6–10. "
                        "Middle School: approximately ages 11–14. "
                        "High School: approximately ages 14–18. "
                        "Adult: approximately ages 18 and above. "
                        "\n\n"
                        "The selected age group and numerical age range should be "
                        "consistent with these definitions. "
                        "\n\n"
                        "For reading difficulty, evaluate the complexity of the reading "
                        "itself, including vocabulary, sentence structure, narrative "
                        "structure, and conceptual complexity. Do not equate mature themes "
                        "with high reading difficulty. "
                        "\n\n"
                        "For genre, identify the book's primary literary or content genre. "
                        "Primary genre means the single category that best describes the "
                        "book as a whole. "
                        "Do not use the intended audience or the physical format of the "
                        "book as its primary genre. For example, 'Graphic Novel' describes "
                        "a format rather than a literary genre. "
                        "Do not select a genre merely because the book contains elements "
                        "of that genre. For example, the presence of fantasy elements does "
                        "not necessarily make Fantasy the primary genre. "
                        "Choose the most appropriate primary genre based on the book's "
                        "overall narrative or subject matter. "
                        "\n\n"
                        "Use the available evidence and avoid making the classification "
                        "more specific or more mature than the evidence supports. "
                        "The recommended age range is an estimate based on the available "
                        "book information, not a precise scientific measurement."
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