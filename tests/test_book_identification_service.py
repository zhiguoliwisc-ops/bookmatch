from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import (
    IdentificationStatus,
)
from bookmatch.models.candidate_evidence import CandidateEvidence
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)

def create_candidate(
    title: str,
    author: str | None,
    description: str | None = None,
    isbn: str | None = None,
    evidence: CandidateEvidence | None = None,
) -> BookCandidate:
    book = EnrichedBook(
        title=title,
        author=author,
        publication_date=None,
        isbn=isbn,
        description=description,
        source="Google Books",
    )

    return BookCandidate(
        book=book,
        provider="Google Books",
        evidence=evidence,
    )


def test_exact_title_and_author_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L'Engle",
    )

    candidate = create_candidate(
        "A Wrinkle in Time",
        "Madeline L'Engle",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book == candidate.book
    assert result.confidence == 1.0


def test_title_with_extra_subtitle_is_corrected_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Deadly Wandering",
        author="Matt Richtel",
    )

    candidate = create_candidate(
        "A Deadly Wandering: A Mystery, A Landmark Investigation",
        "Matt Richtel",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.CORRECTED_MATCH
    assert result.matched_book == candidate.book
    assert result.confidence == 0.95


def test_title_matching_ignores_case_and_extra_whitespace() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="  A   Perfect Day ",
        author="Lane Smith",
    )

    candidate = create_candidate(
        "A Perfect Day",
        "Lane Smith",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH


def test_author_mismatch_is_not_accepted() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Perfect Day",
        author="Different Author",
    )

    candidate = create_candidate(
        "A Perfect Day",
        "Lane Smith",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_multiple_editions_with_same_title_and_author_are_exact_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="The Outsiders",
        author="S. E. Hinton",
    )

    candidates = [
        create_candidate(
            "The Outsiders",
            "S. E. Hinton",
            isbn="9780140385724",
        ),
        create_candidate(
            "The Outsiders",
            "S. E. Hinton",
            isbn="9780671665202",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None


def test_no_candidates_returns_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Unknown Book",
        author="Unknown Author",
    )

    result = service.identify(book, [])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_unrelated_title_returns_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    candidate = create_candidate(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_matching_isbn_returns_exact_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="978-1234567890",
    )

    candidate = create_candidate(
        "Completely Different Title",
        "Different Author",
    )

    candidate.book.isbn = "9781234567890"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book == candidate.book


def test_isbn_match_ignores_formatting() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        isbn="978-123-4567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    candidate.book.isbn = "9781234567890"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH


def test_isbn_mismatch_does_not_fall_back_to_title() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="9781234567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    candidate.book.isbn = "9780987654321"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_isbn_without_candidate_is_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="9781234567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_author_name_order_variation_is_accepted() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Book",
        author="Lance Rubin",
    )

    candidate = create_candidate(
        title="A Book",
        author="Rubin Lance",
    )

    result = service.identify(
        book,
        [candidate],
    )

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None


def test_author_spelling_variation_is_accepted() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L’Engle",
    )

    candidate = create_candidate(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    result = service.identify(
        book,
        [candidate],
    )

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None
    assert result.matched_book.author == "Madeleine L'Engle"


def test_similar_but_different_author_is_not_accepted() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Book",
        author="Jane Smith",
    )

    candidate = create_candidate(
        title="A Book",
        author="Lane Smith",
    )

    result = service.identify(
        book,
        [candidate],
    )

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_series_volume_metadata_can_identify_canonical_book() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Girl Called Echo Vol. 1",
        author="Katherena Vermette",
    )

    metadata_candidate = create_candidate(
        title="Pemmican Wars (A Girl Called Echo, Vol. 1).",
        author=None,
        description=(
            "Pemmican Wars is the first graphic novel "
            "in a new series, A Girl Called Echo, "
            "by Governor General Award-winning writer "
            "Katherena Vermette."
        ),
        evidence=CandidateEvidence(
            series_title="A Girl Called Echo",
            volume_number=1,
            author="Katherena Vermette",
            canonical_title="Pemmican Wars",
        ),
    )

    canonical_candidate = create_candidate(
        title="Pemmican Wars",
        author="Katherena Vermette",
        isbn="9781553797357",
    )

    result = service.identify(
        book,
        [
            metadata_candidate,
            canonical_candidate,
        ],
    )

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None
    assert result.matched_book.title == "Pemmican Wars"
    assert result.matched_book.author == "Katherena Vermette"
    assert result.matched_book.isbn == "9781553797357"

def test_different_isbns_with_same_title_and_author_are_same_book() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L’Engle",
    )

    candidates = [
        create_candidate(
            title="A Wrinkle in Time",
            author="Madeleine L'Engle",
            isbn="9780312367558",
        ),
        create_candidate(
            title="A Wrinkle in Time",
            author="Madeleine L'Engle",
            isbn="0440498058",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None
    assert result.matched_book.title == "A Wrinkle in Time"


def test_candidate_base_title_matches_input_with_subtitle() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title=(
            "A Deadly Wandering: A Mystery, A Landmark Investigation, "
            "and the Astonishing Science of Attention in the Digital Age"
        ),
        author="Matt Richtel",
    )

    candidates = [
        create_candidate(
            "A Deadly Wandering",
            "Matt Richtel",
            isbn="9780062284082",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.CORRECTED_MATCH
    assert result.matched_book is not None
    assert result.matched_book.title == "A Deadly Wandering"

def test_multiple_editions_with_title_variations_are_same_book() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L’Engle",
    )

    candidates = [
        create_candidate(
            "A Wrinkle in Time",
            "Madeleine L'Engle",
            isbn="9780312367558",
        ),
        create_candidate(
            "A Wrinkle in Time: 50th Anniversary Commemorative Edition",
            "Madeleine L'Engle",
            isbn="9781250004673",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None

def test_titles_with_same_canonical_title_are_same_work() -> None:
    service = BookIdentificationService()

    assert service._titles_match_as_same_work(
        "A Wrinkle in Time",
        "A Wrinkle in Time",
    )



def test_title_with_edition_subtitle_is_same_work() -> None:
    service = BookIdentificationService()

    assert service._titles_match_as_same_work(
        "A Wrinkle in Time",
        "A Wrinkle in Time: 50th Anniversary Commemorative Edition",
    )


def test_different_titles_are_not_same_work() -> None:
    service = BookIdentificationService()

    assert not service._titles_match_as_same_work(
        "A Wrinkle in Time",
        "A Wind in the Door",
    )

def test_title_matching_ignores_punctuation_difference():
    service = BookIdentificationService()

    book = BookInput(
        title="Adulting Life Skills for Young Adults, Beyond the Basics",
        author="Jaqui Meyer",
    )

    candidate = EnrichedBook(
        title="Adulting Life Skills for Young Adults Beyond the Basics",
        author="Jaqui Meyer",
        source="Google Books",
    )

    assert service._title_matches(book, candidate)
def test_title_only_prefers_exact_title_over_series_titles():
    service = BookIdentificationService()

    book = BookInput(
        title="Dog Man",
    )

    candidates = [
        create_candidate(
            title="Dog Man",
            author="Dav Pilkey",
            isbn="1338611941",
        ),
        create_candidate(
            title="Dog Man",
            author="Dav Pilkey",
            isbn="9352755952",
        ),
        create_candidate(
            title="Dog Man",
            author="Dav Pilkey",
            isbn="0545581605",
        ),
        create_candidate(
            title="Dog Man: Grime and Punishment: A Graphic Novel",
            author="Dav Pilkey",
            isbn="9781338554274",
        ),
        create_candidate(
            title="Dog Man: For Whom the Ball Rolls: A Graphic Novel",
            author="Dav Pilkey",
            isbn="9781338236613",
        ),
        create_candidate(
            title="Dog Man: Big Jim Begins: A Graphic Novel",
            author="Dav Pilkey",
            isbn="9781338896473",
        ),
        create_candidate(
            title="Dog Man: Big Jim Believes: A Graphic Novel",
            author="Dav Pilkey",
            isbn="9781546176206",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None
    assert result.matched_book.title == "Dog Man"

def test_extract_author_ignores_fictitious_characters() -> None:
    authors = [
        "Dav Pilkey",
        "George Beard (Fictitious character)",
        "Harold Hutchins (Fictitious character)",
    ]

    result = GoogleBooksBookCandidateService._extract_author(
        authors
    )

    assert result == "Dav Pilkey"

def test_extract_author_preserves_multiple_real_authors() -> None:
    authors = [
        "Author One",
        "Author Two",
    ]

    result = GoogleBooksBookCandidateService._extract_author(
        authors
    )

    assert result == "Author One, Author Two"

def test_same_title_with_different_authors_is_ambiguous():
    service = BookIdentificationService()

    candidates = [
        BookCandidate(
            book=EnrichedBook(
                title="Dog Man",
                author="Dav Pilkey",
                publication_date=None,
                isbn="1338611941",
                description=None,
                source="Google Books",
            ),
            provider="Google Books",
        ),
        BookCandidate(
            book=EnrichedBook(
                title="Dog Man",
                author="Maurice Procter",
                publication_date=None,
                isbn=None,
                description=None,
                source="Open Library",
            ),
            provider="Open Library",
        ),
    ]

    result = service.identify(
        BookInput(title="Dog Man"),
        candidates,
    )

    assert result.status == IdentificationStatus.AMBIGUOUS
    assert result.matched_book is None