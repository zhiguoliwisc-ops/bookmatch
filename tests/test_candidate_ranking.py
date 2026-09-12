from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate

from bookmatch.services.candidate_ranking import (
    filter_candidates_by_relevance,
    rank_candidates,
    limit_candidates,
)

def create_candidate(
    title: str,
    author: str | None = None,
) -> BookCandidate:
    return BookCandidate(
        book=EnrichedBook(
            title=title,
            author=author,
            publication_date=None,
            isbn=None,
            description=None,
            source="Test",
        ),
        provider="Test",
    )


def test_rank_candidates_puts_exact_title_first() -> None:
    book = BookInput(title="16 Forever")

    candidates = [
        create_candidate(
            "Node.js Recipes",
            "Cory Gackenheimer",
        ),
        create_candidate(
            "Forever Strong",
            "Gabrielle Lyon",
        ),
        create_candidate(
            "16 Forever",
            "Lance Rubin",
        ),
    ]

    ranked = rank_candidates(book, candidates)

    assert ranked[0].book.title == "16 Forever"
    assert ranked[1].book.title == "Forever Strong"
    assert ranked[2].book.title == "Node.js Recipes"


def test_rank_candidates_preserves_all_candidates() -> None:
    book = BookInput(title="16 Forever")

    candidates = [
        create_candidate("16 Forever", "Lance Rubin"),
        create_candidate("Node.js Recipes", "Cory Gackenheimer"),
    ]

    ranked = rank_candidates(book, candidates)

    assert len(ranked) == len(candidates)


def test_rank_candidates_preserves_input_order_for_equal_scores() -> None:
    book = BookInput(title="16 Forever")

    candidates = [
        create_candidate("16 Forever", "Lance Rubin"),
        create_candidate("16 Forever", "Diana Frances Ferrell"),
    ]

    ranked = rank_candidates(book, candidates)

    assert ranked[0].book.author == "Lance Rubin"
    assert ranked[1].book.author == "Diana Frances Ferrell"

def test_filter_candidates_removes_zero_relevance_candidates() -> None:
    book = BookInput(title="16 Forever")

    candidates = [
        create_candidate(
            "16 Forever",
            "Lance Rubin",
        ),
        create_candidate(
            "Forever Strong",
            "Gabrielle Lyon",
        ),
        create_candidate(
            "Node.js Recipes",
            "Cory Gackenheimer",
        ),
        create_candidate(
            "House Documents",
            "USA House of Representatives",
        ),
    ]

    filtered = filter_candidates_by_relevance(
        book,
        candidates,
    )

    assert [candidate.book.title for candidate in filtered] == [
        "16 Forever",
        "Forever Strong",
    ]


def test_limit_candidates_returns_top_10() -> None:
    candidates = [
        create_candidate(
            f"Book {index}",
            f"Author {index}",
        )
        for index in range(1, 16)
    ]

    limited = limit_candidates(candidates)

    assert len(limited) == 10
    assert [candidate.book.title for candidate in limited] == [
        f"Book {index}"
        for index in range(1, 11)
    ]


def test_limit_candidates_returns_all_when_fewer_than_10() -> None:
    candidates = [
        create_candidate(
            f"Book {index}",
            f"Author {index}",
        )
        for index in range(1, 6)
    ]

    limited = limit_candidates(candidates)

    assert limited == candidates