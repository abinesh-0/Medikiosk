def test_extractor():
    from services.ai.clinical_extractor import extract
    assert extract("fever and cough")["department"] in ("Pulmonology","General Medicine")
