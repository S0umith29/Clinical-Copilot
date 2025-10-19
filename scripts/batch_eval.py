import os, json, datetime
from copilot_engine import ClinicalQuestionCopilot

REPORT_DIR = 'reports'
INPUT_JSON = os.path.join(REPORT_DIR, 'questions_100.json')
OUTPUT_MD = os.path.join(REPORT_DIR, 'questions_100_v2.md')

os.makedirs(REPORT_DIR, exist_ok=True)

with open(INPUT_JSON) as f:
    data = json.load(f)
questions = [r['question'] for r in data['results']]

copilot = ClinicalQuestionCopilot()
rows = []
for q in questions:
    r = copilot.process_question(q, user_id='eval_v2')
    rows.append({
        'q': q,
        'conf': r.get('confidence', 0.0),
        'clinical': not r.get('guardrail_triggered', False),
        'sources': len(r.get('sources', []))
    })

total = len(rows)
overall_avg = round(sum(x['conf'] for x in rows)/total, 3)
clinical_rows = [x for x in rows if x['clinical']]
clinical_avg = round(sum(x['conf'] for x in clinical_rows)/max(len(clinical_rows),1), 3)
with_sources = sum(1 for x in rows if x['sources']>0)
clinical_with_sources = sum(1 for x in clinical_rows if x['sources']>0)

lines = []
lines.append('# ICU Clinical Questions Batch Report (v2)\n')
lines.append(f"Generated: {datetime.datetime.now().isoformat()}\n")
lines.append(f"Total questions: {total}\n")
lines.append(f"Clinical recognized: {len(clinical_rows)}\n")
lines.append(f"With sources (overall): {with_sources}\n")
lines.append(f"With sources (clinical): {clinical_with_sources}\n")
lines.append(f"Average confidence (overall): {overall_avg}\n")
lines.append(f"Average confidence (clinical only): {clinical_avg}\n")

lines.append('\n## Sample (first 10)\n')
for x in rows[:10]:
    lines.append(f"- clinical: {x['clinical']} | conf: {x['conf']:.2f} | sources: {x['sources']} | {x['q']}")

with open(OUTPUT_MD, 'w') as f:
    f.write('\n'.join(lines))

print('Wrote', OUTPUT_MD)
