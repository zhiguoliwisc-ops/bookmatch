from pydantic import BaseModel, Field


class BookInput(BaseModel):
    """Basic information provided for a book."""

    title: str = Field(
        ...,
        description="Title of the book.",
    )

    author: str | None = Field(
        default=None,
        description="Author of the book.",
    )

    publication_date: str | None = Field(
        default=None,
        description="Publication date of the book.",
    )

    isbn: str | None = Field(
        default=None,
        description="ISBN of the book.",
    )

    description: str | None = Field(
        default=None,
        description="Brief description or summary of the book.",
    )

class EnrichedBook(BookInput):
    """Book information enriched by the system."""

    source: str