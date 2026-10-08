import time, requests, json

url = 'http://127.0.0.1:11434/api/chat'

def query_gemma(user_prompt):
    payload = {
        'model': 'gemma4:e4b',
        'messages': [
            {'role': 'system', 'content': 'Clinical intake assistant. Select ONE next question key or mark complete.'},
            {'role': 'user', 'content': user_prompt}
        ],
        'options': {'temperature': 0.1, 'num_predict': 35},
        'format': 'json',
        'think': False,
        'stream': False
    }
    t0 = time.perf_counter()
    r = requests.post(url, json=payload, timeout=30)
    ms = (time.perf_counter() - t0)
    return r.json().get('message', {}).get('content'), ms

# Case 1: Fever
p1 = '''Complaint: fever. Known: none. Missing: duration, chills, cough.
Candidates:
- fever_duration: How many days have you had the fever?
- fever_pattern: Does the fever stay constant or come and go?
- fever_associated: Along with the fever, do you have chills or body pain?

Select the most relevant next question. Return JSON: {"key": "selected_key", "is_complete": false}'''
res, t = query_gemma(p1)
print(f"Case 1 (Fever) took {t:.2f}s: {res}")

# Case 2: Stomach pain
p2 = '''Complaint: stomach pain. Known: none. Missing: duration, location, severity, onset.
Candidates:
- abd_duration: How many days have you had the stomach pain?
- abd_location: Which part of your abdomen hurts?
- abd_character: Is the pain burning, cramping, or sharp?
- abd_vomit_stool: Do you have vomiting or loose stools with it?

Select the most relevant next question. Return JSON: {"key": "selected_key", "is_complete": false}'''
res, t = query_gemma(p2)
print(f"Case 2 (Stomach pain) took {t:.2f}s: {res}")

# Case 3: Headache for 2 days
p3 = '''Complaint: headache for 2 days. Known: duration = 2 days, location = head. Missing: onset, character, associated symptoms.
Candidates:
- head_onset: Did the headache start suddenly or gradually?
- head_character: Is the headache throbbing, dull, or band-like?
- head_vision: Do you have vision changes, nausea, or sensitivity to light?
- fever_duration: How many days have you had the fever?

Select the most relevant next question. Return JSON: {"key": "selected_key", "is_complete": false}'''
res, t = query_gemma(p3)
print(f"Case 3 (Headache for 2 days) took {t:.2f}s: {res}")
