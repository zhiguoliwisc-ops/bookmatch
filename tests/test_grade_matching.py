import pytest

from bookmatch.batch.grade_matching import (
    AgeAlignment,
    age_group_alignment,
    age_group_matches,
    age_range_alignment,
    age_range_matches,
    expected_age_group,
    grade_range_to_age_range,
    parse_grade_range,
)
from bookmatch.models.classification import AgeGroup


@pytest.mark.parametrize(
    ("suggested_grades", "expected"),
    [
        ("1st Grade", (1, 1)),
        ("6th–8th Grade", (6, 8)),
        ("9th–10th Grade", (9, 10)),
        ("11th–12th Grade", (11, 12)),
        ("10th Grade", (10, 10)),
        ("11th Grade", (11, 11)),
        (
            "9th–10th Grade; 11th–12th Grade",
            (9, 12),
        ),
    ],
)
def test_parse_grade_range(
    suggested_grades: str,
    expected: tuple[int, int],
) -> None:
    assert parse_grade_range(suggested_grades) == expected


def test_parse_grade_range_rejects_unsupported_format() -> None:
    with pytest.raises(ValueError):
        parse_grade_range("Kindergarten")


@pytest.mark.parametrize(
    ("suggested_grades", "expected"),
    [
        ("1st Grade", (6, 7)),
        ("6th–8th Grade", (11, 14)),
        ("9th–10th Grade", (14, 16)),
        ("11th–12th Grade", (16, 18)),
        ("10th Grade", (15, 16)),
        ("11th Grade", (16, 17)),
        (
            "9th–10th Grade; 11th–12th Grade",
            (14, 18),
        ),
    ],
)
def test_grade_range_to_age_range(
    suggested_grades: str,
    expected: tuple[int, int],
) -> None:
    assert grade_range_to_age_range(suggested_grades) == expected


@pytest.mark.parametrize(
    (
        "suggested_grades",
        "minimum_age",
        "maximum_age",
        "expected",
    ),
    [
        ("1st Grade", 6, 7, True),
        ("6th–8th Grade", 11, 14, True),
        ("9th–10th Grade", 14, 16, True),
        ("11th–12th Grade", 16, 18, True),
        ("6th–8th Grade", 10, 12, True),
        ("9th–10th Grade", 13, 15, True),
        ("1st Grade", 8, 10, False),
        ("6th–8th Grade", 6, 10, False),
        ("9th–10th Grade", 6, 12, False),
        ("11th–12th Grade", 10, 15, False),
        (
            "9th–10th Grade; 11th–12th Grade",
            14,
            18,
            True,
        ),
    ],
)
def test_age_range_matches(
    suggested_grades: str,
    minimum_age: int,
    maximum_age: int,
    expected: bool,
) -> None:
    assert (
        age_range_matches(
            suggested_grades,
            minimum_age,
            maximum_age,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("suggested_grades", "expected"),
    [
        ("1st Grade", AgeGroup.ELEMENTARY),
        ("6th–8th Grade", AgeGroup.MIDDLE_SCHOOL),
        ("9th–10th Grade", AgeGroup.HIGH_SCHOOL),
        ("11th–12th Grade", AgeGroup.HIGH_SCHOOL),
        (
            "9th–10th Grade; 11th–12th Grade",
            AgeGroup.HIGH_SCHOOL,
        ),
        ("10th Grade", AgeGroup.HIGH_SCHOOL),
        ("11th Grade", AgeGroup.HIGH_SCHOOL),
    ],
)
def test_expected_age_group(
    suggested_grades: str,
    expected: AgeGroup,
) -> None:
    assert expected_age_group(suggested_grades) == expected


@pytest.mark.parametrize(
    (
        "suggested_grades",
        "age_group",
        "expected",
    ),
    [
        ("1st Grade", AgeGroup.ELEMENTARY, True),
        ("6th–8th Grade", AgeGroup.MIDDLE_SCHOOL, True),
        ("9th–10th Grade", AgeGroup.HIGH_SCHOOL, True),
        ("11th–12th Grade", AgeGroup.HIGH_SCHOOL, True),
        (
            "9th–10th Grade; 11th–12th Grade",
            AgeGroup.HIGH_SCHOOL,
            True,
        ),
        ("1st Grade", AgeGroup.MIDDLE_SCHOOL, False),
        ("6th–8th Grade", AgeGroup.ELEMENTARY, False),
        ("9th–10th Grade", AgeGroup.MIDDLE_SCHOOL, False),
        ("11th–12th Grade", AgeGroup.ELEMENTARY, False),
    ],
)
def test_age_group_matches(
    suggested_grades: str,
    age_group: AgeGroup,
    expected: bool,
) -> None:
    assert (
        age_group_matches(
            suggested_grades,
            age_group,
        )
        == expected
    )


@pytest.mark.parametrize(
    (
        "suggested_grades",
        "age_group",
        "expected",
    ),
    [
        (
            "1st Grade",
            AgeGroup.PRESCHOOL,
            AgeAlignment.LOWER,
        ),
        (
            "1st Grade",
            AgeGroup.ELEMENTARY,
            AgeAlignment.ALIGNED,
        ),
        (
            "1st Grade",
            AgeGroup.MIDDLE_SCHOOL,
            AgeAlignment.HIGHER,
        ),
        (
            "6th–8th Grade",
            AgeGroup.ELEMENTARY,
            AgeAlignment.LOWER,
        ),
        (
            "6th–8th Grade",
            AgeGroup.MIDDLE_SCHOOL,
            AgeAlignment.ALIGNED,
        ),
        (
            "6th–8th Grade",
            AgeGroup.HIGH_SCHOOL,
            AgeAlignment.HIGHER,
        ),
    ],
)
def test_age_group_alignment(
    suggested_grades: str,
    age_group: AgeGroup,
    expected: AgeAlignment,
) -> None:
    assert (
        age_group_alignment(
            suggested_grades,
            age_group,
        )
        == expected
    )


@pytest.mark.parametrize(
    (
        "suggested_grades",
        "minimum_age",
        "maximum_age",
        "expected",
    ),
    [
        (
            "1st Grade",
            3,
            5,
            AgeAlignment.LOWER,
        ),
        (
            "1st Grade",
            6,
            7,
            AgeAlignment.ALIGNED,
        ),
        (
            "1st Grade",
            5,
            8,
            AgeAlignment.ALIGNED,
        ),
        (
            "1st Grade",
            8,
            10,
            AgeAlignment.HIGHER,
        ),
        (
            "6th–8th Grade",
            6,
            10,
            AgeAlignment.LOWER,
        ),
        (
            "6th–8th Grade",
            11,
            14,
            AgeAlignment.ALIGNED,
        ),
        (
            "6th–8th Grade",
            13,
            16,
            AgeAlignment.ALIGNED,
        ),
        (
            "6th–8th Grade",
            15,
            18,
            AgeAlignment.HIGHER,
        ),
    ],
)
def test_age_range_alignment(
    suggested_grades: str,
    minimum_age: int,
    maximum_age: int,
    expected: AgeAlignment,
) -> None:
    assert (
        age_range_alignment(
            suggested_grades,
            minimum_age,
            maximum_age,
        )
        == expected
    )