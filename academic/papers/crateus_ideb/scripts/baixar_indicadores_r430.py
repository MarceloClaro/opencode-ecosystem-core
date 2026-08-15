#!/usr/bin/env python3
"""Coleta R430 — marcadores socioeconômicos NÃO convencionais por município
(microrregião do Sertão de Crateús, 9 municípios).

Fontes (todas IBGE, nível municipal N6, período 2022):
- Censo Demográfico 2022 (universo): 9606 (sexo), 9605 (cor/raça), 9928 (paredes),
  9940 (densidade dormitório).
- Censo Demográfico 2022 (amostra — "Resultados preliminares da amostra", IBGE
  2024-2025): 10261 (posição na ocupação), 10264 (ocupação + previdência),
  10266 (atividade), 10268 (nível de ocupação), 10280/10295/10296 (rendimento),
  10056/10061/10062 (educação).

SPEC-935-R430-crateus-marcadores-nao-convencionais.md
Saída: data/processed/indicadores_r430.json + manifest_r430.json
"""

import json
import time
import urllib.request
import gzip
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
PROC = PAPER / "data" / "processed"

MUNICIPIOS = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]

# (nome, tabela, variavel, classificacoes {class_id: [cats]}, operacao)
# operacoes:
#   variavel        -> valor direto
#   proporcao       -> vals[1]/vals[0]*100 (total, categoria)
#   soma_proporcao  -> soma(vals[1:])/vals[0]*100 (total, varias categorias)
#   soma_percentual -> soma(vals[1:]) (percentuais de distribuicao)
COLETA = [
    # Gênero e raça (universo)
    ("mulheres_pct", 9606, "93", {"2": ["6794", "5"]}, "proporcao"),
    ("pretos_pardos_pct", 9605, "93", {"86": ["95251", "2777", "2779"]}, "soma_proporcao"),
    # Trabalho (amostra)
    ("nivel_ocupacao_pct", 10268, "675", {}, "variavel"),
    ("ocup_carteira_pct", 10261, "4090", {"11913": ["96165", "31722", "79367", "79372", "79375"]}, "soma_proporcao"),
    ("ocup_sem_carteira_pct", 10261, "4090", {"11913": ["96165", "31723", "79368", "79373", "79376"]}, "soma_proporcao"),
    ("ocup_conta_propria_pct", 10261, "4090", {"11913": ["96165", "79378"]}, "proporcao"),
    ("ocup_empregador_pct", 10261, "4090", {"11913": ["96165", "79377"]}, "proporcao"),
    ("ocup_domestico_pct", 10261, "4090", {"11913": ["96165", "31724"]}, "proporcao"),
    ("ocup_setor_publico_pct", 10261, "4090", {"11913": ["96165", "31727"]}, "proporcao"),
    ("ocup_familiar_aux_pct", 10261, "4090", {"11913": ["96165", "31731"]}, "proporcao"),
    ("contribuintes_previdencia_pct", 10264, "4090", {"526": ["15349", "15350"]}, "proporcao"),
    # Profissões (grandes grupos de ocupação, amostra)
    ("ocup_diretores_pct", 10264, "4090", {"12064": ["100971", "12630"]}, "proporcao"),
    ("ocup_profissionais_pct", 10264, "4090", {"12064": ["100971", "12631"]}, "proporcao"),
    ("ocup_tecnicos_pct", 10264, "4090", {"12064": ["100971", "12632"]}, "proporcao"),
    ("ocup_servicos_vendas_pct", 10264, "4090", {"12064": ["100971", "12634"]}, "proporcao"),
    ("ocup_agropec_pct", 10264, "4090", {"12064": ["100971", "12635"]}, "proporcao"),
    ("ocup_elementares_pct", 10264, "4090", {"12064": ["100971", "12638"]}, "proporcao"),
    # Atividade econômica (amostra)
    ("ativ_agropec_pct", 10266, "4090", {"11805": ["95371", "12640"]}, "proporcao"),
    ("ativ_industria_pct", 10266, "4090", {"11805": ["95371", "12641", "12642", "12643", "12644"]}, "soma_proporcao"),
    ("ativ_construcao_pct", 10266, "4090", {"11805": ["95371", "95377"]}, "proporcao"),
    ("ativ_comercio_pct", 10266, "4090", {"11805": ["95371", "12645"]}, "proporcao"),
    ("ativ_admin_pub_pct", 10266, "4090", {"11805": ["95371", "95383"]}, "proporcao"),
    ("ativ_educacao_pct", 10266, "4090", {"11805": ["95371", "95384"]}, "proporcao"),
    ("ativ_saude_pct", 10266, "4090", {"11805": ["95371", "12651"]}, "proporcao"),
    ("ativ_serv_domestico_pct", 10266, "4090", {"11805": ["95371", "95387"]}, "proporcao"),
    # Renda e pobreza (amostra)
    ("rend_domiciliar_percapita", 10295, "13431", {}, "variavel"),
    ("rend_trabalho_medio", 10280, "13536", {}, "variavel"),
    ("pobreza_renda_1sm_pct", 10296, "13604", {"386": ["9680", "9681", "9682", "9683"]}, "soma_proporcao"),
    # Educação e formação (amostra)
    ("anos_estudo_11mais", 10062, "13285", {}, "variavel"),
    ("superior_completo_pct", 10061, "2667", {"1568": ["120704", "99713"]}, "proporcao"),
    ("taxa_frequencia_escolar", 10056, "3795", {}, "variavel"),
    # Habitação (universo)
    ("alvenaria_pct", 9928, "1000381", {"137": ["13233", "73073", "12194"]}, "soma_proporcao"),
    ("domicilio_densidade_pct", 9940, "382", {"1975": ["73086", "73090"]}, "proporcao"),
]

FAMILIAS = {
    "mulheres_pct": "Gênero",
    "pretos_pardos_pct": "Raça/etnia",
    "nivel_ocupacao_pct": "Trabalho",
    "ocup_carteira_pct": "Trabalho",
    "ocup_sem_carteira_pct": "Trabalho",
    "ocup_conta_propria_pct": "Trabalho",
    "ocup_empregador_pct": "Trabalho",
    "ocup_domestico_pct": "Trabalho",
    "ocup_setor_publico_pct": "Trabalho",
    "ocup_familiar_aux_pct": "Trabalho",
    "contribuintes_previdencia_pct": "Trabalho",
    "ocup_diretores_pct": "Profissões",
    "ocup_profissionais_pct": "Profissões",
    "ocup_tecnicos_pct": "Profissões",
    "ocup_servicos_vendas_pct": "Profissões",
    "ocup_agropec_pct": "Profissões",
    "ocup_elementares_pct": "Profissões",
    "ativ_agropec_pct": "Atividade econômica",
    "ativ_industria_pct": "Atividade econômica",
    "ativ_construcao_pct": "Atividade econômica",
    "ativ_comercio_pct": "Atividade econômica",
    "ativ_admin_pub_pct": "Atividade econômica",
    "ativ_educacao_pct": "Atividade econômica",
    "ativ_saude_pct": "Atividade econômica",
    "ativ_serv_domestico_pct": "Atividade econômica",
    "rend_domiciliar_percapita": "Renda",
    "rend_trabalho_medio": "Renda",
    "pobreza_renda_1sm_pct": "Condições de vida",
    "anos_estudo_11mais": "Educação/formação",
    "superior_completo_pct": "Educação/formação",
    "taxa_frequencia_escolar": "Educação/formação",
    "alvenaria_pct": "Habitação",
    "domicilio_densidade_pct": "Habitação",
}

ETIQUETAS = {
    "mulheres_pct": "Mulheres na população (%)",
    "pretos_pardos_pct": "Pretos e pardos na população (%)",
    "nivel_ocupacao_pct": "Nível de ocupação 10+ (%)",
    "ocup_carteira_pct": "Ocupados com carteira (%)",
    "ocup_sem_carteira_pct": "Ocupados sem carteira (%)",
    "ocup_conta_propria_pct": "Conta própria (%)",
    "ocup_empregador_pct": "Empregadores (%)",
    "ocup_domestico_pct": "Trabalhadores domésticos (%)",
    "ocup_setor_publico_pct": "Empregados no setor público (%)",
    "ocup_familiar_aux_pct": "Trabalhadores familiares auxiliares (%)",
    "contribuintes_previdencia_pct": "Contribuintes da previdência (%)",
    "ocup_diretores_pct": "Diretores e gerentes (%)",
    "ocup_profissionais_pct": "Profissionais ciências/intelectuais (%)",
    "ocup_tecnicos_pct": "Técnicos de nível médio (%)",
    "ocup_servicos_vendas_pct": "Serviços e vendedores (%)",
    "ocup_agropec_pct": "Ocupados agropecuária (%)",
    "ocup_elementares_pct": "Ocupações elementares (%)",
    "ativ_agropec_pct": "Atividade: agropecuária (%)",
    "ativ_industria_pct": "Atividade: indústria (%)",
    "ativ_construcao_pct": "Atividade: construção (%)",
    "ativ_comercio_pct": "Atividade: comércio (%)",
    "ativ_admin_pub_pct": "Atividade: administração pública (%)",
    "ativ_educacao_pct": "Atividade: educação (%)",
    "ativ_saude_pct": "Atividade: saúde (%)",
    "ativ_serv_domestico_pct": "Atividade: serviços domésticos (%)",
    "rend_domiciliar_percapita": "Renda domiciliar per capita (R$)",
    "rend_trabalho_medio": "Rendimento médio do trabalho (R$)",
    "pobreza_renda_1sm_pct": "Renda per capita até 1 SM (%)",
    "anos_estudo_11mais": "Anos de estudo (11+)",
    "superior_completo_pct": "18+ com superior completo (%)",
    "taxa_frequencia_escolar": "Taxa bruta de frequência escolar",
    "alvenaria_pct": "Domicílios em alvenaria (%)",
    "domicilio_densidade_pct": "Moradores >3/dormitório (%)",
}


def _get(url: str, tentativas: int = 4):
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
                if data[:2] == b"\x1f\x8b":
                    data = gzip.decompress(data)
            return json.loads(data)
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"falha ao obter {url}: {ultimo}")


def _num(v) -> float | None:
    if v is None or v == "-":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def _valor_municipio(resp, operacao) -> dict:
    por_mun: dict[int, list] = {}
    for bloco in resp:
        for res in bloco.get("resultados", []):
            for serie in res.get("series", []):
                mun_id = int(serie["localidade"]["id"])
                valor = list(serie["serie"].values())[0]
                por_mun.setdefault(mun_id, []).append(_num(valor))
    out = {}
    for mun_id, vals in por_mun.items():
        if operacao == "variavel":
            out[mun_id] = vals[0]
        elif operacao == "proporcao":
            total, cat = vals[0], vals[1]
            out[mun_id] = (cat / total * 100.0) if (total and total > 0) else None
        elif operacao == "soma_proporcao":
            total = vals[0]
            soma = sum(v for v in vals[1:] if v is not None)
            out[mun_id] = (soma / total * 100.0) if (total and total > 0) else None
        elif operacao == "soma_percentual":
            out[mun_id] = sum(v for v in vals[1:] if v is not None)
    return out


def coletar() -> tuple[dict, list]:
    dados: dict[int, dict] = {}
    manifest = []
    for nome, tabela, variavel, classificacoes, operacao in COLETA:
        loc = ",".join(str(m) for m in MUNICIPIOS)
        cls = "&".join(f"classificacao={c}[{','.join(v)}]" for c, v in classificacoes.items())
        url = (f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/2022"
               f"/variaveis/{variavel}?localidades=N6[{loc}]")
        if cls:
            url += f"&{cls}"
        try:
            resp = _get(url)
            valores = _valor_municipio(resp, operacao)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            valores = {}
            status = f"falha: {type(e).__name__} {str(e)[:80]}"
        for mun_id in MUNICIPIOS:
            dados.setdefault(mun_id, {})[nome] = valores.get(mun_id)
        manifest.append({
            "indicador": nome, "tabela": tabela, "variavel": variavel,
            "classificacoes": classificacoes, "periodo": "2022", "url": url,
            "status": status,
        })
        n_ok = sum(1 for v in valores.values() if v is not None)
        print(f"  {status.split(':')[0]} {nome}: {n_ok}/9", flush=True)
    return dados, manifest


def main() -> int:
    dados, manifest = coletar()
    out = []
    for mun_id in MUNICIPIOS:
        out.append({"cod_mun": mun_id, **dados.get(mun_id, {})})
    (PROC / "indicadores_r430.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROC / "manifest_r430.json").write_text(
        json.dumps({
            "ciclo": "R430",
            "fonte": "IBGE SIDRA v3 — Censo Demográfico 2022 (universo e resultados preliminares da amostra)",
            "n_municipios": len(MUNICIPIOS),
            "n_indicadores": len(COLETA),
            "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "coletas": manifest,
            "familia_por_indicador": FAMILIAS,
            "etiquetas": ETIQUETAS,
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Total: {len(out)} municípios × {len(COLETA)} indicadores")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
