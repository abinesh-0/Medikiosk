def test_ocr_import():
    from services.ocr.ocr_engine import extract
    assert callable(extract)
