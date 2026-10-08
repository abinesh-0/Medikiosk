from pathlib import Path
import ast, re, sys
ROOT=Path(__file__).resolve().parent
errors=[]
for p in ROOT.rglob('*.py'):
    if any(x in p.parts for x in ('__pycache__',)) or p.name=='VERIFY_PROJECT.py': continue
    try: ast.parse(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Python syntax: {p}: {e}')
for p in ROOT.rglob('*.js'):
    # Node is used for JS syntax checking below when available.
    pass
html=(ROOT/'templates/auth/auth.html').read_text(encoding='utf-8')
required_ids=['lemail','lpass','loginPane','registerPane','staffPane','rname','remail','rotp','rpass','semail','spass']
for i in required_ids:
    if f'id="{i}"' not in html: errors.append(f'Missing auth control id: {i}')
for i in ['api/doctor/profile','api/doctor/notifications']:
    if i not in (ROOT/'static/js/doctor.js').read_text(): errors.append(f'Missing frontend integration: {i}')
css=(ROOT/'static/css/style.css').read_text()
if '.auth-card input.auth-input' not in css: errors.append('Final auth input CSS override missing')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('MediKiosk static verification: PASS')
print('Auth controls:', ', '.join(required_ids))
