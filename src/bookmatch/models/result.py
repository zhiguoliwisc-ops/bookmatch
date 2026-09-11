from pydantic import BaseModel

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.classification_review import ClassificationReview


class BookMatchResult(BaseModel):
    book: EnrichedBook
    classification: BookClassification
    review: ClassificationReview | None = None