import hashlib
def lookup(abha_id):
    if not abha_id: return None
    return {"abha_id":abha_id,"verified":True,"source":"MOCK_ABDM","message":"Prototype only; no real ABDM data accessed."}
def create_mock(identifier):
    return "91-" + hashlib.sha256(identifier.encode()).hexdigest()[:10]
