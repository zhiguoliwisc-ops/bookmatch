import os

from dotenv import load_dotenv
from google import genai
from openai import OpenAI

from bookmatch.cli import run_cli
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)
from bookmatch.services.book_resolution_service import (
    BookResolutionServiceImpl,
)
from bookmatch.services.book_reviewer_agent import (
    BookReviewerAgent,
)
from bookmatch.services.candidate_book_resolver import (
    CandidateBookResolver,
)
from bookmatch.services.composite_book_candidate_service import (
    CompositeBookCandidateService,
)
from bookmatch.services.gemini_reviewer_agent import (
    GeminiReviewerAgent,
)
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)
from bookmatch.services.openai_classification_service import (
    OpenAIClassificationService,
)
from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)


def main() -> None:
    """Run the BookMatch command-line application."""

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not google_books_api_key:
        raise ValueError(
            "GOOGLE_BOOKS_API_KEY is not configured."
        )

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
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

    classifier_agent = OpenAIClassificationService(
        client=OpenAI(
            api_key=openai_api_key,
        ),
    )

    gemini_client = genai.Client(
        api_key=gemini_api_key,
    )

    reviewer_agent: BookReviewerAgent = GeminiReviewerAgent(
        client=gemini_client,
    )

    #reviewer_agent: BookReviewerAgent = OpenAIReviewerAgent(
    #    client=OpenAI(api_key=api_key),
    #)

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classifier_agent=classifier_agent,
        reviewer_agent=reviewer_agent,
    )

    run_cli(workflow)