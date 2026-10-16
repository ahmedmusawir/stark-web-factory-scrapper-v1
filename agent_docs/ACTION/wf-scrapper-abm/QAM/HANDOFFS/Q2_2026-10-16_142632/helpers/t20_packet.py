"""Q2 T-20 instrument: build the sanitized consumer packet for the fresh cold reader.

Executor: Claudy (Claude Code, Claude Opus 5.5).
Packet = the two accepted reviewed packages (v01, Growth Call reviewed) + every
saved reference they require (T-19's independently enumerated set, minus the
unreferenced helper script) copied from the verified snapshot, plus QUESTIONS.md
whose question text is extracted from the approved plan bytes (not retyped) and a
neutral README. Excludes .runtime, lane/QA material and helper code. Writes the
packet manifest; the checker is run separately on it. argv[1] = result JSON.
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

SNAP = Path('/tmp/opencode/q2-scratch-20261016/snapshot-scoped')
DELIVERY = Path('/tmp/opencode/q2-scratch-20261016/delivery-t19')
PACKET = Path('/tmp/opencode/q2-scratch-20261016/t20/packet')
LANE = Path(__file__).resolve().parents[1]
PLAN = LANE.parent/'WebFactory_Q1_Lead_Review_2026-10-15/01_QAM_TEST_PLAN_FINAL.md'
EXCLUDE = {'agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    t19 = json.loads((LANE/'offline/t19_result.json').read_text())
    delivered = sorted(p.relative_to(DELIVERY).as_posix() for p in DELIVERY.rglob('*') if p.is_file())
    files = [f for f in delivered if f not in EXCLUDE]
    PACKET.mkdir(parents=True, exist_ok=False)
    mismatches = []
    for rel in files:
        src = SNAP/rel
        if src.read_bytes() != (DELIVERY/rel).read_bytes():
            mismatches.append(rel)
        (PACKET/rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, PACKET/rel)
    plan_text = PLAN.read_text(encoding='utf-8')
    qline = next(ln for ln in plan_text.splitlines() if ln.startswith('Questions: (1)'))
    questions = [q.strip() for q in re.split(r'\(\d\)\s', qline[len('Questions: '):]) if q.strip()]
    rubric = next(ln for ln in plan_text.splitlines() if ln.startswith('Rubric: '))
    (PACKET/'QUESTIONS.md').write_text(
        '# Consumer questions\n\nAnswer each question using ONLY the files in this packet. Cite file paths '
        '(and source IDs, capture dates, CSS boundaries and sha256 values where relevant). Label interpretations '
        'as interpretations. If something cannot be known from the packet, say so and cite the relevant gap.\n\n'
        + ''.join(f'{i}. {q}\n' for i, q in enumerate(questions, 1)))
    (PACKET/'README.md').write_text(
        '# Consumer packet\n\nTwo prepared website-research packages and the saved source files they reference, '
        'in their original relative layout. Entry points:\n\n'
        '- `outputs/prepared/CyberizeGroup-first-selected-2026-10-11_210309-v01/ARCHITECT_BRIEF.md`\n'
        '- `outputs/prepared/CyberizeGroup-growth-call-follow-up-2026-10-13_223736-reviewed/ARCHITECT_BRIEF.md`\n\n'
        'Each package has a SOURCE_INDEX.json listing its source files and their sha256 values. Saved URLs are data '
        'only; nothing here should be fetched. Questions are in QUESTIONS.md.\n')
    manifest = {'members': {p.relative_to(PACKET).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
                            for p in sorted(PACKET.rglob('*')) if p.is_file()}}
    (PACKET.parent/'packet.manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    result = {'test': 'T-20 packet', 'executor': 'Claudy (Claude Code, Claude Opus 5.5)',
              'instrument_sha256': sha(Path(__file__).read_bytes()), 'packet': str(PACKET),
              't19_reference_count': t19.get('independent_reference_count'),
              'reference_files_copied': len(files), 'excluded': sorted(EXCLUDE),
              'snapshot_vs_t19_delivery_mismatches': mismatches,
              'questions_extracted_from_plan': questions, 'plan_sha256': sha(PLAN.read_bytes()),
              'rubric_line_from_plan': rubric, 'manifest': manifest,
              'packet_total_files': len(manifest['members'])}
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'files': len(manifest['members']), 'questions': len(questions), 'mismatches': mismatches}))
    return 0 if len(questions) == 8 and not mismatches else 1


if __name__ == '__main__':
    sys.exit(main())
