import os

from dotenv import load_dotenv
from openai import OpenAI

from bookmatch.services.book_resolution_service import (
    BookResolutionServiceImpl,
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

from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)

from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)

from bookmatch.cli import run_cli


def main() -> None:
    """Run the BookMatch command-line application."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not google_books_api_key:
        raise ValueError(
            "GOOGLE_BOOKS_API_KEY is not configured."
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

    identification_service = BookIdentificationService()

    resolution_service = BookResolutionServiceImpl(
        identification_service=identification_service,
    )

    book_resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
    )

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classifier_agent=OpenAIClassificationService(
            client=OpenAI(api_key=api_key),
        ),
    )

    run_cli(workflow)