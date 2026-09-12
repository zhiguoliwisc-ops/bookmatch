from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.candidate_relevance import (
    score_candidate_relevance,
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


def test_exact_title_match_gets_highest_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "16 Forever",
        "Lance Rubin",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 100


def test_title_with_query_phrase_gets_second_highest_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Forever Strong",
        "Gabrielle Lyon",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 25


def test_title_with_all_query_tokens_but_extra_words_gets_middle_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "16 Steps to Forever",
        "Georgia Beers",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 50


def test_title_with_one_query_token_gets_low_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Xeny Volume 16",
        "Robert A. S. Fortin",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 25


def test_incidental_title_overlap_gets_low_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Lone Wolf's Lady (This Time Forever, Book 16)",
        "Beverly Barton",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 25


def test_unrelated_candidate_gets_zero_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Node.js Recipes",
        "Cory Gackenheimer",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 0

def test_exact_title_has_highest_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "16 Forever",
        "Lance Rubin",
    )

    score = score_candidate_relevance(book, candidate)

    assert score == 100


def test_close_title_match_scores_below_exact_match() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "16 Steps to Forever",
        "Georgia Beers",
    )

    score = score_candidate_relevance(book, candidate)

    assert 50 <= score < 100


def test_distant_title_match_scores_below_close_match() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Lone Wolf's Lady (This Time Forever, Book 16)",
        "Beverly Barton",
    )

    score = score_candidate_relevance(book, candidate)

    assert 0 < score < 50


def test_single_keyword_match_gets_low_score() -> None:
    book = BookInput(title="16 Forever")

    candidate = create_candidate(
        "Forever Strong",
        "Gabrielle Lyon",
    )

    score = score_candidate_relevance(book, candidate)

    assert 0 < score < 50