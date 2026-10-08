import time, requests, json

url = 'http://127.0.0.1:11434/api/chat'

def ask_gemma(prompt):
    payload = {
        'model': 'gemma4:e4b',
        'messages': [
            {'role': 'system', 'content': 'Clinical intake assistant. Output JSON with key and is_complete.'},
            {'role': 'user', 'content': prompt}
        ],
        'options': {'temperature': 0.1, 'num_predict': 40},
        'format': 'json',
        'think': False,
        'stream': False
    }
    t0 = time.perf_counter()
    r = requests.post(url, json=payload, timeout=20)
    dur = time.perf_counter() - t0
    return r.json().get('message', {}).get('content'), dur

# Test A: Fever initial turn
prompt_a = """Patient complaint: fever
Collected details: none
Candidate questions:
- fever_duration: How many days have you had the fever?
- fever_pattern: Does the fever stay constant or come and go?
- fever_associated: Along with the fever, do you have chills or body pain?

Select the single most important next question. Return JSON:
{"key": "<candidate_key>", "is_complete": false}"""

res_a, t_a = ask_gemma(prompt_a)
print(f"Test A took {t_a:.2f}s: {res_a}")

# Test B: Fever after duration and associated known
prompt_b = """Patient complaint: fever
Collected details: duration: 3 days; associated: chills and body pain; pattern: continuous
Candidate questions:
- fever_exposure: Have you travelled recently or been around someone with a similar illness?

If enough clinical information is gathered for doctor review, set is_complete: true and key: null.
Return JSON:
{"key": "<candidate_key_or_null>", "is_complete": true_or_false}"""

res_b, t_b = ask_gemma(prompt_b)
print(f"Test B took {t_b:.2f}s: {res_b}")

# Test C: Tamil input
prompt_c = """Patient complaint: எனக்கு வயிற்று வலி இருக்கு (stomach pain)
Collected details: none
Candidate questions:
- abd_duration: எத்தனை நாட்களாக வயிற்று வலி இருக்கிறது?
- abd_location: வயிற்றின் எந்த பகுதியில் வலி இருக்கிறது?
- abd_vomit_stool: வாந்தி அல்லது வயிற்றுப்போக்கு இருக்கிறதா?

Select the single most important next question. Return JSON:
{"key": "<candidate_key>", "is_complete": false}"""

res_c, t_c = ask_gemma(prompt_c)
print(f"Test C took {t_c:.2f}s: {res_c}")
