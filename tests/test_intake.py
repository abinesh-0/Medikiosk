def test_questions():
    from services.ai.question_engine import get_questions
    assert len(get_questions("NORMAL")) >= 5
    assert len(get_questions("AYUSH")) >= 10
