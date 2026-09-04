from bookmatch.models.book import BookInput
from bookmatch.models.book import BookInput, EnrichedBook


def test_create_book_with_title_only():
    book = BookInput(
        title="Charlotte's Web",
    )

    assert book.title == "Charlotte's Web"
    assert book.author is None
    assert book.publication_date is None
    assert book.isbn is None
    assert book.description is None


def test_create_book_with_full_information():
    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A story about friendship between a pig and a spider.",
    )

    assert book.title == "Charlotte's Web"
    assert book.author == "E. B. White"
    assert book.publication_date == "1952"
    assert book.isbn == "9780064400558"
    assert book.description is not None

def test_create_enriched_book():
    book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        description="A story about friendship between a pig and a spider.",
        source="GoogleBooks",
    )

    assert book.title == "Charlotte's Web"
    assert book.description is not None
    assert book.source == "GoogleBooks"