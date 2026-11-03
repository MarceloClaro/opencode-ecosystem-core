"""Demonstração local autorizada R920–R923: fixture, cópia inerte e diagnósticos.

Executa motores locais determinísticos, não LLMs/treino, e não altera permissões.
Cache de plugins é explícito; ausência de licença impede cópia e é relatada.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from academic.adversarial_research.service import _write_json
from academic.adversarial_research.simulation import STAGES, SCENARIOS, render_simulation_report
from marceloclaro.orchestrator import MarceloClaroOrchestrator

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin-cache', default='/mnt/c/Users/marce/.codex/plugins/cache')
    args = parser.parse_args(argv)
    output = ROOT / 'outputs/core-r923'
    primary = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
    project = {'research_id': 'didactic-r920', 'spec_id': 'SPEC-935-R920',
        'artifact_path': str(ROOT / 'examples/academic-simulation-r920/protocol.md'),
        'problem': 'Como documentar interpretações rivais no protocolo didático?',
        'objectives': ['Ensaiar perguntas e evidências exigidas; não inferir resultados empíricos.'],
        'study_type': 'qualitative', 'context': {'humans': False, 'personal_data': False},
        'sources': [], 'claims': [{'claim_id': 'c1',
            'statement': 'Conclusões uniformes podem ser contestadas por casos negativos — exemplo hipotético.',
            'claim_type': 'inferential', 'source_refs': [], 'evidence_status': 'contradicted',
            'limitations': ['Fixture didática sem dados ou fontes empíricas.'],
            'reviewer_agent_ids': [], 'attributes': {}}]}
    cases = [{'case_id': f'{stage}-{scenario}', 'stage': stage, 'scenario': scenario,
        'group': 'cientistas_metodo' if stage == 'metodologia' else
                 'cientistas_resultados' if stage in {'analise', 'resultados'} else 'banca_interdisciplinar',
        'rounds': 2, 'agents': 6} for stage in STAGES for scenario in SCENARIOS]
    plan = primary.academic_rigor_action({'operation': 'simulation_plan', 'project': project,
        'cases': cases, 'seed': 42, 'limits': {'max_rounds': 64, 'max_actions': 512, 'timeout_seconds': 30}})
    academic = primary.academic_rigor_action({'operation': 'simulation_run', 'plan': plan})
    repeated = primary.academic_rigor_action({'operation': 'simulation_run', 'plan': plan})
    _write_json(output / 'academic-plan.json', plan)
    _write_json(output / 'academic-simulation.json', academic)
    (output / 'academic-simulation.md').write_text(render_simulation_report(academic), encoding='utf-8')
    ids = ['zotero', 'sequence-viewer']
    try:
        inventory = primary.scientific_plugin_action('inventory_local', cache_root=args.plugin_cache, plugin_ids=ids)
    except (OSError, ValueError) as exc:
        inventory = {'status': 'blocked', 'reason_type': type(exc).__name__, 'reason_code': str(exc)[:100],
                     'scope': 'explicit_catalogued_packages', 'executed': False}
    try:
        extraction = primary.scientific_plugin_action('extract_selected', cache_root=args.plugin_cache, plugin_ids=ids)
    except (OSError, ValueError) as exc:
        extraction = {'status': 'blocked', 'reason_type': type(exc).__name__, 'reason_code': str(exc)[:100],
                      'scope': 'explicit_catalogued_packages', 'executed': False}
    _write_json(output / 'local-plugin-inventory.json', inventory)
    _write_json(output / 'local-plugin-extraction.json', extraction)
    fine_plan = primary.itsfine_action({'operation': 'plan', 'run_id': 'r923-diagnostic'})
    fine = primary.itsfine_action({'operation': 'run', 'plan': fine_plan})
    _write_json(output / 'itsfine-plan.json', fine_plan)
    _write_json(output / 'itsfine-diagnostics.json', fine)
    summary = {'kind': 'local_demonstration_not_scientific_validation',
        'academic': {'status': academic['status'], 'usage': academic['usage'],
            'stages': len(STAGES), 'scenarios': len(SCENARIOS),
            'review_status': academic['base_review']['review_status'],
            'unresolved_objections': len(academic['unresolved_objection_ids']),
            'trajectory_sha256': academic['trajectory_sha256'],
            'deterministic_replay_matches': academic['trajectory_sha256'] == repeated['trajectory_sha256']},
        'plugins': {'status': extraction['status'],
            'imported_ids': [p['id'] for p in extraction.get('plugins', [])],
            'reference_only': [{'id': p['id'], 'reason_codes': p['reason_codes']}
                               for p in extraction.get('reference_only', [])]},
        'itsfine': {k: fine.get(k) for k in ('status', 'steps_executed', 'processes_executed',
            'next_skill', 'training_executed', 'inference_executed', 'policy_modified')},
        'externally_validated': False, 'human_review_required': True}
    _write_json(output / 'demonstration-summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
