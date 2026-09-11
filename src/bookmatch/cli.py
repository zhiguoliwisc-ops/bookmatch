from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.result import BookMatchResult
from bookmatch.services.exceptions import AmbiguousBookError
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)


def select_book_from_candidates(
    candidates: list[EnrichedBook],
) -> EnrichedBook:
    """Prompt the user to select one book from multiple candidates."""

    print()
    print("Multiple possible books were found:")

    for index, candidate in enumerate(candidates, start=1):
        print(
            f"{index}. {candidate.title} — "
            f"{candidate.author or 'Unknown author'}"
        )

    while True:
        selection = input(
            f"Select a book (1-{len(candidates)}): "
        ).strip()

        if selection.isdigit():
            index = int(selection)

            if 1 <= index <= len(candidates):
                return candidates[index - 1]

        print(
            f"Please enter a number between 1 and {len(candidates)}."
        )


def run_cli(
    workflow: BookClassificationWorkflow,
) -> None:
    """Run the interactive BookMatch CLI."""

    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip() or None
    isbn = input("Enter ISBN (optional): ").strip() or None

    book = BookInput(
        title=title,
        author=author,
        isbn=isbn,
    )

    try:
        result = workflow.run(book)

    except AmbiguousBookError as error:
        selected_book = select_book_from_candidates(
            error.candidates
        )

        classification = workflow.classify_book(
            selected_book
        )

        result = BookMatchResult(
            book=selected_book,
            classification=classification,
        )

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