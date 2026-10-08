#!/usr/bin/env python3
"""Preencher cópias DOCX com fontes declaradas, sem rede ou assinatura."""
import argparse
import copy
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\{\{([a-zA-Z0-9_.\[\]-]+)\}\}')
LIST_TOKEN = re.compile(r'\{\{([a-zA-Z0-9_-]+)\[\]\.([a-zA-Z0-9_.-]+)\}\}')
CENT = Decimal('0.01')
MONEY_FIELDS = {
    'acao.valor', 'empenho.valor', 'plano.valor', 'saldo.bancario',
    'saldo.rendimentos_disponiveis', 'saldo.total_utilizar',
    'acoes.programado', 'acoes.executado', 'acoes.saldo',
}


def is_money(key):
    return (key.startswith('financeiro.') or key in MONEY_FIELDS
            or key.endswith(('.total', '.unitario'))
            or re.fullmatch(r'pagamentos\.\d+\.valor', key)
            or re.fullmatch(r'acoes\.\d+\.(programado|executado|saldo)', key)
            or re.fullmatch(r'mapa\.\d+\.[abc]', key))


def known(value):
    return value is not None and str(value).strip() != ''


def money(value):
    """Exigir string inequívoca; aceitar BR com vírgula ou decimal sem milhar."""
    if not isinstance(value, str):
        raise ValueError('Valor numérico deve ser texto, nunca float.')
    s = value.strip().replace('R$', '').strip()
    if re.fullmatch(r'-?\d{1,3}(\.\d{3})+,\d{1,2}', s):
        s = s.replace('.', '').replace(',', '.')
    elif re.fullmatch(r'-?\d+,\d{1,2}', s):
        s = s.replace(',', '.')
    elif not re.fullmatch(r'-?\d+(\.\d{1,2})?', s):
        raise ValueError('Valor monetário inválido ou ambíguo: ' + value)
    try:
        result = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError('Valor inválido') from exc
    if not result.is_finite():
        raise ValueError('Valor não finito')
    return result.quantize(CENT, rounding=ROUND_HALF_UP)


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+([.,]\d+)?', value.strip()):
        raise ValueError('Quantidade inválida; usar texto sem separador de milhar.')
    result = Decimal(value.strip().replace(',', '.'))
    if result <= 0:
        raise ValueError('Quantidade deve ser positiva.')
    return result


def brl(value):
    return f'{value:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def evidence(data, key, row=None):
    src = data.get('fontes', {}).get(key)
    if not src and row:
        src = row.get('_fonte')
    return src if isinstance(src, str) and src.strip() else None


def derive(data):
    """Nunca totalizar linhas incompletas, nem sobrescrever divergência."""
    data = copy.deepcopy(data)
    fields = data.setdefault('campos', {})
    sources = data.setdefault('fontes', {})
    lists = data.setdefault('listas', {})
    log = []
    def suppress(key, reason):
        if known(fields.get(key)):
            log.append({'campo':key,'operacao':'bloqueado','motivo':reason})
        fields[key] = None
        sources.pop(key, None)

    for group in ['itens', 'bens', 'remanejados', 'adicionados', 'proposta', 'mapa']:
        rows = lists.get(group)
        if not rows:
            suppress(group+'.total', 'lista vazia ou desconhecida')
            continue
        totals = []
        for i, row in enumerate(rows):
            prefix = f'{group}.{i}'
            a, b = row.get('quantidade'), row.get('unitario')
            if not (known(a) and known(b) and evidence(data, prefix+'.quantidade', row)
                    and evidence(data, prefix+'.unitario', row)):
                totals.append(None)
                continue
            unit = money(b)
            if unit < 0:
                raise ValueError(f'{prefix}: preço negativo.')
            total = (quantity(a) * unit).quantize(CENT, rounding=ROUND_HALF_UP)
            if known(row.get('total')) and money(row['total']) != total:
                raise ValueError(f'{prefix}: total informado difere de quantidade × preço.')
            row['total'] = brl(total)
            sources[prefix+'.total'] = f'Cálculo: {prefix}.quantidade × {prefix}.unitario'
            log.append({'campo':prefix+'.total','operacao':f'{a} × {b}','resultado':brl(total)})
            totals.append(total)
        key = group+'.total'
        if all(v is not None for v in totals):
            total = sum(totals, Decimal(0))
            if known(fields.get(key)) and money(fields[key]) != total:
                raise ValueError(f'{key}: soma diverge do total informado.')
            fields[key] = brl(total)
            sources[key] = 'Cálculo: soma das linhas completas de '+group
            log.append({'campo':key,'operacao':'soma','resultado':brl(total)})
        else:
            # Um total de extrato pode existir, mas não deve ser apresentado como
            # soma desta tabela incompleta; preservar o input fora do resultado.
            suppress(key, 'linhas incompletas')
    # Pagamentos devem representar saídas sem duplicar bruto, líquido e guias.
    rows = lists.get('pagamentos')
    if rows:
        complete = all(known(row.get('valor')) and evidence(data,f'pagamentos.{i}.valor',row)
                       for i,row in enumerate(rows))
        if complete:
            values = [money(row['valor']) for row in rows]
            if any(v < 0 for v in values):
                raise ValueError('Pagamento negativo: classificar estorno na conciliação.')
            total = sum(values,Decimal(0))
            if known(fields.get('pagamentos.total')) and money(fields['pagamentos.total']) != total:
                raise ValueError('Total de pagamentos diverge das linhas.')
            fields['pagamentos.total'] = brl(total)
            sources['pagamentos.total'] = 'Cálculo: soma dos pagamentos documentados'
            log.append({'campo':'pagamentos.total','operacao':'soma','resultado':brl(total)})
        else:
            suppress('pagamentos.total', 'linhas incompletas')
    else:
        suppress('pagamentos.total', 'lista vazia ou desconhecida')
    # Ações: orçamento e execução não são sinônimos do saldo bancário.
    rows = lists.get('acoes', [])
    for i, row in enumerate(rows):
        prefix = f'acoes.{i}'
        if all(known(row.get(k)) and evidence(data,prefix+'.'+k,row)
               for k in ['programado','executado']):
            planned, spent = money(row['programado']), money(row['executado'])
            if min(planned, spent) < 0:
                raise ValueError(prefix+': programado e executado devem ser não negativos.')
            value = planned-spent
            if known(row.get('saldo')) and money(row['saldo']) != value:
                raise ValueError(prefix+': saldo diverge de programado menos executado.')
            row['saldo'] = brl(value)
            sources[prefix+'.saldo'] = 'Cálculo: programado menos executado em '+prefix
            log.append({'campo':prefix+'.saldo','operacao':'programado - executado','resultado':brl(value)})
    for column in ['programado','executado','saldo']:
        key = 'acoes.'+column
        if rows and all(known(row.get(column)) and evidence(data,f'acoes.{i}.{column}',row)
                        for i,row in enumerate(rows)):
            total = sum((money(row[column]) for row in rows),Decimal(0))
            if known(fields.get(key)) and money(fields[key]) != total:
                raise ValueError(key+': soma diverge do total informado.')
            fields[key] = brl(total)
            sources[key] = 'Cálculo: soma da coluna '+column+' das ações documentadas'
            log.append({'campo':key,'operacao':'soma','resultado':brl(total)})
        else:
            suppress(key, 'ações incompletas ou desconhecidas')
    base = ['financeiro.saldo_anterior','financeiro.repasse',
            'financeiro.contrapartida','financeiro.rendimentos']
    if all(known(fields.get(k)) and evidence(data,k) for k in base):
        total = sum((money(fields[k]) for k in base),Decimal(0))
        for key,value in [('financeiro.total_disponivel',total)]:
            if known(fields.get(key)) and money(fields[key]) != value:
                raise ValueError(key+': valor diverge da memória de cálculo.')
            fields[key]=brl(value);sources[key]='Cálculo: soma de '+', '.join(base)
            log.append({'campo':key,'operacao':'soma','resultado':brl(value)})
        key='financeiro.despesas'
        if known(fields.get(key)) and evidence(data,key):
            saldo=total-money(fields[key])
            if known(fields.get('financeiro.saldo')) and money(fields['financeiro.saldo']) != saldo:
                raise ValueError('Saldo financeiro diverge de disponível menos despesas.')
            fields['financeiro.saldo']=brl(saldo)
            sources['financeiro.saldo']='Cálculo: total disponível menos despesas'
            log.append({'campo':'financeiro.saldo','operacao':'disponível - despesas','resultado':brl(saldo)})
    if (known(fields.get('financeiro.despesas')) and known(fields.get('pagamentos.total'))
            and evidence(data,'financeiro.despesas') and evidence(data,'pagamentos.total')
            and money(fields['financeiro.despesas']) != money(fields['pagamentos.total'])):
        raise ValueError('Despesas e relação de pagamentos divergem; delimitar o mesmo escopo.')
    return data, log


def analyze(data):
    """Alertas de conferência; não corrigir, excluir ou aprovar registros."""
    alerts = []
    fields, lists = data.get('campos',{}), data.get('listas',{})
    def add(code, field, message):
        alerts.append({'codigo':code,'campo':field,'mensagem':message})
    def value(key):
        return money(fields[key]) if known(fields.get(key)) and evidence(data,key) else None
    seen = {}
    for i,row in enumerate(lists.get('pagamentos',[])):
        columns = ['comprovante','credor','data_pagamento','valor']
        if all(known(row.get(k)) and evidence(data,f'pagamentos.{i}.{k}',row) for k in columns):
            signature = tuple(money(row[k]) if k == 'valor' else row[k].strip().casefold() for k in columns)
            if signature in seen:
                add('possivel_duplicidade',f'pagamentos.{i}',
                    f'Comprovante, credor, data e valor coincidem com pagamentos.{seen[signature]}; conferir antes de totalizar para entrega.')
            else:
                seen[signature] = i
    for i,row in enumerate(lists.get('acoes',[])):
        if known(row.get('saldo')) and evidence(data,f'acoes.{i}.saldo',row) and money(row['saldo']) < 0:
            add('execucao_superior',f'acoes.{i}.saldo','Executado superior ao programado; conferir plano e autorizações.')
    proposal, available = value('proposta.total'), value('saldo.total_utilizar')
    if proposal is not None and available is not None and proposal > available:
        add('proposta_excede_saldo','proposta.total','Proposta supera o total informado para utilização; revisar disponibilidade e escopo.')
    removed, added = value('remanejados.total'), value('adicionados.total')
    if removed is not None and added is not None and removed != added:
        add('readequacao_desbalanceada','adicionados.total','Valores remanejados e adicionados diferem; documentar a cobertura ou o saldo remanescente.')
    for i,row in enumerate(lists.get('mapa',[])):
        chosen = (row.get('escolhido') or '').strip().lower()
        if chosen in ['a','b','c'] and all(known(row.get(k)) and evidence(data,f'mapa.{i}.{k}',row)
                                        for k in ['escolhido','unitario',chosen]):
            if money(row['unitario']) != money(row[chosen]):
                add('preco_escolhido_diverge',f'mapa.{i}.unitario','Preço utilizado difere da cotação do fornecedor indicado; conferir a proposta e a decisão.')
    return alerts


def xml_text(node):
    return ''.join(x.text or '' for x in node.iter(qn('w:t')))


def replace_spanning(p, replacements):
    """Substituir tokens até entre runs, conservando formatação circundante."""
    nodes = list(p.iter(qn('w:t')))
    text = ''.join(n.text or '' for n in nodes)
    matches = [m for m in TOKEN.finditer(text) if m.group(1) in replacements]
    for match in reversed(matches):
        pos = 0
        segments = []
        for n in nodes:
            length = len(n.text or '')
            segments.append((n, pos, pos+length))
            pos += length
        touched = [(n,a,b) for n,a,b in segments if a < match.end() and b > match.start()]
        if not touched:
            continue
        value = str(replacements[match.group(1)])
        for j,(n,a,b) in enumerate(touched):
            old = n.text or ''
            before = old[:max(0, match.start()-a)]
            after = old[max(0, match.end()-a):] if b > match.end() else ''
            n.text = before + (value if j == 0 else '') + after
            n.set(qn('xml:space'), 'preserve')


def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError('Entrada deve ser objeto JSON.')
    for key in ['campos', 'fontes', 'listas']:
        if not isinstance(data.get(key, {}), dict):
            raise ValueError(key+' deve ser objeto.')
    for k,v in data.get('campos', {}).items():
        if v is not None and not isinstance(v, str):
            raise ValueError('Campo deve ser string ou null: '+k)
        if isinstance(v, str) and ('{{' in v or '}}' in v):
            raise ValueError('Valor contém marcador reservado: '+k)
        if known(v) and is_money(k):
            money(v)
    for k,v in data.get('fontes',{}).items():
        if v is not None and not isinstance(v,str):
            raise ValueError('Fonte deve ser texto ou null: '+k)
    for k,rows in data.get('listas', {}).items():
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError('Lista inválida: '+k)
        for row in rows:
            for field, value in row.items():
                if value is not None and not isinstance(value, str):
                    raise ValueError(f'{k}.{field}: usar string ou null.')
                if isinstance(value, str) and ('{{' in value or '}}' in value):
                    raise ValueError('Valor contém marcador reservado.')
                if known(value) and is_money(f'{k}.0.{field}'):
                    money(value)
                if field == 'quantidade' and known(value):
                    quantity(value)


def fill(model, data, output):
    doc = Document(ROOT/'assets'/'modelos-editaveis'/f'{model}.docx')
    missing = []
    used = []

    def resolve(key, value, src):
        if not known(value) or not src:
            missing.append({'modelo':model,'campo':key,
                            'motivo':'dado ausente' if not known(value) else 'fonte ausente'})
            return '[PENDENTE]'
        used.append({'campo':key,'fonte':src})
        return brl(money(value)) if is_money(key) else str(value)

    parts = [doc._element]
    for section in doc.sections:
        parts.extend([section.header._element, section.footer._element])
    for part in parts:
        for row in list(part.iter(qn('w:tr'))):
            tokens = LIST_TOKEN.findall(xml_text(row))
            if not tokens:
                continue
            groups = {x[0] for x in tokens}
            if len(groups) != 1:
                raise ValueError('Mais de uma lista numa linha de modelo.')
            group = next(iter(groups))
            entries = data.get('listas', {}).get(group, [])
            if not entries:
                entries = [{}]
            parent = row.getparent()
            for i,entry in enumerate(entries):
                new = copy.deepcopy(row)
                replacements = {}
                for _,field in tokens:
                    key = f'{group}.{i}.{field}'
                    replacements[f'{group}[].{field}'] = resolve(
                        key, entry.get(field), evidence(data, key, entry))
                for p in new.iter(qn('w:p')):
                    replace_spanning(p, replacements)
                parent.insert(parent.index(row), new)
            parent.remove(row)
        for p in list(part.iter(qn('w:p'))):
            keys = set(TOKEN.findall(xml_text(p)))
            replacements = {}
            for key in keys:
                if key == 'status_documento':
                    replacements[key] = ('MINUTA PARA ANÁLISE E EMISSÃO PELA CREDE'
                                         if model == 'anexo-10' else 'MINUTA PARA CONFERÊNCIA')
                else:
                    replacements[key] = resolve(key, data.get('campos',{}).get(key), evidence(data,key))
            replace_spanning(p, replacements)
    unresolved = TOKEN.findall(xml_text(doc._element))
    if unresolved:
        raise ValueError('Marcadores não processados: '+', '.join(unresolved))
    path = output/(model+'_minuta.docx')
    doc.save(path)
    return {'modelo':model,'arquivo':path.name,'status':'minuta',
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'pendencias':missing,'preenchidos':used}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada', type=Path)
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--modelos', required=True, help='IDs separados por vírgula ou todos')
    args = parser.parse_args()
    raw = json.loads(args.entrada.read_text(encoding='utf-8'))
    validate_input(raw)
    data, calculations = derive(raw)
    alerts = analyze(data)
    available = sorted(p.stem for p in (ROOT/'assets'/'modelos-editaveis').glob('*.docx'))
    models = available if args.modelos == 'todos' else list(dict.fromkeys(args.modelos.split(',')))
    if not models or any(m not in available for m in models):
        raise ValueError('Modelo desconhecido. Disponíveis: '+', '.join(available))
    # Não substituir saídas de um lote anterior, mesmo quando geradas no mesmo dia.
    if args.saida.exists() and any(args.saida.iterdir()):
        raise ValueError('Pasta de saída não está vazia; use uma nova versão.')
    args.saida.mkdir(parents=True, exist_ok=True)
    reports = [fill(m, data, args.saida) for m in models]
    report = {'gerado_em_utc':datetime.now(timezone.utc).isoformat(),
              'entrada_sha256':hashlib.sha256(args.entrada.read_bytes()).hexdigest(),
              'tipo':'minutas; fontes declaradas precisam de conferência humana',
              'calculos':calculations,'alertas':alerts,'documentos':reports}
    (args.saida/'preenchimento.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    with (args.saida/'pendencias.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=['modelo','campo','motivo'],delimiter=';')
        writer.writeheader()
        for r in reports:
            writer.writerows(r['pendencias'])
    with (args.saida/'alertas.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=['codigo','campo','mensagem'],delimiter=';')
        writer.writeheader()
        writer.writerows(alerts)
    print(json.dumps({'documentos':len(reports),'campos_pendentes':sum(len(r['pendencias']) for r in reports),
                      'alertas':len(alerts)},ensure_ascii=False))


if __name__ == '__main__':
    main()
