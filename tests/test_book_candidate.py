from bookmatch.models.book import EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.candidate_evidence import CandidateEvidence

def create_book() -> EnrichedBook:
    return EnrichedBook(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
        publication_date=None,
        isbn="9780312367541",
        description=None,
        source="Google Books",
    )


def test_book_candidate_contains_book_and_provider() -> None:
    book = create_book()

    candidate = BookCandidate(
        book=book,
        provider="Google Books",
    )

    assert candidate.book == book
    assert candidate.provider == "Google Books"


def test_book_candidate_can_use_open_library() -> None:
    book = create_book()

    candidate = BookCandidate(
        book=book,
        provider="Open Library",
    )

    assert candidate.provider == "Open Library"

def test_book_candidate_can_store_evidence() -> None:
    book = EnrichedBook(
        title="Pemmican Wars",
        author="Katherena Vermette",
        publication_date=None,
        isbn="9781553797357",
        description=None,
        source="Google Books",
    )

    evidence = CandidateEvidence(
        series_title="A Girl Called Echo",
        volume_number=1,
        author="Katherena Vermette",
    )

    candidate = BookCandidate(
        book=book,
        provider="Google Books",
        evidence=evidence,
    )

    assert candidate.evidence == evidence
    assert candidate.evidence.series_title == "A Girl Called Echo"
    assert candidate.evidence.volume_number == 1