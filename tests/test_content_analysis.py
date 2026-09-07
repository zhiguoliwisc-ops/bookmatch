from bookmatch.models.content_analysis import BookContentAnalysis


def test_create_book_content_analysis():
    analysis = BookContentAnalysis(
        themes=["friendship", "loss"],
        subject_maturity=2,
        emotional_complexity=3,
        conceptual_complexity=2,
        sensitive_topics=["death"],
        summary="A story about friendship and loss.",
    )

    assert analysis.themes == ["friendship", "loss"]
    assert analysis.subject_maturity == 2
    assert analysis.emotional_complexity == 3
    assert analysis.conceptual_complexity == 2
    assert analysis.sensitive_topics == ["death"]
    assert analysis.summary == "A story about friendship and loss."
    