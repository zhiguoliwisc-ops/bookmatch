from bookmatch.models.book import BookInput
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)
from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)
from bookmatch.services.composite_book_candidate_service import (
    CompositeBookCandidateService,
)


def main() -> None:
    google_api_key = input(
        "Enter Google Books API key: "
    ).strip()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L’Engle",
    )

    google_service = GoogleBooksBookCandidateService(
        api_key=google_api_key,
    )
    open_library_service = OpenLibraryBookCandidateService()

    composite_service = CompositeBookCandidateService(
        services=[
            google_service,
            open_library_service,
        ]
    )

    identification_service = BookIdentificationService()

    print("=" * 100)
    print(f"INPUT TITLE : {book.title}")
    print(f"INPUT AUTHOR: {book.author}")
    print()

    candidates = composite_service.find_candidates(book)

    print(f"TOTAL CANDIDATES AFTER DEDUP: {len(candidates)}")
    print()

    for index, candidate in enumerate(candidates, start=1):
        print(
            f"{index}. "
            f"Title={candidate.book.title!r} | "
            f"Author={candidate.book.author!r} | "
            f"ISBN={candidate.book.isbn!r} | "
            f"Provider={candidate.provider}"
        )

    print()
    print("=" * 100)

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

    print(
        f"MATCHING CANDIDATES FOR IDENTIFICATION: "
        f"{len(matching_candidates)}"
    )
    print()

    for index, candidate in enumerate(
        matching_candidates,
        start=1,
    ):
        print(
            f"{index}. "
            f"Title={candidate.book.title!r} | "
            f"Author={candidate.book.author!r} | "
            f"ISBN={candidate.book.isbn!r} | "
            f"Provider={candidate.provider}"
        )

    print()
    print(
        "same_book_identity =",
        identification_service._same_book_identity(
            matching_candidates
        ),
    )


if __name__ == "__main__":
    main()