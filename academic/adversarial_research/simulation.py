"""R920: ensaio acadêmico sintético sobre o motor social MIT, sem inferência.

O planejamento só inspeciona entradas locais. A revisão por regras acontece uma
única vez na execução; nenhuma dinâmica social resolve suas objeções. Os papéis
referenciam SPECIALISTS, mas não ativam agentes nem representam pessoas reais.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from typing import Any, Callable

from .board import review_research
from .evidence import identifier, intake
from .registry import SPECIALISTS


STAGES = (
    'projeto', 'metodologia', 'qualificacao', 'analise', 'resultados',
    'pre_defesa', 'defesa',
)
SCENARIOS = ('base', 'banca_divergente', 'fonte_indisponivel')
GROUPS = {
    'cientistas_metodo': (
        'A02', 'A08', 'A10', 'A11', 'A13', 'A14', 'A15', 'A16',
        'A18', 'A22', 'A25', 'A32',
    ),
    'cientistas_resultados': (
        'A03', 'A09', 'A11', 'A12', 'A15', 'A16', 'A17', 'A23',
        'A24', 'A25', 'A26', 'A32',
    ),
    'banca_interdisciplinar': (
        'A04', 'A05', 'A08', 'A10', 'A13', 'A18', 'A22', 'A24',
        'A26', 'A30', 'A31', 'A32',
    ),
}
DEFAULT_LIMITS = {
    'max_steps': 34, 'max_rounds': 288, 'max_actions': 3456,
    'timeout_seconds': 30,
}
_USAGE_FIELDS = (
    'review_steps', 'cases_executed', 'rounds_executed',
    'actions_executed', 'actions_reserved',
)
_TEMPLATES = {
    'projeto': (
        'Como o problema e os objetivos delimitam a contribuição pretendida?',
        'Problema delimitado, objetivos, contraste bibliográfico e pressupostos explícitos.',
    ),
    'metodologia': (
        'Por que os procedimentos e critérios de seleção são adequados ao desenho?',
        'Protocolo, unidades de análise, critérios de seleção e justificativa dos instrumentos.',
    ),
    'qualificacao': (
        'Que alinhamentos e lacunas precisam ser discutidos antes de prosseguir?',
        'Versão do projeto, decisões metodológicas justificadas, viabilidade e documentos éticos pertinentes.',
    ),
    'analise': (
        'Como as decisões analíticas distinguem interpretações rivais e casos negativos?',
        'Trilha de análise, critérios de interpretação, unidades e registro dos desacordos.',
    ),
    'resultados': (
        'Quais resultados são observados, propostos ou contraditos pelas fontes?',
        'Resultados rastreáveis às fontes, evidências negativas e limites das inferências.',
    ),
    'pre_defesa': (
        'Quais pendências documentais e objeções ainda precisam de encaminhamento?',
        'Manuscrito versionado, mapa alegação-evidência e lista explícita de pendências.',
    ),
    'defesa': (
        'Como justificar as conclusões diante das alternativas e das contradições preservadas?',
        'Alegações delimitadas, fontes localizadas, decisões justificadas e limites reconhecidos.',
    ),
}
_NON_RESEARCH_OUTPUTS = {
    'legacy_board', 'score', 'scores', 'weighted_score', 'overall_score',
    'verdict', 'answer', 'answers', 'resposta_modelo',
}
_CLOCK_FIELDS = {'timestamp', 'created_at', 'generated_at', 'started_at_hour'}


def _safeguards() -> dict[str, bool]:
    return {
        'scientifically_approved': False, 'external_validation': False,
        'agent_inference_executed': False, 'llm_inference_executed': False,
        'confidence_promoted': False, 'human_review_required': True,
    }


def _canonical_bytes(value: Any) -> bytes:
    """JSON estrito: não converte silenciosamente tuplas ou chaves numéricas."""
    def check(item: Any) -> None:
        if type(item) is dict:
            for key, child in item.items():
                if type(key) is not str:
                    raise ValueError('As chaves JSON devem ser strings')
                check(child)
        elif type(item) is list:
            for child in item:
                check(child)
        elif item is not None and type(item) not in (str, int, float, bool):
            raise ValueError('Objeto não permitido no contrato JSON')

    try:
        check(value)
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          allow_nan=False, separators=(',', ':')).encode('utf-8')
    except (TypeError, OverflowError, RecursionError, UnicodeError) as exc:
        raise ValueError('Contrato JSON inválido') from exc


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _limits(value: Any) -> dict[str, int | float]:
    if value is None:
        value = {}
    if type(value) is not dict or set(value) - set(DEFAULT_LIMITS):
        raise ValueError('Limites desconhecidos ou inválidos')
    result = {**DEFAULT_LIMITS, **value}
    for key in ('max_steps', 'max_rounds', 'max_actions'):
        if type(result[key]) is not int or not 1 <= result[key] <= DEFAULT_LIMITS[key]:
            raise ValueError(key + ' fora do limite')
    timeout = result['timeout_seconds']
    if (type(timeout) not in (int, float) or not 0 < timeout <= 120
            or not math.isfinite(timeout)):
        raise ValueError('timeout_seconds inválido')
    return result


def _cases(value: Any) -> list[dict[str, Any]]:
    if value is None:
        value = [{'case_id': 'pre_defesa_base', 'stage': 'pre_defesa',
                  'group': 'banca_interdisciplinar', 'scenario': 'base'}]
    if type(value) is not list or not 1 <= len(value) <= 24:
        raise ValueError('Forneça de 1 a 24 casos')
    result, known = [], set()
    required = {'case_id', 'stage', 'group', 'scenario'}
    for row in value:
        if (type(row) is not dict or set(row) - required - {'rounds', 'agents'}
                or required - set(row)):
            raise ValueError('Estrutura do caso inválida')
        cid = identifier(row['case_id'], 'case_id')
        if cid in known:
            raise ValueError('case_id duplicado')
        known.add(cid)
        for field, choices in (('stage', STAGES), ('group', GROUPS), ('scenario', SCENARIOS)):
            if type(row[field]) is not str or row[field] not in choices:
                raise ValueError(field + ' desconhecido')
        item = {**row, 'rounds': row.get('rounds', 4), 'agents': row.get('agents', 6)}
        for field in ('rounds', 'agents'):
            if type(item[field]) is not int or not 1 <= item[field] <= 12:
                raise ValueError(field + ' deve ser inteiro de 1 a 12')
        result.append(item)
    return result


def plan_simulation(project: dict[str, Any], cases: Any = None, seed: int = 42,
                    limits: Any = None) -> dict[str, Any]:
    """Sela dados e estados de integridade, inclusive fontes não inspecionadas."""
    if type(seed) is not int:
        raise ValueError('seed deve ser inteiro não booleano')
    bounds, selected = _limits(limits), _cases(cases)
    if type(project) is not dict:
        raise ValueError('Projeto deve ser objeto JSON')
    _canonical_bytes(project)
    try:
        _, artifact, manifest = intake(project)
    except (OSError, UnicodeError, TypeError) as exc:
        raise ValueError('Não foi possível inspecionar o projeto local') from exc
    # Não usar o projeto normalizado pelo intake: preservar todas as declarações
    # originais, sem duplicar normalizações na revisão futura.
    payload = {
        'project': copy.deepcopy(project), 'cases': selected, 'seed': seed,
        'limits': bounds, 'artifact_sha256': artifact['sha256'],
        'evidence_manifest': manifest,
    }
    plan = {
        **payload, 'spec_id': 'SPEC-935-R920', 'status': 'planned',
        'simulation_id': 'academic-sim-' + _digest(payload)[:32],
        'execution_started': False, 'simulation_executed': False,
        'execution_complete': False, 'usage': dict.fromkeys(_USAGE_FIELDS, 0),
        **_safeguards(),
    }
    plan['plan_sha256'] = _digest(plan)
    return plan


def _validated_plan(value: Any) -> dict[str, Any]:
    if type(value) is not dict or type(value.get('plan_sha256')) is not str:
        raise ValueError('Plano selado obrigatório')
    encoded = _canonical_bytes(value)
    if value['plan_sha256'] != _digest({k: v for k, v in value.items() if k != 'plan_sha256'}):
        raise ValueError('Hash do plano divergente')
    required = {'project', 'cases', 'seed', 'limits'}
    if required - set(value):
        raise ValueError('Plano incompleto')
    # Reconstruir também recusa configurações inválidas com hash recalculado,
    # campos adicionais, flags alteradas e mudanças de estado/erro das fontes.
    rebuilt = plan_simulation(value['project'], value['cases'], value['seed'], value['limits'])
    if encoded != _canonical_bytes(rebuilt):
        raise ValueError('Plano obsoleto ou estrutura divergente; planeje novamente')
    return rebuilt


def _without_metrics(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _without_metrics(v) for k, v in value.items() if k not in _NON_RESEARCH_OUTPUTS}
    if isinstance(value, list):
        return [_without_metrics(v) for v in value]
    return value


def _normalize_trace(value: Any) -> Any:
    if isinstance(value, dict):
        # A engine usa int em final_opinions. Converter ANTES da canonização.
        return {str(k): _normalize_trace(v) for k, v in value.items()
                if k not in _CLOCK_FIELDS and k != 'text'}
    if isinstance(value, list):
        return [_normalize_trace(v) for v in value]
    return value


def _questions(project: dict[str, Any], review: dict[str, Any], case: dict[str, Any]
               ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    targets = [c['claim_id'] for c in project['claims']]
    question, evidence = _TEMPLATES[case['stage']]
    questions = [{
        'stage': case['stage'], 'question': question, 'required_evidence': evidence,
        'target_claim_ids': targets, 'origin': 'question_template', 'status': 'pending',
    }]
    for objection in review['objections']:
        questions.append({
            'stage': case['stage'], 'question': objection['question'],
            'required_evidence': objection['required_evidence'],
            'target_claim_ids': list(objection['target_claim_ids']),
            'origin': 'local_rule', 'objection_id': objection['objection_id'],
            'source_refs': list(objection['source_refs']),
            'responsible_agent': objection['responsible_agent'], 'status': 'pending',
        })
    assumptions = []
    if case['scenario'] == 'fonte_indisponivel':
        sources = sorted(project.get('sources', []), key=lambda s: s['source_id'])
        refs = [sources[0]['source_id']] if sources else []
        affected = [c['claim_id'] for c in project['claims'] if set(c['source_refs']) & set(refs)]
        assumptions.append({
            'origin': 'hypothetical', 'source_refs': refs,
            'assumption': 'Indisponibilidade hipotética de fonte; não é constatação sobre os arquivos ou sua validade.',
        })
        questions.append({
            'stage': case['stage'], 'origin': 'hypothetical', 'source_refs': refs,
            'question': 'Se esta fonte ficasse indisponível, quais alegações precisariam ser limitadas ou suspensas?',
            'required_evidence': 'Plano de contingência e fontes alternativas efetivamente recuperadas, sem substituir evidência negativa.',
            'target_claim_ids': affected or targets, 'status': 'pending',
        })
    elif case['scenario'] == 'banca_divergente':
        assumptions.append({
            'origin': 'hypothetical', 'source_refs': [],
            'assumption': 'Posturas divergentes são parâmetros sintéticos, não opiniões observadas de especialistas.',
        })
    return questions, assumptions


def _run_case(plan: dict[str, Any], case: dict[str, Any], review: dict[str, Any]
              ) -> dict[str, Any]:
    from mirofish.social.contracts import (
        EventConfig, OasisAgentProfile, PlatformConfig, SimulationParameters,
        TimeSimulationConfig,
    )
    from mirofish.social.engine import SocialSimulationEngine

    sub_seed = int(_digest({'seed': plan['seed'], 'simulation_id': plan['simulation_id'], 'case': case}), 16)
    divergent = case['scenario'] == 'banca_divergente'
    interaction = {
        'echo_chamber_strength': 0.75 if divergent else (0.45 if case['scenario'] == 'fonte_indisponivel' else 0.35),
        'activity_level': 1.0,
        'stance_pattern': ['opposing', 'supportive', 'neutral'] if divergent else ['neutral', 'observer', 'neutral'],
        'sentiment_bias_pattern': [-0.6, 0.6, 0.0] if divergent else [-0.1, 0.1, 0.0],
    }
    roles = {role['number']: role for role in SPECIALISTS}
    profiles, participants = [], []
    for index, number in enumerate(GROUPS[case['group']][:case['agents']]):
        role = roles[number]
        profile = OasisAgentProfile(
            user_id=index, user_name=role['agent_id'], name='Papel sintético ' + number,
            bio='Referência efêmera a SPECIALISTS; não representa pessoa real.',
            persona=role['responsibility'], karma=0, friend_count=0,
            follower_count=0, statuses_count=0, created_at='',
            source_entity_uuid=role['agent_id'], source_entity_type='specialist_reference',
            sentiment_bias=interaction['sentiment_bias_pattern'][index % 3],
            stance=interaction['stance_pattern'][index % 3],
            influence_weight=1.0, activity_level=interaction['activity_level'],
        )
        profiles.append(profile)
        participants.append({
            'user_id': index, 'agent_id': role['agent_id'], 'number': number,
            'responsibility': role['responsibility'], 'limitations': role['limitations'],
            'ephemeral': True, 'inference_executed': False,
        })
    params = SimulationParameters(
        simulation_id=plan['simulation_id'] + '-' + case['case_id'],
        project_id=plan['project']['research_id'],
        simulation_requirement='Ensaio sintético de perguntas; não responder nem aprovar pesquisa.',
        time_config=TimeSimulationConfig(
            total_simulation_hours=case['rounds'], minutes_per_round=60,
            peak_activity_multiplier=1.0, off_peak_activity_multiplier=1.0,
            morning_activity_multiplier=1.0, work_activity_multiplier=1.0,
        ),
        event_config=EventConfig(hot_topics=[case['stage']]),
        twitter_config=PlatformConfig(platform='twitter', echo_chamber_strength=interaction['echo_chamber_strength']),
        generated_at='',
    )
    result = SocialSimulationEngine(profiles, params, seed=sub_seed).run(rounds=case['rounds'])
    trace = _normalize_trace(result.to_dict())
    # Perfis já estão representados como referências efêmeras. Posts padronizados
    # da engine não são respostas acadêmicas e seu texto não é exportado.
    trace.pop('profiles', None)
    questions, assumptions = _questions(plan['project'], review, case)
    return {
        **case, 'seed': sub_seed, 'participants': _normalize_trace(participants),
        'interaction_parameters': interaction, 'scenario_assumptions': assumptions,
        'questions': questions, 'trace': trace,
        'content_scope': 'synthetic_dynamics_only_no_answers', **_safeguards(),
    }


def _finish(result: dict[str, Any], plan: dict[str, Any], status: str,
            reason: str | None) -> dict[str, Any]:
    remaining = plan['cases'][len(result['cases']):]
    if remaining or result['base_review'] is None:
        result['unresolved_gaps'].append({
            'code': 'simulation_incomplete', 'reason': reason,
            'remaining_case_ids': [c['case_id'] for c in remaining],
            'base_review_pending': result['base_review'] is None,
        })
    result.update(status=status, stop_reason=reason, execution_complete=status == 'completed',
                  trajectory_sha256=_digest(result['cases']))
    return result


def run_simulation(plan: dict[str, Any], cancelled: bool = False,
                   should_stop: Callable[[], bool] | None = None) -> dict[str, Any]:
    """Executa revisão única e casos inteiros, com orçamento e prazo globais.

    O prazo/cancelamento é cooperativo entre unidades: não interrompe a revisão
    ou uma chamada da engine em andamento. Reservas não usadas não são devolvidas.
    """
    if type(cancelled) is not bool:
        raise ValueError('cancelled deve ser booleano')
    if should_stop is not None and not callable(should_stop):
        raise ValueError('should_stop deve ser callback sem argumentos')
    started = time.monotonic()
    plan = _validated_plan(plan)
    result = {
        'spec_id': 'SPEC-935-R920', 'simulation_id': plan['simulation_id'],
        'plan_sha256': plan['plan_sha256'], 'artifact_sha256': plan['artifact_sha256'],
        'evidence_manifest': copy.deepcopy(plan['evidence_manifest']),
        'base_review': None, 'cases': [], 'unresolved_objection_ids': [],
        'unresolved_gaps': [], 'usage': dict.fromkeys(_USAGE_FIELDS, 0),
        'execution_started': False, 'simulation_executed': False,
        'limits': dict(plan['limits']), 'seed': plan['seed'], **_safeguards(),
        'limitations': [
            'SIMULAÇÃO: não constitui validação científica; exige revisão humana.',
            'Opiniões e ações são dinâmica sintética, não medidas de mérito ou aprovação.',
            'Somente alegações e metadados explícitos foram submetidos às regras locais.',
            'Prazo e cancelamento são cooperativos, sem preempção durante revisão ou caso.',
        ],
    }
    if cancelled:
        return _finish(result, plan, 'cancelled', 'cancelled')
    bounds = plan['limits']
    deadline = started + bounds['timeout_seconds']

    def checkpoint() -> str | None:
        if should_stop is not None:
            stopped = should_stop()
            if type(stopped) is not bool:
                raise ValueError('should_stop deve retornar booleano')
            if stopped:
                return 'cancelled'
        return 'timeout' if time.monotonic() >= deadline else None

    reason = checkpoint()
    remaining_seconds = deadline - time.monotonic()
    if reason or remaining_seconds <= 0:
        reason = reason or 'timeout'
        return _finish(result, plan, 'cancelled' if reason == 'cancelled' else 'partial', reason)
    result['execution_started'] = True
    base = review_research(copy.deepcopy(plan['project']), max_steps=bounds['max_steps'],
                           timeout_seconds=min(bounds['timeout_seconds'], remaining_seconds))
    if (base['reviewed_artifact_hash'] != plan['artifact_sha256']
            or _canonical_bytes(base['evidence_manifest']) != _canonical_bytes(plan['evidence_manifest'])):
        raise ValueError('Artefato/fontes mudaram durante a revisão local')
    base = _without_metrics(copy.deepcopy(base))
    # O hash legado cobria métricas removidas; não o apresentar como selo desta visão.
    base.pop('report_sha256', None)
    base.update(_safeguards())
    result['base_review'] = base
    result['usage']['review_steps'] = len(base['specialist_results'])
    result['unresolved_objection_ids'] = list(dict.fromkeys(o['objection_id'] for o in base['objections']))
    result['unresolved_gaps'] = copy.deepcopy(base['unresolved_gaps'])
    reserved_rounds = 0
    for case in plan['cases']:
        reason = checkpoint()
        if reason:
            break
        reservation = case['agents'] * case['rounds']
        if (reserved_rounds + case['rounds'] > bounds['max_rounds']
                or result['usage']['actions_reserved'] + reservation > bounds['max_actions']):
            reason = 'budget_exhausted'
            break
        reserved_rounds += case['rounds']
        result['usage']['actions_reserved'] += reservation
        row = _run_case(plan, case, base)
        result['simulation_executed'] = True
        result['cases'].append(row)
        result['usage']['cases_executed'] += 1
        rounds = row['trace']['rounds']
        actions = sum(len(r['actions']) for r in rounds)
        if len(rounds) > case['rounds'] or actions > reservation:
            raise ValueError('Motor excedeu a reserva do caso')
        result['usage']['rounds_executed'] += len(rounds)
        result['usage']['actions_executed'] += actions
        if not row['trace']['completed'] or len(rounds) != case['rounds']:
            reason = 'case_incomplete'
            result['unresolved_gaps'].append({'code': reason, 'case_id': case['case_id']})
            break
    if reason is None and time.monotonic() >= deadline:
        reason = 'timeout'
    if reason is None and base['execution_complete'] is not True:
        reason = 'review_incomplete'
    if reason and not result['unresolved_gaps']:
        result['unresolved_gaps'].append({'code': 'execution_incomplete', 'reason': reason})
    status = 'cancelled' if reason == 'cancelled' else ('partial' if reason else 'completed')
    return _finish(result, plan, status, reason)


def render_simulation_report(result: dict[str, Any]) -> str:
    """Relato de perguntas pendentes, sem respostas-modelo ou decisão científica."""
    _canonical_bytes(result)
    lines = [
        '# SIMULAÇÃO acadêmica — ensaio sintético', '',
        'Este ensaio não constitui validação científica. Revisão humana obrigatória.',
        'Sentimento sintético não é aprovação; nenhuma resposta acadêmica foi gerada.', '',
        f"Identificador: {result['simulation_id']}",
        f"Estado: {result['status']}; interrupção: {result['stop_reason'] or 'nenhuma'}.",
        '', '## Alegações submetidas',
    ]
    for claim in (result.get('base_review') or {}).get('claims', []):
        lines.append(f"- {claim['claim_id']} [{claim['evidence_status']}]: {claim['statement']}")
    for case in result['cases']:
        lines.extend(['', f"## {case['case_id']} — {case['stage']} / {case['scenario']}"])
        for assumption in case['scenario_assumptions']:
            lines.append('- Hipótese: ' + assumption['assumption'])
        for question in case['questions']:
            lines.extend([
                f"- Pergunta ({question['origin']}; alvos: {', '.join(question['target_claim_ids'])}): {question['question']}",
                '  Evidência exigida (pendente): ' + question['required_evidence'],
            ])
            if question.get('objection_id'):
                lines.append('  Objeção preservada: ' + question['objection_id'])
            if question.get('source_refs'):
                lines.append('  Fontes referenciadas: ' + ', '.join(question['source_refs']))
    lines.extend(['', '## Pendências preservadas'])
    lines.extend('- ' + oid for oid in result['unresolved_objection_ids'])
    lines.extend('- ' + _canonical_bytes(gap).decode('utf-8') for gap in result['unresolved_gaps'])
    lines.extend(['', 'Encaminhamento: revisão humana das perguntas, fontes e evidências; sem aprovação automática.'])
    return '\n'.join(lines) + '\n'
