def test_health(client):
    r=client.get("/api/health"); assert r.status_code in (200,503)
