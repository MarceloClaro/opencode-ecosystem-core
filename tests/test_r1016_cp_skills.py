"""R1016 — pacote de skills audiovisuais (sete cp-* e três meia-*)."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".claude" / "skills"

CP_SKILLS = {
    "cp-extratora-de-referencia": (
        "observado",
        "inferido",
        "nao_verificavel",
        "referencia-de-edicao.md",
        "mapa-de-cenas.csv",
        "receita-visual.json",
        "prompt-de-recriacao.txt",
    ),
    "cp-estilo-por-referencia": (
        "gramatica visual",
        "identidade",
        "copiar",
        "referencia",
    ),
    "cp-direcao-de-edicao": (
        "unidades de sentido",
        "foco",
        "continuidade",
    ),
    "cp-apresentador-em-cena": (
        "rosto",
        "gestos",
        "avatar",
        "recorte alfa",
    ),
    "cp-lettering-com-hierarquia": (
        "hierarquia",
        "legenda",
        "licenca",
        "tempo de leitura",
    ),
    "cp-motion-explicativo": (
        "estado inicial",
        "estado final",
        "dados",
        "causalidade",
    ),
    "cp-variacoes-controladas": (
        "base aprovada",
        "uma variavel",
        "matriz",
        "manifesto",
        "nao medido",
    ),
}

MEIA_SKILLS = {
    "meia-briefing-de-edicao": (
        "briefing",
        "sem repetir",
        "oferta",
        "amostra",
    ),
    "meia-legendas-e-enquadramento": (
        "fala real",
        "sincron",
        "proporcao",
        "area de legenda",
        "nao comprovam sincronizacao",
    ),
    "meia-revisao-economia": (
        "intervalo",
        "causa",
        "orcamento",
        "nao afirme",
        "preserve o original",
    ),
}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(without_marks.casefold().split())


def skill_text(slug: str) -> str:
    path = SKILLS_ROOT / slug / "SKILL.md"
    assert path.is_file(), f"skill ausente: {path}"
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    lines = text.splitlines()
    assert lines and lines[0] == "---"
    closing = lines.index("---", 1)
    return "\n".join(lines[1:closing])


def assert_frontmatter(slug: str, text: str) -> None:
    data = yaml.safe_load(frontmatter(text))
    assert isinstance(data, dict), f"{slug}: frontmatter não é um mapa YAML"
    assert data.get("name") == slug
    description = data.get("description")
    assert isinstance(description, str) and len(description.strip()) >= 24


@pytest.mark.parametrize("slug", sorted(CP_SKILLS))
def test_cp_package_structure(slug: str) -> None:
    directory = SKILLS_ROOT / slug
    text = skill_text(slug)
    assert_frontmatter(slug, text)
    agent_metadata = directory / "agents" / "openai.yaml"
    assert agent_metadata.is_file()
    agent_data = yaml.safe_load(agent_metadata.read_text(encoding="utf-8"))
    assert isinstance(agent_data, dict) and isinstance(agent_data.get("interface"), dict)
    references = sorted((directory / "references").glob("*.md"))
    assert references, f"{slug} não possui arquivos de referência"
    for match in re.finditer(r"\]\((references/[^)]+)\)", text):
        assert (directory / match.group(1)).is_file(), f"link quebrado: {match.group(1)}"


@pytest.mark.parametrize("slug", sorted(MEIA_SKILLS))
def test_meia_package_structure(slug: str) -> None:
    text = skill_text(slug)
    assert_frontmatter(slug, text)
    assert "## Salvaguardas" in text


@pytest.mark.parametrize(("slug", "phrases"), sorted(CP_SKILLS.items()))
def test_cp_skill_contract(slug: str, phrases: tuple[str, ...]) -> None:
    body = normalize(skill_text(slug))
    missing = [phrase for phrase in phrases if normalize(phrase) not in body]
    assert not missing, f"{slug} não cobre: {missing}"


@pytest.mark.parametrize(("slug", "phrases"), sorted(MEIA_SKILLS.items()))
def test_meia_skill_contract(slug: str, phrases: tuple[str, ...]) -> None:
    body = normalize(skill_text(slug))
    missing = [phrase for phrase in phrases if normalize(phrase) not in body]
    assert not missing, f"{slug} não cobre: {missing}"


def test_shared_safety_contract() -> None:
    for slug in sorted({*CP_SKILLS, *MEIA_SKILLS}):
        body = normalize(skill_text(slug))
        assert "autoriza" in body, f"{slug}: autorização não explícita"
        assert "preserve os arquivos originais" in body, f"{slug}: preservação dos originais ausente"
        assert "nao sobrescreva" in body, f"{slug}: proibição de sobrescrita ausente"
        assert "nao envie" in body, f"{slug}: proibição de envio externo ausente"
        assert "servicos externos" in body, f"{slug}: limite de serviço externo ausente"
        assert "autorizacao especifica" in body, f"{slug}: autorização específica ausente"
        assert "licenca" in body or "direito" in body, f"{slug}: direitos/licença ausentes"
        assert "## salvaguardas adicionais" in body, f"{slug}: seção de salvaguardas ausente"


def test_relative_markdown_links_resolve() -> None:
    link_pattern = re.compile(r"\]\(([^)\s]+)\)")
    for slug in sorted({*CP_SKILLS, *MEIA_SKILLS}):
        for path in sorted((SKILLS_ROOT / slug).rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                local = target.split("#", 1)[0].split("?", 1)[0]
                if not local:
                    continue
                resolved = (path.parent / local).resolve()
                assert resolved.is_file(), f"link relativo quebrado em {path}: {target}"


def test_text_only_and_no_personal_data() -> None:
    email = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
    cpf = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
    secret = re.compile(r"\b(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b")
    for slug in sorted({*CP_SKILLS, *MEIA_SKILLS}):
        directory = SKILLS_ROOT / slug
        files = [path for path in directory.rglob("*") if path.is_file()]
        assert files
        for path in files:
            assert path.suffix in {".md", ".yaml"}, f"arquivo não textual: {path}"
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for forbidden in ("licenciado para", "@gmail.com", "cpf "):
                assert forbidden not in lowered, f"dado pessoal em {path}"
            assert not email.search(text), f"e-mail em {path}"
            assert not cpf.search(text), f"CPF em {path}"
            assert not secret.search(text), f"segredo em {path}"
