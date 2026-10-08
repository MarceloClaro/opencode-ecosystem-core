# -*- coding: utf-8 -*-
"""SPEC-935-R711 — Registro auditado de laboratórios GitHub para pesquisador polímata.

Camada de governança, sem rede/subprocesso/LLM.

Separação arquitetural:
- Orquestração pertence ao orquestrador `marceloclaro` via Blackboard (A2A).
- MCP fornece ferramentas e contexto.
- A2A trata colaboração entre agentes.
- Artefatos de terceiros importados são inertes: este módulo nunca clona,
  instala, constrói ou executa hooks/scripts externos. Clonagem pertence ao
  operador com consentimento explícito, fora do gate hermético.

Recuperação lexical de metadados não equivale a treinamento de modelo nem a
melhoria cognitiva medida. Nenhum rótulo aqui possui autoridade epistêmica
automática.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os

SPEC_ID = "SPEC-935-R711"
GERADOR = "marceloclaro"

ALLOWLIST: list[dict] = [
    {
        "id": "z3",
        "url": "https://github.com/Z3Prover/z3",
        "tipo_raciocinio": ["dedutivo", "formal", "smt"],
        "uso_polimata": "Prova de teoremas e checagem de consistência lógica de protocolos.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "sympy",
        "url": "https://github.com/sympy/sympy",
        "tipo_raciocinio": ["dedutivo", "simbolico"],
        "uso_polimata": "Derivação simbólica e apêndices matemáticos auditáveis.",
        "licenca": "BSD",
        "status_licenca": "ok",
    },
    {
        "id": "reasonkit-core",
        "url": "https://github.com/reasonkit/reasonkit-core",
        "tipo_raciocinio": ["dedutivo", "auditoria"],
        "uso_polimata": "Padrão prompt-em-protocolo com trilha auditável.",
        "licenca": "Apache-2.0 (a confirmar)",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "scireason",
        "url": "https://github.com/InternScience/SciReason",
        "tipo_raciocinio": ["indutivo", "benchmark"],
        "uso_polimata": "Régua multidisciplinar de raciocínio científico sobre OpenCompass.",
        "licenca": "Apache-2.0",
        "status_licenca": "ok",
    },
    {
        "id": "scir",
        "url": "https://github.com/idiap/SciR",
        "tipo_raciocinio": ["dedutivo", "indutivo", "abdutivo-causal"],
        "uso_polimata": "Benchmark multi-documento com verdade verificável e distratores.",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "cot-evo",
        "url": "https://github.com/Irving-Feng/CoT-Evo",
        "tipo_raciocinio": ["indutivo", "evolutivo"],
        "uso_polimata": "Destilação evolutiva de CoT compacta para ciência (química/bio).",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "abduction-syllogism",
        "url": "https://github.com/kmineshima/abduction-syllogism-llm",
        "tipo_raciocinio": ["abdutivo", "dedutivo"],
        "uso_polimata": "Dataset que separa gerar hipótese de provar consequência.",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "research-reasoning-engine",
        "url": "https://github.com/Aswinesag/research-reasoning-engine",
        "tipo_raciocinio": ["causal", "abdutivo"],
        "uso_polimata": "Grafo causal esparso com hipótese fundamentada e controle de especulação.",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "pgmpy",
        "url": "https://github.com/pgmpy/pgmpy",
        "tipo_raciocinio": ["causal", "probabilistico", "bayesiano"],
        "uso_polimata": "Descoberta causal, inferência intervencional e simulação sob do(X).",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "dowhy",
        "url": "https://github.com/py-why/dowhy",
        "tipo_raciocinio": ["causal", "contrafactual"],
        "uso_polimata": "Modelagem explícita + refutadores placebo/confundidor.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "causalpy",
        "url": "https://github.com/pymc-labs/CausalPy",
        "tipo_raciocinio": ["causal", "bayesiano", "quase-experimental"],
        "uso_polimata": "DID, controle sintético, RDD, ITS, VI com HDI bayesiano.",
        "licenca": "Apache-2.0",
        "status_licenca": "ok",
    },
    {
        "id": "causalnex",
        "url": "https://github.com/mckinsey/causalnex",
        "tipo_raciocinio": ["causal", "bayesiano"],
        "uso_polimata": "Redes bayesianas what-if com conhecimento de domínio.",
        "licenca": "Apache-2.0",
        "status_licenca": "ok",
    },
    {
        "id": "prisma",
        "url": "https://github.com/Proportione/prisma",
        "tipo_raciocinio": ["sintese-evidencias", "sistematico"],
        "uso_polimata": "Revisão sistemática PRISMA 2020 + MMAT com log de auditoria.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "prisma-traice",
        "url": "https://github.com/cqh4046/PRISMA-trAIce",
        "tipo_raciocinio": ["sintese-evidencias", "transparencia-ia"],
        "uso_polimata": "Checklist de relato transparente de IA em revisão sistemática.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "evidence-synthesis",
        "url": "https://github.com/OHDSI/EvidenceSynthesis",
        "tipo_raciocinio": ["sintese-evidencias", "meta-analise"],
        "uso_polimata": "Meta-análise multi-site bayesiana e forest plots.",
        "licenca": "Apache-2.0",
        "status_licenca": "ok",
    },
    {
        "id": "ai-scientist",
        "url": "https://github.com/SakanaAI/AI-Scientist",
        "tipo_raciocinio": ["autonomo", "indutivo"],
        "uso_polimata": "Esqueleto fim-a-fim ideia-experimento-escrita sob supervisão; exige disclosure de geração (AI Scientist Clause).",
        "licenca": "AI Scientist Source Code License v1.0 (custom restritiva, revisão jurídica exigida)",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "aiscientist-filebus",
        "url": "https://github.com/AweAI-Team/AiScientist",
        "tipo_raciocinio": ["autonomo", "orquestracao"],
        "uso_polimata": "Coordenação File-as-Bus para horizontes longos, trilhas paper/mle.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
    {
        "id": "agent-laboratory",
        "url": "https://github.com/SamuelSchmidgall/AgentLaboratory",
        "tipo_raciocinio": ["autonomo", "colaborativo"],
        "uso_polimata": "Assistente em 3 fases com AgentRxiv cumulativo supervisionado.",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "github-demo-lab",
        "url": "https://github.com/rasilab/github_demo",
        "tipo_raciocinio": ["reprodutibilidade", "laboratorio"],
        "uso_polimata": "Exemplo PLOS Biology de issues + versão + contêineres (DOI 10.1371/journal.pbio.3003029).",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "github-template-lab",
        "url": "https://github.com/rasilab/github_template",
        "tipo_raciocinio": ["reprodutibilidade", "laboratorio"],
        "uso_polimata": "Template copiável de laboratório reproduzível.",
        "licenca": "a confirmar",
        "status_licenca": "license_undeclared",
    },
    {
        "id": "repro-audit",
        "url": "https://github.com/aqibrahimbt/repro_audit",
        "tipo_raciocinio": ["auditoria", "reprodutibilidade"],
        "uso_polimata": "Gate estático seeds/hiperparâmetros/splits/dependências antes da submissão.",
        "licenca": "MIT",
        "status_licenca": "ok",
    },
]

_URLS_NORMALIZADAS = {e["url"].lower(): e["url"] for e in ALLOWLIST}


def _normalizar(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("URL deve ser texto não vazio.")
    u = url.strip()
    if not u:
        raise ValueError("URL vazia rejeitada (fail-closed).")
    if u.lower().endswith(".git"):
        u = u[: -len(".git")]
    u = u.rstrip("/")
    # Normaliza organização/repo para minúsculas no retorno canônico
    partes = u.split("/")
    if len(partes) >= 5:
        org = partes[3]
        repo = partes[4]
        u = "/".join(partes[:3] + [org.lower(), repo.lower()] + partes[5:])
    return u


def listar_labs() -> list[dict]:
    """Retorna cópia profunda da allowlist (imutável ao chamador)."""
    return copy.deepcopy(ALLOWLIST)


def validar_url(url: str) -> str:
    """Fail-closed: aceita apenas https://github.com/<org>/<repo> da allowlist."""
    u = _normalizar(url)
    if not u.startswith("https://github.com/"):
        raise ValueError(f"Fora do GitHub HTTPS: {url!r}")
    resto = u[len("https://github.com/") :]
    if "/" not in resto or not resto.split("/")[0] or not resto.split("/")[1]:
        raise ValueError(f"Formato org/repo inválido: {url!r}")
    if len(resto.split("/")) != 2:
        raise ValueError(f"Apenas org/repo raiz é permitido: {url!r}")
    chave = u.lower()
    if chave not in _URLS_NORMALIZADAS:
        raise ValueError(f"Fora da allowlist R711: {url!r}")
    return _URLS_NORMALIZADAS[chave].lower() if False else u


def gerar_manifesto(destino_dir: str) -> dict:
    """Escreve labs_manifest.json auditável, sem rede. Retorna recibo."""
    if not destino_dir or not str(destino_dir).strip():
        raise ValueError("destino_dir vazio (fail-closed).")
    os.makedirs(destino_dir, exist_ok=True)
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entradas = []
    for lab in ALLOWLIST:
        entradas.append(
            {
                "id": lab["id"],
                "url": lab["url"],
                "sha256_url": hashlib.sha256(lab["url"].encode("utf-8")).hexdigest(),
                "tipo_raciocinio": list(lab["tipo_raciocinio"]),
                "uso_polimata": lab["uso_polimata"],
                "licenca": lab["licenca"],
                "status_licenca": lab["status_licenca"],
                "commit_pin": None,
            }
        )
    payload = {
        "spec_id": SPEC_ID,
        "gerado_em": agora,
        "gerador": GERADOR,
        "total": len(entradas),
        "entradas": entradas,
        "nota": "Manifesto de curadoria; clonagem e pinagem viva pertencem ao operador.",
    }
    alvo = os.path.join(destino_dir, "labs_manifest.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return {"ok": True, "manifesto": alvo, "total": len(entradas)}


def _sha256_arquivo(caminho: str) -> str | None:
    try:
        with open(caminho, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except (OSError, FileNotFoundError):
        return None


def verificar_clones(base_dir: str) -> dict:
    """Audita diretório local sem subprocesso: existe/HEAD/hash. Ausente=false."""
    if not base_dir or not str(base_dir).strip():
        raise ValueError("base_dir vazio (fail-closed).")
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entradas = []
    for lab in ALLOWLIST:
        partes = lab["url"].rstrip("/").split("/")
        org, repo = partes[-2].lower(), partes[-1].lower()
        candidatos = [
            os.path.join(base_dir, f"{org}__{repo}"),
            os.path.join(base_dir, repo),
        ]
        achado = next((c for c in candidatos if os.path.isdir(c)), None)
        if achado is None:
            entradas.append(
                {
                    "id": lab["id"],
                    "url": lab["url"],
                    "existe": False,
                    "HEAD": None,
                    "sha256_readme_ou_gitignore": None,
                }
            )
            continue
        head_path = os.path.join(achado, ".git", "HEAD")
        head = None
        try:
            with open(head_path, "r", encoding="utf-8", errors="strict") as fh:
                head = fh.read().strip() or None
        except (OSError, FileNotFoundError, UnicodeDecodeError):
            head = None
        h = _sha256_arquivo(os.path.join(achado, "README.md"))
        if h is None:
            h = _sha256_arquivo(os.path.join(achado, ".gitignore"))
        entradas.append(
            {
                "id": lab["id"],
                "url": lab["url"],
                "existe": True,
                "diretorio": achado,
                "HEAD": head,
                "sha256_readme_ou_gitignore": h,
            }
        )
    return {
        "spec_id": SPEC_ID,
        "gerador": GERADOR,
        "auditado_em": agora,
        "base_dir": base_dir,
        "total": len(entradas),
        "entradas": entradas,
        "audit_trail": f"{GERADOR} auditou {len(entradas)} labs em {agora} sem rede/subprocesso.",
    }


def rotulo_epistemico() -> dict:
    """Guarda anti-overclaim: todo lab nasce candidato, nunca aprovado."""
    return {
        "rotulo": "candidato_a_inspecao",
        "exige_validacao_externa": True,
        "nota": "Licença, manutenção, testes e aderência ao desenho exigem checagem viva.",
    }
