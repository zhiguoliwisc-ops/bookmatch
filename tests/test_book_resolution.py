from bookmatch.models.book import EnrichedBook
from bookmatch.models.book_resolution import (
    BookResolution,
    ResolutionDecision,
)


def make_book(
    title: str,
    author: str,
) -> EnrichedBook:
    return EnrichedBook(
        title=title,
        author=author,
        publication_date=None,
        isbn=None,
        description=None,
        source="Test",
    )


def test_auto_resolve_contains_selected_book():
    book = make_book("Dog Man", "Dav Pilkey")

    result = BookResolution(
        decision=ResolutionDecision.AUTO_RESOLVE,
        selected_book=book,
    )

    assert result.decision == ResolutionDecision.AUTO_RESOLVE
    assert result.selected_book == book
    assert result.candidates == []


def test_ask_user_contains_candidates():
    candidates = [
        make_book("Dog Man", "Dav Pilkey"),
        make_book("Dog Man", "Maurice Procter"),
    ]

    result = BookResolution(
        decision=ResolutionDecision.ASK_USER,
        candidates=candidates,
    )

    assert result.decision == ResolutionDecision.ASK_USER
    assert result.selected_book is None
    assert result.candidates == candidates


def test_not_found_contains_no_book():
    result = BookResolution(
        decision=ResolutionDecision.NOT_FOUND,
    )

    assert result.decision == ResolutionDecision.NOT_FOUND
    assert result.selected_book is None
    assert result.candidates == []