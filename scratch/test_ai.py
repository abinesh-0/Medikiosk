import requests

res = requests.post(
    "http://127.0.0.1:5000/api/ai/doc-analyze",
    json={"text": "Patient Ramesh, 52 M. BP 150/95. Fasting Blood Glucose 180 mg/dL. Rx: Tab Metformin 500mg BD, Tab Telmisartan 40mg OD."}
)
print("Status:", res.status_code)
print("Analysis:", res.json())

res_chat = requests.post(
    "http://127.0.0.1:5000/api/ai/doc-chat",
    json={
        "message": "What do my medications do and is my sugar high?",
        "document_context": "Fasting Blood Glucose 180 mg/dL. Rx: Tab Metformin 500mg BD, Tab Telmisartan 40mg OD.",
        "language": "English"
    }
)
print("\nChat Status:", res_chat.status_code)
print("Chat Reply:", res_chat.json().get("reply", "")[:200])
