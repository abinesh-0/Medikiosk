def test_red_flag():
    from services.triage.red_flag_engine import detect, highest
    flags=detect("I have chest pain and severe breathing difficulty")
    assert flags
    assert highest(flags) in ("HIGH","URGENT")
