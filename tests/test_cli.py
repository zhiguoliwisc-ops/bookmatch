from unittest.mock import Mock, patch
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.models.result import BookMatchResult
from bookmatch.services.exceptions import AmbiguousBookError

from bookmatch.models.book import EnrichedBook
from bookmatch.cli import select_book_from_candidates

from bookmatch.cli import (
    run_cli,
    select_book_from_candidates,
)

from bookmatch.models.classification_review import (
    ClassificationReview,
    ReviewDecision,
)

def create_book(
    title: str,
    author: str,
) -> EnrichedBook:
    return EnrichedBook(
        title=title,
        author=author,
        publication_date="2020",
        isbn=None,
        description="Test description.",
        source="Test",
    )


def test_select_book_from_candidates_returns_selected_book() -> None:
    candidates = [
        create_book("Dog Man", "Dav Pilkey"),
        create_book("Dog Man", "Maurice Procter"),
    ]

    with patch(
        "builtins.input",
        return_value="1",
    ):
        result = select_book_from_candidates(candidates)

    assert result == candidates[0]


def test_select_book_from_candidates_selects_second_book() -> None:
    candidates = [
        create_book("Dog Man", "Dav Pilkey"),
        create_book("Dog Man", "Maurice Procter"),
    ]

    with patch(
        "builtins.input",
        return_value="2",
    ):
        result = select_book_from_candidates(candidates)

    assert result == candidates[1]

'''
from bookmatch.models.classification import (
    BookClassification,
    ReadingDifficulty,
    AgeGroup,
)
from bookmatch.models.result import BookMatchResult
from bookmatch.services.exceptions import AmbiguousBookError

def test_cli_resolves_ambiguous_book_with_user_selection() -> None:
    candidates = [
        create_book("Dog Man", "Dav Pilkey"),
        create_book("Dog Man", "Maurice Procter"),
    ]

    selected_book = candidates[0]

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Graphic Novel",
        confidence=0.9,
    )

    workflow = Mock()

    workflow.run.side_effect = AmbiguousBookError(
        "Multiple possible books were found.",
        candidates=candidates,
    )

    workflow.classify_book.return_value = classification

    with patch(
        "bookmatch.cli.input",
        return_value="1",
    ):
        # This test will initially fail because the CLI entry point
        # does not yet expose this behavior.
        ...

'''

def test_run_cli_handles_ambiguous_book() -> None:
    candidates = [
        create_book("Dog Man", "Dav Pilkey"),
        create_book("Dog Man", "Maurice Procter"),
    ]

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Graphic Novel",
        confidence=0.9,
    )

    review = ClassificationReview(
        decision=ReviewDecision.APPROVED,
        confidence=0.95,
        reason="The classification is consistent with the book evidence.",
    )

    workflow = Mock()

    workflow.run.side_effect = AmbiguousBookError(
        "Multiple possible books were found.",
        candidates=candidates,
    )

    workflow.classify_book.return_value = classification
    workflow.review_book.return_value = review

    with patch(
        "bookmatch.cli.input",
        side_effect=[
            "Dog Man",
            "",
            "",
            "1",
        ],
    ):
        run_cli(workflow)

    workflow.run.assert_called_once()
    workflow.classify_book.assert_called_once_with(
        candidates[0]
    )
    workflow.review_book.assert_called_once_with(
        candidates[0],
        classification,
    )
def test_run_cli_displays_review(
    monkeypatch,
    capsys,
) -> None:
    workflow = Mock()

    workflow.run.return_value = BookMatchResult(
        book=EnrichedBook(
            title="Dog Man",
            author="Dav Pilkey",
            publication_date="2016",
            isbn="1338611941",
            description="A graphic novel about a dog-headed police officer.",
            source="Test",
        ),
        classification=BookClassification(
            recommended_age_group=AgeGroup.ELEMENTARY,
            minimum_age=6,
            maximum_age=10,
            reading_difficulty=ReadingDifficulty.EASY,
            genre="Graphic Novel",
            confidence=0.9,
        ),
        review=ClassificationReview(
            decision=ReviewDecision.APPROVED,
            confidence=0.95,
            reason="The classification is consistent with the book evidence.",
        ),
    )

    monkeypatch.setattr(
        "builtins.input",
        Mock(
            side_effect=[
                "Dog Man",
                "Dav Pilkey",
                "",
            ]
        ),
    )

    run_cli(workflow)

    output = capsys.readouterr().out

    assert "Review decision: approved" in output