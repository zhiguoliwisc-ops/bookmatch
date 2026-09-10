from bookmatch.models.candidate_evidence import (
    CandidateEvidence,
)


def test_candidate_evidence_stores_series_information() -> None:
    evidence = CandidateEvidence(
        series_title="A Girl Called Echo",
        volume_number=1,
        author="Katherena Vermette",
    )

    assert evidence.series_title == "A Girl Called Echo"
    assert evidence.volume_number == 1
    assert evidence.author == "Katherena Vermette"


def test_candidate_evidence_allows_missing_series_information() -> None:
    evidence = CandidateEvidence(
        series_title=None,
        volume_number=None,
        author="Katherena Vermette",
    )

    assert evidence.series_title is None
    assert evidence.volume_number is None
    assert evidence.author == "Katherena Vermette"


def test_candidate_evidence_stores_canonical_title() -> None:
    evidence = CandidateEvidence(
        series_title="A Girl Called Echo",
        volume_number=1,
        author="Katherena Vermette",
        canonical_title="Pemmican Wars",
    )

    assert evidence.canonical_title == "Pemmican Wars"