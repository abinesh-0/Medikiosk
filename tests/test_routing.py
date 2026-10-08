def test_route():
    from services.routing.department_router import recommend
    assert recommend("knee pain")[0]=="Orthopaedics"
