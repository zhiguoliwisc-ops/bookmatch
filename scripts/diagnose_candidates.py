from bookmatch.models.book import BookInput
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)
from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)


TEST_BOOKS = [
    ("A Perfect Day", "Lane Smith"),
    ("A Wrinkle in Time", "Madeline L’Engle"),
    ("16 Forever", "Rubin Lance"),
    ("1776", "David McCullough"),
    (
        "A Deadly Wandering: A Mystery, A Landmark Investigation, "
        "and the Astonishing Science of Attention in the Digital Age",
        "Matt Richtel",
    ),
    (
        "Adulting Life Skills for Young Adults, Beyond the Basics",
        "Jaqui Meyer",
    ),
]


def print_candidates(
    provider: str,
    candidates,
) -> None:
    print(f"\n--- {provider}: {len(candidates)} candidates ---")

    for index, candidate in enumerate(candidates, start=1):
        book = candidate.book

        print(
            f"{index}. "
            f"Title={book.title!r} | "
            f"Author={book.author!r} | "
            f"ISBN={book.isbn!r}"
        )

        if candidate.evidence is not None:
            print(
                f"   Evidence={candidate.evidence}"
            )


def main() -> None:
    google_api_key = input(
        "Enter Google Books API key: "
    ).strip()

    google_service = GoogleBooksBookCandidateService(
        api_key=google_api_key,
    )
    open_library_service = OpenLibraryBookCandidateService()

    for title, author in TEST_BOOKS:
        print("\n" + "=" * 100)
        print(f"INPUT: {title}")
        print(f"AUTHOR: {author}")

        book = BookInput(
            title=title,
            author=author,
        )

        try:
            google_candidates = (
                google_service.find_candidates(book)
            )
            print_candidates(
                "Google Books",
                google_candidates,
            )
        except Exception as error:
            print(
                f"\nGoogle Books ERROR: "
                f"{type(error).__name__}: {error}"
            )

        try:
            open_library_candidates = (
                open_library_service.find_candidates(book)
            )
            print_candidates(
                "Open Library",
                open_library_candidates,
            )
        except Exception as error:
            print(
                f"\nOpen Library ERROR: "
                f"{type(error).__name__}: {error}"
            )


if __name__ == "__main__":
    main()