import re
import unicodedata

from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate


def _normalize_title(title: str) -> str:
    """Normalize a title for conservative comparison."""

    normalized = unicodedata.normalize("NFKD", title)

    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def score_candidate_relevance(
    book: BookInput,
    candidate: BookCandidate,
) -> int:
    """Score how closely a candidate title matches the input title."""

    query_title = _normalize_title(book.title)
    candidate_title = _normalize_title(candidate.book.title)

    if not query_title or not candidate_title:
        return 0

    if query_title == candidate_title:
        return 100

    if query_title in candidate_title:
        return 75

    query_tokens = query_title.split()
    candidate_tokens = candidate_title.split()

    if not query_tokens or not candidate_tokens:
        return 0

    positions: list[int] = []

    for token in query_tokens:
        try:
            positions.append(candidate_tokens.index(token))
        except ValueError:
            continue

    if not positions:
        return 0

    if len(positions) == len(query_tokens):
        if positions == sorted(positions):
            token_span = max(positions) - min(positions)

            if token_span <= len(query_tokens) + 1:
                return 50

        return 25

    return 25