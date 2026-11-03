"""Executa checks selecionados e gates locais R923; não instala ou faz inferência."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from academic.adversarial_research.service import _write_json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs/core-r923'
TESTS = tuple('tests/' + name + '.py' for name in (
    'test_r583_mirofish_offline', 'test_r649_opencode_agent_sdk', 'test_r659_sdk_hooks_contract',
    'test_r670_scientific_plugins', 'test_r671_runtime_surfaces',
    'test_r879_architecture_maps', 'test_r879_architecture_contract', 'test_r879_architecture_page',
    'test_r881_mermaid_integral', 'test_r881_readme_flowcharts', 'test_r895_requested_plugins',
    'test_r913_component_plugins', 'test_r914_academic_rigor', 'test_r916_documentation_atlas',
    'test_r917_academic_orchestration', 'test_r918_ollama_context_reliability',
    'test_r919_core_gaps', 'test_r920_academic_simulation', 'test_r921_local_plugin_extraction',
    'test_r922_academic_plugin_integration', 'test_r923_itsfine_core'))


def command(name, argv, timeout=180):
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': '/tmp/opencode'}
    result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True,
                            text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    log = OUTPUT / (name + '.log')
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    return {'argv': argv, 'returncode': result.returncode,
            'log': str(log.relative_to(ROOT)),
            'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    receipt = command('documentation-receipt-refresh', [sys.executable, '-m', 'scripts.build_documentation_receipt'])
    if receipt['returncode']:
        print(json.dumps(receipt)); return 1
    tests = command('selected-tests', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
        '--junitxml=' + str(OUTPUT / 'selected-tests.xml'), *TESTS], timeout=300)
    cases = list(ET.parse(OUTPUT / 'selected-tests.xml').getroot().iter('testcase'))
    tests.update(collected=len(cases), failures=sum(c.find('failure') is not None for c in cases),
                 errors=sum(c.find('error') is not None for c in cases),
                 skipped=sum(c.find('skipped') is not None for c in cases), whole_repository_suite_run=False)
    checks = [command('architecture-check', [sys.executable, 'scripts/build_architecture_maps.py',
        '--root', str(ROOT), '--ref', 'HEAD', '--source', 'worktree', '--output', 'docs/architecture', '--check']),
        command('mermaid-check', [sys.executable, 'scripts/build_mermaid_architecture.py',
            '--inventory', 'docs/architecture/architecture-inventory.json', '--output', 'docs/architecture/dependencies.mmd',
            '--correspondence', 'docs/architecture/mermaid-correspondence.json', '--check']),
        command('readme-check', [sys.executable, 'scripts/sync_readme_flowcharts.py', '--check']),
        command('operational-docs-check', [sys.executable, 'scripts/reconcile_operational_docs.py', '--check']),
        command('documentation-receipt-check', [sys.executable, '-m', 'scripts.build_documentation_receipt', '--check']),
        command('itsfine-upstream-verify', [sys.executable, '.its-fine/bin/verify.py', '--root', str(ROOT)])]
    if tests['returncode'] or tests['failures'] or tests['errors'] or tests['skipped'] or any(c['returncode'] for c in checks):
        _write_json(OUTPUT / 'final-gates.json', {'status': 'blocked', 'tests': tests, 'checks': checks,
                    'externally_validated': False})
        print(json.dumps({'status': 'blocked', 'tests': tests, 'checks': checks}, ensure_ascii=False)); return 1
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from sdd.spec_engine import spec_registry, spec_verifier
    from sdd.tdd_runner import TDDRunner
    spec_registry.load_formal_specs()
    spec = spec_registry.get('SPEC-935-R923')
    if spec is None or not spec.evidence_contract_valid:
        raise RuntimeError('Contrato R923 inválido')
    evidence = TDDRunner().run_delivery_test(spec)
    gate = spec_verifier.verify(spec.spec_id, {'implementation': 'R919-R923'}, trusted_test_evidence=evidence)
    primary = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
    behavioral = asdict(primary.trust.execute('core.r923.local_delivery'))
    report = {'status': 'local_selected_checks_passed' if gate['verified'] and behavioral['allowed'] else 'blocked',
        'tests': tests, 'checks': checks, 'sdd': gate, 'behavioral_gate': behavioral,
        'externally_validated': False, 'scientific_validation': False,
        'limitations': ['Suíte selecionada, não suíte integral.', 'Gate comportamental local em shadow mode.',
                        'Revisão e métricas locais não comprovam qualidade científica ou desempenho de modelos.']}
    _write_json(OUTPUT / 'final-gates.json', report)
    if report['status'] == 'blocked':
        print(json.dumps({'status': 'blocked', 'sdd': gate, 'behavioral_gate': behavioral}, ensure_ascii=False)); return 1
    from mci.metabus import metabus
    failures = ['tdd_scope_and_history_attempts', 'external_review_blocked_or_usage_limit',
                'itsfine_bootstrap_timeout', 'lean_virtual_memory_regression']
    penalties = []
    # Contabilidade simbólica local, retrospectiva e explicitamente não financeira.
    for name in failures:
        task = 'r923-observed-' + name
        primary.economy.commit(primary.id, task, stake=10)
        penalties.append(primary.economy.resolve(task, success=False))
        primary.trust.learn(task, success=False, delta=0)
    confidence_before = metabus.memory.confidence_ledger.get(primary.id, 0.5)
    reflection = ('Falhas observadas foram preservadas: contrato TDD inválido ampliou indevidamente alvos; '
        'revisão externa sem leitura/limite não foi tratada como revisão; bootstrap silencioso exigiu '
        'deadline e diagnóstico; Lean 4.34.1 precisou de teto virtual 6 GiB mantendo heap limitado. '
        'Lição: validar contrato antes do runner, separar execução de mérito, usar escopo selecionado '
        'sem credenciais de irmãos e nunca aumentar permissões/treinar para fechar um checklist.')
    metabus.memory.add_reflection(primary.id, 'R923 observações e correções locais', reflection,
                                  score=min(confidence_before, 0.4))
    observation = metabus.memory.record_observation(primary.id, 'R919-R923 fechamento local',
        {'tests_passed': len(cases), 'sdd_verified': True, 'history': gate['red_history'],
         'confidence_promoted': False, 'externally_validated': False, 'scientific_validation': False})
    _write_json(OUTPUT / 'reflection.json', {'reflection': reflection, 'observation_id': observation,
        'confidence_before': confidence_before, 'confidence_after': metabus.memory.confidence_ledger.get(primary.id),
        'symbolic_slashing_retrospective': penalties, 'economy_scope': 'local_symbolic_no_real_currency',
        'confidence_promoted': False})
    artifacts = [*TESTS, 'integrations/itsfine_core.py', 'integrations/local_plugin_extraction.py',
        'integrations/opencode_agent_sdk.py', 'integrations/local_lean.py', 'integrations/scientific_plugins.py',
        'academic/adversarial_research/simulation.py', 'academic/adversarial_research/service.py',
        'marceloclaro/orchestrator.py', 'marceloclaro/runtime_actions.py', 'scripts/build_documentation_receipt.py',
        'scripts/demo_core_r923.py', 'scripts/finalize_core_r923.py', 'AGENTS.md', 'README.md',
        'docs/ITSFINE_CORE_R923.md', 'docs/MIROFISH_ACADEMICO_E_PLUGINS_R920.md',
        'docs/verification-documentation-r916-ollama-quantizacao.json',
        'outputs/core-r923/demonstration-summary.json', 'outputs/core-r923/final-gates.json',
        'outputs/core-r923/reflection.json', '.its-fine/install-manifest.json']
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in artifacts}
    _write_json(OUTPUT / 'artifact-hashes.json', {'sha256': hashes, 'externally_validated': False,
        'scope': 'selected_delivery_files_including_untracked_new_adapters_not_full_repository'})
    from evolution.cycles import EvolutionRegistry
    registry = EvolutionRegistry()
    if not any(c.round_id == 'R923' for c in registry.cycles):
        cycle = registry.record('R919–R923: bugs do Core, MiroFish acadêmico, plugins selecionados e ITS-FINE por composição',
            ['SDK e recibo corrigidos com RED→GREEN', '21 cenários sintéticos com revisão-base única',
             'Sequence Viewer instrucional importado; Zotero reference_only',
             'ITS-FINE 0.0.15 instalado e diagnósticos limitados executados',
             'Regressão Lean positiva/negativa fechada sob limites'], score=7.0,
            lessons=[reflection, 'Score 7 é heurística interna de processo, não avaliação científica/externa.'], round_id='R923')
        cycle.artifact_hashes = hashes
        cycle.evidence_trail = ['specs/SPEC-935-R923-itsfine-core.md', 'outputs/core-r923/final-gates.json']
        registry.save()
    from marceloclaro.doctor import run_doctor
    doctor = run_doctor()
    _write_json(OUTPUT / 'doctor-final.json', doctor)
    print(json.dumps({'status': report['status'], 'tests_passed': len(cases),
        'sdd_criteria': f"{gate['passed_count']}/{gate['total_count']}", 'history': gate['red_history'],
        'behavioral_allowed': behavioral['allowed'], 'doctor': doctor['overall'],
        'externally_validated': False}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
