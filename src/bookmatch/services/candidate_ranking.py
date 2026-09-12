from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.candidate_relevance import (
    score_candidate_relevance,
)


MAX_DISPLAYED_CANDIDATES = 10


def rank_candidates(
    book: BookInput,
    candidates: list[BookCandidate],
) -> list[BookCandidate]:
    """Rank candidates by relevance while preserving stable order."""

    return sorted(
        candidates,
        key=lambda candidate: score_candidate_relevance(
            book,
            candidate,
        ),
        reverse=True,
    )


def filter_candidates_by_relevance(
    book: BookInput,
    candidates: list[BookCandidate],
) -> list[BookCandidate]:
    """Remove candidates with no title relevance to the input."""

    return [
        candidate
        for candidate in candidates
        if score_candidate_relevance(
            book,
            candidate,
        ) > 0
    ]


def limit_candidates(
    candidates: list[BookCandidate],
) -> list[BookCandidate]:
    """Limit candidates to the maximum displayed count."""

    return candidates[:MAX_DISPLAYED_CANDIDATES]