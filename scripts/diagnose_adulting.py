from bookmatch.models.book import BookInput
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)
from bookmatch.services.candidate_deduplication import (
    deduplicate_candidates,
)
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)
from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)


def main() -> None:
    google_api_key = input(
        "Enter Google Books API key: "
    ).strip()

    book = BookInput(
        title=(
            "Adulting Life Skills for Young Adults, "
            "Beyond the Basics"
        ),
        author="Jaqui Meyer",
    )

    services: list[BookCandidateService] = [
        GoogleBooksBookCandidateService(
            api_key=google_api_key
        ),
        OpenLibraryBookCandidateService(),
    ]

    all_candidates = []

    for service in services:
        print(
            f"\n===== {service.__class__.__name__} ====="
        )

        try:
            candidates = service.find_candidates(book)
        except BookInformationServiceError as error:
            print(f"ERROR: {error}")
            continue

        print(f"RAW CANDIDATES: {len(candidates)}")

        for candidate in candidates:
            print(
                f"- {candidate.book.title} | "
                f"{candidate.book.author} | "
                f"{candidate.book.isbn} | "
                f"{candidate.provider}"
            )

        all_candidates.extend(candidates)

    candidates = deduplicate_candidates(
        all_candidates
    )

    print("\n===== AFTER DEDUP =====")
    print(f"TOTAL: {len(candidates)}")

    for candidate in candidates:
        print(
            f"- {candidate.book.title} | "
            f"{candidate.book.author} | "
            f"{candidate.book.isbn} | "
            f"{candidate.provider}"
        )

    identification_service = (
        BookIdentificationService()
    )

    matching_candidates = [
        candidate
        for candidate in candidates
        if identification_service._author_matches(
            book,
            candidate.book,
        )
        and identification_service._title_matches(
            book,
            candidate.book,
        )
    ]

    print("\n===== MATCHING CANDIDATES =====")
    print(
        f"TOTAL: {len(matching_candidates)}"
    )

    for candidate in matching_candidates:
        print(
            f"- {candidate.book.title} | "
            f"{candidate.book.author} | "
            f"{candidate.book.isbn} | "
            f"{candidate.provider}"
        )

    print("\n===== IDENTIFICATION =====")

    result = identification_service.identify(
        book,
        candidates,
    )

    print(f"STATUS: {result.status}")
    print(f"CONFIDENCE: {result.confidence}")
    print(f"REASON: {result.reason}")

    if result.matched_book:
        print(
            f"MATCHED: "
            f"{result.matched_book.title} | "
            f"{result.matched_book.author} | "
            f"{result.matched_book.isbn}"
        )


if __name__ == "__main__":
    main()