from bookmatch.models.book import BookInput
from bookmatch.services.open_library_book_information_service import (
    OpenLibraryBookInformationService,
)
import os

from dotenv import load_dotenv
from openai import OpenAI

from bookmatch.models.book import BookInput
from bookmatch.services.open_library_book_information_service import (
    OpenLibraryBookInformationService,
)
from bookmatch.services.openai_classification_service import (
    OpenAIClassificationService,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)

from bookmatch.services.fallback_book_information_service import (
    FallbackBookInformationService,
)
from bookmatch.services.google_books_book_information_service import (
    GoogleBooksBookInformationService,
)


def main() -> None:
    """Run the BookMatch command-line application."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    title = input("Enter book title: ").strip()
    author = input("Enter author (optional): ").strip() or None
    isbn = input("Enter ISBN (optional): ").strip() or None

    book = BookInput(
        title=title,
        author=author,
        isbn=isbn,
    )

    primary_book_information_service = (
        OpenLibraryBookInformationService()
    )

    fallback_book_information_service = (
        GoogleBooksBookInformationService()
    )

    book_information_service = FallbackBookInformationService(
        primary=primary_book_information_service,
        fallback=fallback_book_information_service,
    )

    workflow = BookClassificationWorkflow(
        book_information_service=book_information_service,
        classification_service=OpenAIClassificationService(
            client=OpenAI(api_key=api_key),
        ),
    )

    result = workflow.run(book)

    print()
    print(f"Recommended age group: {result.recommended_age_group.value}")
    print(f"Reading difficulty: {result.reading_difficulty.value}")