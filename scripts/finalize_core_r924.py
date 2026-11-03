"""Fechamento R924–R926: efeitos confirmados e checks fixos, sem treino/modelos."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from academic.adversarial_research.service import _write_json
from integrations.itsfine_lifecycle import audit_distribution, run_bounded, _public_process
from scripts.finalize_core_r923 import TESTS as BASE_TESTS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs/core-r924'
TESTS = (*BASE_TESTS, 'tests/test_r924_itsfine_hardening.py',
    'tests/test_r925_managed_dependencies.py', 'tests/test_r926_itsfine_final_review.py',
    'tests/test_r839_tdd_history.py', 'tests/test_r839_red_delivery.py', 'tests/test_r839_verifier_delivery.py')


def command(name, argv, timeout=300):
    result = run_bounded(argv,cwd=ROOT,timeout_seconds=timeout,max_output_bytes=4*1024*1024)
    path = OUTPUT/(name+'.log')
    path.write_bytes(result['stdout']+result['stderr'])
    return {'argv':argv,**_public_process(result),'log':str(path.relative_to(ROOT)),
            'log_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    primary=MarceloClaroOrchestrator(auto_load_agents=False,pipeline_layers=1)
    archive=ROOT/'.its-fine/core/distributions/sandeco-itsfine-0.0.15.tgz'
    distribution=audit_distribution(archive)
    _write_json(OUTPUT/'distribution-audit.json',distribution)
    plan=primary.itsfine_action({'operation':'install_plan','archive_path':str(archive)})
    installation=primary.itsfine_action({'operation':'install','plan':plan,'confirm':True,'timeout_seconds':120})
    _write_json(OUTPUT/'installation-plan.json',plan)
    _write_json(OUTPUT/'installation.json',installation)
    if installation['status']!='installed_verified' or installation['policy_modified']:
        print(json.dumps({'status':'blocked','installation':installation})); return 1
    engines=primary.itsfine_action({'operation':'engines_status'})
    _write_json(OUTPUT/'engines-live.json',engines)
    if not all(row['dependencies_ready'] and row['cpu_probe_passed'] for row in engines['engines']):
        print(json.dumps({'status':'blocked','engines':engines})); return 1
    diagnostics=primary.itsfine_action({'operation':'run','plan':primary.itsfine_action({'operation':'plan','run_id':'r924-diagnostic'})})
    _write_json(OUTPUT/'diagnostics.json',diagnostics)
    from integrations.local_lean import LocalLeanVerifier
    lean=LocalLeanVerifier()
    probes={name:lean.verify(code) for name,code in {
        'positive':'theorem core_positive (n : Nat) : n = n := by rfl',
        'false':'theorem core_negative : (0 : Nat) = 1 := by rfl',
        'admission':'theorem core_admitted : False := sorryAx False true',
        'multiple':'theorem core_one : True := by trivial\ntheorem core_two : True := by trivial'}.items()}
    _write_json(OUTPUT/'lean-probes.json',probes)
    if not probes['positive']['is_valid'] or any(probes[k]['is_valid'] for k in ('false','admission','multiple')):
        print(json.dumps({'status':'blocked','reason':'lean_probe_failed'})); return 1
    refresh=command('documentation-receipt-refresh',[sys.executable,'-m','scripts.build_documentation_receipt'])
    if refresh['status']!='completed' or refresh['returncode']!=0:
        print(json.dumps({'status':'blocked','check':refresh})); return 1
    tests=command('selected-tests',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',
        '--junitxml='+str(OUTPUT/'selected-tests.xml'),*TESTS],timeout=480)
    cases=list(ET.parse(OUTPUT/'selected-tests.xml').getroot().iter('testcase'))
    tests.update(collected=len(cases),failures=sum(c.find('failure') is not None for c in cases),
        errors=sum(c.find('error') is not None for c in cases),skipped=sum(c.find('skipped') is not None for c in cases),
        whole_repository_suite_run=False)
    checks=[command('architecture-check',[sys.executable,'scripts/build_architecture_maps.py','--root',str(ROOT),
        '--ref','HEAD','--source','worktree','--output','docs/architecture','--check']),
        command('mermaid-check',[sys.executable,'scripts/build_mermaid_architecture.py','--inventory','docs/architecture/architecture-inventory.json',
            '--output','docs/architecture/dependencies.mmd','--correspondence','docs/architecture/mermaid-correspondence.json','--check']),
        command('readme-check',[sys.executable,'scripts/sync_readme_flowcharts.py','--check']),
        command('operational-docs-check',[sys.executable,'scripts/reconcile_operational_docs.py','--check']),
        command('receipt-check',[sys.executable,'-m','scripts.build_documentation_receipt','--check']),
        command('itsfine-core-verify',[sys.executable,'-m','marceloclaro.cli','itsfine','verify'])]
    if tests['status']!='completed' or tests['returncode']!=0 or tests['errors'] or tests['failures'] or tests['skipped'] or any(c['status']!='completed' or c['returncode']!=0 for c in checks):
        _write_json(OUTPUT/'final-gates.json',{'status':'blocked','tests':tests,'checks':checks})
        print(json.dumps({'status':'blocked','tests':tests,'checks':checks})); return 1
    from sdd.spec_engine import spec_registry,spec_verifier
    from sdd.tdd_runner import TDDRunner
    from sdd.tdd_history import TDDHistory
    spec_registry.load_formal_specs(); spec=spec_registry.get('SPEC-935-R926')
    if spec is None or not spec.evidence_contract_valid: raise RuntimeError('invalid_spec')
    evidence=TDDRunner().run_delivery_test(spec)
    gate=spec_verifier.verify(spec.spec_id,{'implementation':'R924–R926'},trusted_test_evidence=evidence)
    behavioral=asdict(primary.trust.execute('core.r926.local_delivery'))
    sources=TDDHistory()._sources()
    report={'status':'local_selected_checks_passed' if gate['verified'] and behavioral['allowed'] else 'blocked',
        'tests':tests,'checks':checks,'sdd':gate,'behavioral_gate':behavioral,
        'core_source_files':len(sources['files']),'dependency_trees':sources.get('dependency_trees',{}),
        'engines':engines['engines'],'upstream_tests_status':distribution['upstream_tests_status'],
        'upstream_tests_executed':False,'gpu_training_ready':all(r['training_ready'] for r in engines['engines']),
        'training_executed':False,'model_weights_downloaded':False,'externally_validated':False}
    _write_json(OUTPUT/'final-gates.json',report)
    if report['status']=='blocked':
        print(json.dumps({'status':'blocked','sdd':gate})); return 1
    from mci.metabus import metabus
    reflection=('R924–R926: dependências preparadas e sondadas em CPU não significam GPU disponível. '
        'Torchaudio 2.14.1 ausente foi recusado; par 2.11.0 CPU resolveu voz sem alterar Core. '
        'Suíte upstream não distribuída permaneceu not_shipped, nunca foi fabricada. '
        'Manifesto TDD de dependências migrou para árvore de cada byte fonte, não ignore list. '
        'Review foi convertido em testes; defaults de política e encerramento do grupo são contratos distintos de bypass. '
        'Lição: testar consentimento, outputs, admissões e identidade de ambiente antes de anunciar prontidão.')
    before=metabus.memory.confidence_ledger.get(primary.id,0.5)
    metabus.memory.add_reflection(primary.id,'Fechamento local R924–R926',reflection,score=min(before,0.4))
    penalties=[]
    for reason in ('external_review_quota','voice_dependency_resolution','source_manifest_capacity'):
        tid='r926-observed-'+reason
        primary.economy.commit(primary.id,tid,stake=10)
        penalties.append(primary.economy.resolve(tid,success=False))
        primary.trust.learn(tid,success=False,delta=0)
    observation=metabus.memory.record_observation(primary.id,'R924–R926 aceite computacional local',
        {'tests_passed':len(cases),'sdd_verified':gate['verified'],'history':gate['red_history'],
         'gpu_ready':False,'upstream_tests_status':distribution['upstream_tests_status'],
         'confidence_promoted':False,'externally_validated':False})
    _write_json(OUTPUT/'reflection.json',{'reflection':reflection,'observation_id':observation,
        'retrospective_symbolic_slashing':penalties,'economy_scope':'local_symbolic_no_real_currency',
        'confidence_promoted':False})
    artifacts=['integrations/itsfine_core.py','integrations/itsfine_lifecycle.py','integrations/local_plugin_extraction.py',
        'integrations/local_lean.py','sdd/tdd_history.py','marceloclaro/orchestrator.py','marceloclaro/cli.py',
        'scripts/finalize_core_r924.py','tests/test_r924_itsfine_hardening.py','tests/test_r925_managed_dependencies.py',
        'tests/test_r926_itsfine_final_review.py','tests/test_r923_itsfine_core.py',
        'integrations/itsfine-locks/text-py312.txt','integrations/itsfine-locks/voice-py312.txt',
        'specs/SPEC-935-R924-itsfine-lifecycle-hardening.md','specs/SPEC-935-R925-managed-dependency-attestation.md',
        'specs/SPEC-935-R926-itsfine-final-review.md','docs/ITSFINE_CORRECOES_R924.md',
        'outputs/core-r924/final-gates.json','outputs/core-r924/engines-live.json','outputs/core-r924/installation.json']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in artifacts}
    _write_json(OUTPUT/'artifact-hashes.json',{'sha256':hashes,'scope':'selected_delivery_including_new_untracked_files','externally_validated':False})
    from evolution.cycles import EvolutionRegistry
    registry=EvolutionRegistry()
    cycle=registry.record('R924–R926: instalação fixa, motores CPU preparados e hardening de extrator/Lean/TDD',
        ['Reinstalação offline/SRI e política preservada','Três motores com locks e sondas reais sem pesos',
         'Paths/YAML/processos/admissões corrigidos sob testes','Fontes gerenciadas agregadas e vinculadas a inputs'],
        score=7.0,lessons=[reflection,'Score de processo interno, não qualidade científica ou validação externa.'])
    cycle.artifact_hashes=hashes; cycle.evidence_trail=['specs/SPEC-935-R926-itsfine-final-review.md','outputs/core-r924/final-gates.json']
    registry.save()
    from marceloclaro.doctor import run_doctor
    doctor=run_doctor(); _write_json(OUTPUT/'doctor-final.json',doctor)
    print(json.dumps({'status':report['status'],'tests_passed':len(cases),'sdd_criteria':f"{gate['passed_count']}/{gate['total_count']}",
        'history':gate['red_history'],'engines':engines['engines'],'upstream_tests_status':distribution['upstream_tests_status'],
        'doctor':doctor['overall'],'evolution_round':cycle.round_id,'externally_validated':False},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
