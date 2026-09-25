#!/usr/bin/env python3
"""Conferência aritmética de um escopo financeiro; não valida conformidade legal."""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ZERO = Decimal('0.00')
CREDITS = {'repasse', 'rendimento', 'contrapartida', 'ressarcimento', 'estorno_despesa'}
DEBITS = {'despesa', 'tarifa', 'tributo', 'devolucao', 'estorno_receita'}
TRANSFERS = {'transferencia_entrada', 'transferencia_saida'}


def money(value, label, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str):
        raise ValueError(f'{label}: usar texto monetário exato, nunca float ou zero presumido')
    text = value.strip()
    if text.startswith('R$'):
        text = text[2:].strip()
    if re.fullmatch(r'-?(?:\d+|\d{1,3}(?:\.\d{3})+),\d{2}', text):
        text = text.replace('.', '').replace(',', '.')
    elif not re.fullmatch(r'-?\d+(?:\.\d{2})?', text):
        raise ValueError(f'{label}: valor ambíguo ou inválido: {value!r}')
    return Decimal(text).quantize(Decimal('0.01'))


def iso_date(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{label}: usar data ISO AAAA-MM-DD')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{label}: data inválida') from exc


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: texto obrigatório')
    return value.strip()


def as_list(value, label):
    if not isinstance(value, list):
        raise ValueError(f'{label}: lista obrigatória')
    return value


def fmt(value):
    return None if value is None else format(value, '.2f')


def reconcile(data):
    if not isinstance(data, dict):
        raise ValueError('A entrada deve ser um objeto JSON')
    scope = required_text(data.get('escopo'), 'escopo')
    if data.get('moeda', 'BRL') != 'BRL':
        raise ValueError('Somente BRL é suportado')
    period = data.get('periodo')
    if not isinstance(period, dict):
        raise ValueError('periodo: objeto obrigatório')
    start = iso_date(period.get('inicio'), 'periodo.inicio')
    end = iso_date(period.get('fim'), 'periodo.fim')
    if start > end:
        raise ValueError('Período invertido')
    accounts = as_list(data.get('contas_incluidas'), 'contas_incluidas')
    accounts = [required_text(x, 'conta') for x in accounts]
    if not accounts or len(accounts) != len(set(accounts)):
        raise ValueError('Informar contas incluídas únicas e não vazias')

    opening = money(data.get('saldo_inicial_controle'), 'saldo_inicial_controle', True)
    bank = money(data.get('saldo_final_banco'), 'saldo_final_banco', True)
    warnings = []
    sources = data.get('fontes_saldos', {})
    if not isinstance(sources, dict):
        raise ValueError('fontes_saldos deve ser objeto')
    for field, value in [('saldo_inicial_controle', opening), ('saldo_final_banco', bank)]:
        if value is None:
            warnings.append({'tipo': 'saldo_desconhecido', 'campo': field})
        elif not isinstance(sources.get(field), str) or not sources[field].strip():
            warnings.append({'tipo': 'saldo_sem_fonte', 'campo': field})
    coverage = data.get('extratos_completos')
    if coverage not in (True, False, None) or (coverage is not None and type(coverage) is not bool):
        raise ValueError('extratos_completos deve ser true, false ou null')
    if coverage is not True:
        warnings.append({'tipo': 'cobertura_de_extratos_nao_confirmada'})

    totals = defaultdict(lambda: ZERO)
    transfers = defaultdict(list)
    ids, potential_duplicates = set(), defaultdict(list)
    movement_index = {}
    movements = as_list(data.get('movimentos'), 'movimentos')
    for i, row in enumerate(movements, 1):
        if not isinstance(row, dict):
            raise ValueError(f'Movimento {i}: objeto obrigatório')
        mid = required_text(row.get('id'), f'Movimento {i}.id')
        if mid in ids:
            raise ValueError(f'ID de movimento repetido: {mid}; resolver antes de calcular')
        ids.add(mid)
        movement_index[mid] = row
        kind = row.get('tipo')
        if kind not in CREDITS | DEBITS | TRANSFERS:
            raise ValueError(f'{mid}: tipo não reconhecido; classificar com evidência')
        when = iso_date(row.get('data'), f'{mid}.data')
        if not start <= when <= end:
            raise ValueError(f'{mid}: data fora do período')
        account = required_text(row.get('conta'), f'{mid}.conta')
        if account not in accounts:
            raise ValueError(f'{mid}: conta fora do escopo')
        amount = money(row.get('valor'), f'{mid}.valor')
        if amount < ZERO:
            raise ValueError(f'{mid}: usar valor não negativo e tipo para indicar o sentido')
        source = row.get('fonte')
        if not isinstance(source, str) or not source.strip():
            warnings.append({'tipo': 'movimento_sem_fonte', 'id': mid})
        document = row.get('documento', '')
        if not isinstance(document, str):
            raise ValueError(f'{mid}.documento: usar texto')
        potential_duplicates[(row['data'], kind, amount, account, document)].append(mid)
        if kind in TRANSFERS:
            tid = required_text(row.get('id_transferencia'), f'{mid}.id_transferencia')
            transfers[tid].append((kind, amount, account, mid))
        else:
            totals[kind] += amount

    for tid, rows in transfers.items():
        if (len(rows) != 2 or {r[0] for r in rows} != TRANSFERS
                or rows[0][1] != rows[1][1] or rows[0][2] == rows[1][2]):
            raise ValueError(f'Transferência interna {tid}: exigir dois lados de mesmo valor em contas distintas do escopo')
    for key, group in potential_duplicates.items():
        if len(group) > 1:
            warnings.append({'tipo': 'possivel_duplicidade_mantida_no_calculo', 'ids': group})

    prior = as_list(data.get('movimentos_anteriores_pendentes', []), 'movimentos_anteriores_pendentes')
    for row in prior:
        if not isinstance(row, dict):
            raise ValueError('Movimento anterior: objeto obrigatório')
        mid = required_text(row.get('id'), 'movimento_anterior.id')
        if mid in ids:
            raise ValueError(f'ID de movimento repetido: {mid}')
        ids.add(mid)
        if row.get('tipo') not in CREDITS | DEBITS:
            raise ValueError(f'{mid}: movimento anterior deve ser entrada ou saída externa')
        if iso_date(row.get('data'), f'{mid}.data') >= start:
            raise ValueError(f'{mid}: movimento anterior deve anteceder o período')
        if row.get('conta') not in accounts:
            raise ValueError(f'{mid}: conta fora do escopo')
        if money(row.get('valor'), f'{mid}.valor') <= ZERO:
            raise ValueError(f'{mid}: valor anterior deve ser positivo')
        required_text(row.get('fonte'), f'{mid}.fonte')
        if row.get('incluido_no_saldo_inicial') is not True:
            raise ValueError(f'{mid}: confirmar documentalmente que já integra o saldo inicial do controle')
        movement_index[mid] = row

    adjustments = as_list(data.get('pendencias_bancarias', []), 'pendencias_bancarias')
    adjustment_total = ZERO
    adjustment_ids = set()
    for row in adjustments:
        if not isinstance(row, dict):
            raise ValueError('Pendência bancária: objeto obrigatório')
        aid = required_text(row.get('id'), 'pendencia.id')
        if aid in adjustment_ids:
            raise ValueError(f'Pendência bancária duplicada: {aid}')
        adjustment_ids.add(aid)
        kind = row.get('natureza')
        if kind not in {'credito_ja_no_controle', 'debito_ja_no_controle'}:
            raise ValueError(f'{aid}: natureza de pendência inválida')
        amount = money(row.get('valor'), f'{aid}.valor')
        if amount <= ZERO:
            raise ValueError(f'{aid}: pendência deve ter valor positivo')
        required_text(row.get('fonte'), f'{aid}.fonte')
        required_text(row.get('justificativa'), f'{aid}.justificativa')
        linked = required_text(row.get('movimento_id'), f'{aid}.movimento_id')
        if linked not in movement_index:
            raise ValueError(f'{aid}: movimento do controle não localizado')
        expected_types = CREDITS if kind == 'credito_ja_no_controle' else DEBITS
        linked_row = movement_index[linked]
        if linked_row['tipo'] not in expected_types:
            raise ValueError(f'{aid}: sentido incompatível com movimento vinculado')
        if amount != money(linked_row['valor'], f'{aid}.valor_vinculado'):
            raise ValueError(f'{aid}: valor diferente do movimento; separar parcelas documentadas antes de calcular')
        if sum(1 for r in adjustments if r.get('movimento_id') == linked) > 1:
            raise ValueError(f'{aid}: movimento vinculado a mais de uma pendência')
        adjustment_total += amount if kind == 'credito_ja_no_controle' else -amount

    credits = sum((totals[t] for t in CREDITS), ZERO)
    debits = sum((totals[t] for t in DEBITS), ZERO)
    closing = None if opening is None else opening + credits - debits
    adjusted_bank = None if bank is None else bank + adjustment_total
    difference = None if closing is None or adjusted_bank is None else closing - adjusted_bank
    if closing is not None and closing < ZERO:
        warnings.append({'tipo': 'saldo_calculado_negativo'})
    status = ('nao_calculavel' if difference is None else
              'valores_conciliados' if difference == ZERO else 'divergencia')
    return {
        'escopo': scope, 'moeda': 'BRL', 'periodo': period, 'contas_incluidas': accounts,
        'quantidade_movimentos': len(movements), 'pares_transferencias_internas': len(transfers),
        'quantidade_movimentos_anteriores_informados': len(prior),
        'totais_por_tipo': {k: fmt(totals[k]) for k in sorted(CREDITS | DEBITS)},
        'saldo_inicial_controle': fmt(opening), 'entradas_externas': fmt(credits),
        'saidas_externas': fmt(debits), 'saldo_calculado_controle': fmt(closing),
        'saldo_final_banco': fmt(bank), 'ajustes_bancarios_liquidos': fmt(adjustment_total),
        'saldo_bancario_ajustado': fmt(adjusted_bank), 'diferenca_controle_menos_banco': fmt(difference),
        'status_aritmetico': status, 'alertas': warnings,
        'cobertura_de_extratos_declarada': coverage,
        'comprovacao_documental': 'nao_avaliada_pelo_script',
        'observacao': 'Resultado aritmético baseado na entrada. Verificar fontes, completude e classificações; não certifica regularidade ou aprovação da prestação de contas.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = reconcile(json.loads(args.input.read_text(encoding='utf-8')))
        output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            if args.output.resolve() == args.input.resolve():
                raise ValueError('Saída deve ser diferente da entrada')
            args.output.write_text(output, encoding='utf-8')
        else:
            sys.stdout.write(output)
    except (OSError, ValueError, TypeError, KeyError, InvalidOperation) as exc:
        print(f'Erro de entrada: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
