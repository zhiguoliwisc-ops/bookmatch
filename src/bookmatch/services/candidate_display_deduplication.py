from bookmatch.models.book import EnrichedBook


def deduplicate_display_candidates(
    candidates: list[EnrichedBook],
) -> list[EnrichedBook]:
    """Remove duplicate books from the human-facing candidate list."""

    unique_candidates: list[EnrichedBook] = []

    seen: set[tuple[str, str]] = set()

    for candidate in candidates:
        key = (
            _normalize(candidate.title),
            _normalize(candidate.author or ""),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_candidates.append(candidate)

    return unique_candidates


def _normalize(value: str) -> str:
    """Normalize text for display-level comparison."""

    return " ".join(value.split()).casefold()