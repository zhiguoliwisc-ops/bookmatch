import os

from dotenv import load_dotenv
from openai import OpenAI

from bookmatch.models.book import BookInput

from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)

from bookmatch.services.candidate_book_resolver import (
    CandidateBookResolver,
)

from bookmatch.services.composite_book_candidate_service import (
    CompositeBookCandidateService,
)

from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)

from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)

from bookmatch.services.openai_classification_service import (
    OpenAIClassificationService,
)

from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)


def main() -> None:
    """Run the BookMatch command-line application."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not google_books_api_key:
        raise ValueError("GOOGLE_BOOKS_API_KEY is not configured.")

    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip() or None
    isbn = input("Enter ISBN (optional): ").strip() or None

    book = BookInput(
        title=title,
        author=author,
        isbn=isbn,
    )

    google_books_candidate_service = (
        GoogleBooksBookCandidateService(
            api_key=google_books_api_key,
        )
    )

    open_library_candidate_service = (
        OpenLibraryBookCandidateService()
    )

    candidate_service = CompositeBookCandidateService(
        services=[
            google_books_candidate_service,
            open_library_candidate_service,
        ],
    )

    book_resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        identification_service=BookIdentificationService(),
    )

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classification_service=OpenAIClassificationService(
            client=OpenAI(api_key=api_key),
        ),
    )

    result = workflow.run(book)

    print()
    print(f"Title: {result.book.title}")
    print(f"Author: {result.book.author}")
    print(
        f"Recommended age group: "
        f"{result.classification.recommended_age_group.value}"
    )
    print(
        f"Recommended age range: "
        f"{result.classification.minimum_age}–"
        f"{result.classification.maximum_age} years old"
    )
    print(
        f"Reading difficulty: "
        f"{result.classification.reading_difficulty.value} / 5"
    )
    print(f"Genre: {result.classification.genre}")