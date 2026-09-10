from bookmatch.models.book_candidate import BookCandidate


def deduplicate_candidates(
    candidates: list[BookCandidate],
) -> list[BookCandidate]:
    """Remove duplicate book candidates while preserving order."""
    unique_candidates: list[BookCandidate] = []

    for candidate in candidates:
        if any(
            _are_duplicates(candidate, existing)
            for existing in unique_candidates
        ):
            continue

        unique_candidates.append(candidate)

    return unique_candidates


def _are_duplicates(
    first: BookCandidate,
    second: BookCandidate,
) -> bool:
    """Return whether two candidates represent the same book."""
    first_isbn = first.book.isbn
    second_isbn = second.book.isbn

    if first_isbn and second_isbn:
        return _normalize_isbn(first_isbn) == _normalize_isbn(
            second_isbn
        )

    return (
        _normalize(first.book.title)
        == _normalize(second.book.title)
        and _normalize(first.book.author or "")
        == _normalize(second.book.author or "")
    )


def _normalize(value: str) -> str:
    """Normalize text for comparison."""
    return " ".join(value.split()).casefold()


def _normalize_isbn(isbn: str) -> str:
    """Normalize an ISBN for comparison."""
    return "".join(
        character
        for character in isbn
        if character.isalnum()
    ).upper()