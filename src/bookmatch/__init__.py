from bookmatch.models.book import BookInput
from bookmatch.services.open_library_book_information_service import (
    OpenLibraryBookInformationService,
)
from bookmatch.services.rule_based_classification_service import (
    RuleBasedClassificationService,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)


def main() -> None:
    """Run the BookMatch command-line application."""

    title = input("Enter book title: ").strip()
    author = input("Enter author (optional): ").strip() or None
    isbn = input("Enter ISBN (optional): ").strip() or None

    book = BookInput(
        title=title,
        author=author,
        isbn=isbn,
    )

    workflow = BookClassificationWorkflow(
        book_information_service=OpenLibraryBookInformationService(),
        classification_service=RuleBasedClassificationService(),
    )

    result = workflow.run(book)

    print()
    print(f"Recommended age group: {result.recommended_age_group.value}")
    print(f"Reading difficulty: {result.reading_difficulty.value}")