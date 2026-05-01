"""Phase 7: IEEE Submission Checklist Verification."""
import re, os

tex_path = r'd:\Daa-2\research\paper\paper.tex'
bib_path = r'd:\Daa-2\research\paper\references.bib'

with open(tex_path, 'r', encoding='utf-8') as f:
    tex = f.read()
with open(bib_path, 'r', encoding='utf-8') as f:
    bib = f.read()

print('=' * 60)
print('PHASE 7: IEEE SUBMISSION CHECKLIST')
print('=' * 60)

# 1. IEEEtran class
print('[PASS] IEEEtran.cls' if 'IEEEtran' in tex else '[FAIL] NOT IEEEtran')

# 2. Author details
for label, text in [('Author name', 'Purushotham Prajapati'), ('Affiliation', 'VNRVJIET'), ('Email', 'purushothamprajapati7473@gmail.com')]:
    print(f'[PASS] {label}' if text in tex else f'[FAIL] {label} MISSING')

# 3. Abstract word count
m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.DOTALL)
if m:
    wc = len(m.group(1).split())
    print(f'[{"PASS" if wc <= 200 else "WARN"}] Abstract: ~{wc} words (target <= 200)')

# 4. Citation integrity
cite_keys = set()
for group in re.findall(r'\\cite\{([^}]+)\}', tex):
    for k in group.split(','):
        cite_keys.add(k.strip())
bib_keys = set(re.findall(r'@\w+\{(\w+)', bib))
missing = cite_keys - bib_keys
if missing:
    print(f'[FAIL] Missing BibTeX entries: {missing}')
else:
    print(f'[PASS] All {len(cite_keys)} citation keys found in references.bib')

# 5. Figures
figs = re.findall(r'\\includegraphics.*?\{([^}]+)\}', tex)
print(f'[INFO] {len(figs)} figures referenced')
for fig in figs:
    path = os.path.join(r'd:\Daa-2\research\paper', fig)
    if os.path.exists(path):
        sz = os.path.getsize(path)
        print(f'  [PASS] {fig} ({sz:,} bytes)')
    else:
        print(f'  [FAIL] {fig} NOT FOUND')

# 6. Structure
sections = re.findall(r'\\section\{([^}]+)\}', tex)
print(f'[INFO] {len(sections)} sections: {", ".join(sections)}')
eqs = len(re.findall(r'\\begin\{equation\}', tex))
thms = len(re.findall(r'\\begin\{theorem\}', tex))
proofs = len(re.findall(r'\\begin\{proof\}', tex))
print(f'[INFO] {eqs} equations, {thms} theorems, {proofs} proofs')

# 7. Placeholders
for p in ['TODO', 'FIXME', 'XXX', 'University Name', 'email@institution', 'City, Country']:
    if p in tex:
        print(f'[FAIL] Placeholder found: "{p}"')
    else:
        print(f'[PASS] No placeholder: "{p}"')

# 8. Keywords
if 'IEEEkeywords' in tex:
    print('[PASS] IEEE keywords present')

# 9. Bibliography
if '\\bibliography{references}' in tex:
    print('[PASS] Bibliography linked')
if '\\bibliographystyle{IEEEtran}' in tex:
    print('[PASS] IEEE bibliography style')

print('=' * 60)
print('CHECKLIST COMPLETE')
