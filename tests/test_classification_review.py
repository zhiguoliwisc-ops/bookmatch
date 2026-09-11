from bookmatch.models.classification_review import (
    ClassificationReview,
    ReviewDecision,
)


def test_classification_review_model() -> None:
    review = ClassificationReview(
        decision=ReviewDecision.APPROVED,
        confidence=0.95,
        reason="The classification is consistent with the book evidence.",
    )

    assert review.decision == ReviewDecision.APPROVED
    assert review.confidence == 0.95
    assert (
        review.reason
        == "The classification is consistent with the book evidence."
    )