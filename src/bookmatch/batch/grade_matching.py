from __future__ import annotations

import re
from enum import Enum

from bookmatch.models.classification import AgeGroup


GRADE_AGE_RANGES = {
    "1st Grade": (6, 7),
    "6th–8th Grade": (11, 14),
    "9th–10th Grade": (14, 16),
    "11th–12th Grade": (16, 18),
    "10th Grade": (15, 16),
    "11th Grade": (16, 17),
}


class AgeAlignment(str, Enum):
    LOWER = "LOWER"
    ALIGNED = "ALIGNED"
    HIGHER = "HIGHER"


def parse_grade_range(
    suggested_grades: str,
) -> tuple[int, int]:
    """Convert a school-district grade recommendation to a grade range."""

    normalized = suggested_grades.strip()

    if normalized == "9th–10th Grade; 11th–12th Grade":
        return 9, 12

    match = re.fullmatch(
        r"(\d+)(?:st|nd|rd|th)–(\d+)(?:st|nd|rd|th) Grade",
        normalized,
    )

    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.fullmatch(
        r"(\d+)(?:st|nd|rd|th) Grade",
        normalized,
    )

    if match:
        grade = int(match.group(1))
        return grade, grade

    raise ValueError(
        f"Unsupported grade recommendation: {suggested_grades}"
    )


def grade_range_to_age_range(
    suggested_grades: str,
) -> tuple[int, int]:
    """Convert a school grade recommendation to an approximate age range."""

    first_grade, last_grade = parse_grade_range(suggested_grades)

    return first_grade + 5, last_grade + 6


def age_range_matches(
    suggested_grades: str,
    minimum_age: int,
    maximum_age: int,
) -> bool:
    """Return whether the BookMatch age range overlaps the school age range."""

    school_minimum_age, school_maximum_age = (
        grade_range_to_age_range(suggested_grades)
    )

    return (
        minimum_age <= school_maximum_age
        and maximum_age >= school_minimum_age
    )


def expected_age_group(
    suggested_grades: str,
) -> AgeGroup:
    """Return the BookMatch age group expected for a school grade recommendation."""

    first_grade, last_grade = parse_grade_range(suggested_grades)

    if last_grade <= 5:
        return AgeGroup.ELEMENTARY

    if first_grade >= 6 and last_grade <= 8:
        return AgeGroup.MIDDLE_SCHOOL

    if first_grade >= 9:
        return AgeGroup.HIGH_SCHOOL

    raise ValueError(
        f"Unsupported grade recommendation: {suggested_grades}"
    )


def age_group_matches(
    suggested_grades: str,
    age_group: AgeGroup,
) -> bool:
    """Return whether the BookMatch age group matches the school recommendation."""

    return expected_age_group(suggested_grades) == age_group


def age_group_alignment(
    suggested_grades: str,
    age_group: AgeGroup,
) -> AgeAlignment:
    """Compare a BookMatch age group with the school-list grade level."""

    expected_group = expected_age_group(suggested_grades)

    age_group_order = {
        AgeGroup.PRESCHOOL: 0,
        AgeGroup.EARLY_ELEMENTARY: 1,
        AgeGroup.ELEMENTARY: 2,
        AgeGroup.MIDDLE_SCHOOL: 3,
        AgeGroup.HIGH_SCHOOL: 4,
        AgeGroup.ADULT: 5,
    }

    expected_level = age_group_order[expected_group]
    actual_level = age_group_order[age_group]

    if actual_level < expected_level:
        return AgeAlignment.LOWER

    if actual_level > expected_level:
        return AgeAlignment.HIGHER

    return AgeAlignment.ALIGNED


def age_range_alignment(
    suggested_grades: str,
    minimum_age: int,
    maximum_age: int,
) -> AgeAlignment:
    """Compare a BookMatch age range with the school-list age proxy."""

    school_minimum_age, school_maximum_age = (
        grade_range_to_age_range(suggested_grades)
    )

    if maximum_age < school_minimum_age:
        return AgeAlignment.LOWER

    if minimum_age > school_maximum_age:
        return AgeAlignment.HIGHER

    return AgeAlignment.ALIGNED