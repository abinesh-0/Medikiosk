import sys
sys.path.insert(0, r'a:\MediKiosk')
sys.stdout.reconfigure(encoding='utf-8')
from services.ai.question_engine import BRANCHES, AYUSH_BRANCHES

for src_name, src in (('NORMAL', BRANCHES), ('AYUSH', AYUSH_BRANCHES)):
    for name, _, qs in src:
        for q in qs:
            opts = q.get('options', [])
            if opts:
                print(f"{src_name}/{name}/{q['key']}: {opts}")
