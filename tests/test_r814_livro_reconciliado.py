"""R814: inventário derivado de fontes e geração sem duplicar seções curadas."""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load(filename):
    spec = importlib.util.spec_from_file_location(filename.replace(".", "_"),
                                                 ROOT / "livro-core" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_activation_generator_preserves_existing_reviewed_section(tmp_path, monkeypatch):
    generator = _load("gen_mod14_ativacao.py")
    entry = generator.MODULES[0]
    path = tmp_path / entry[0]
    reviewed = "\\section[Ativação e cálculo]{Ativação revisada}\nConteúdo revisado e limites.\n"
    path.write_text(reviewed, encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "MODULES", [entry])

    generator.main()
    first = path.read_text(encoding="utf-8")
    generator.main()
    second = path.read_text(encoding="utf-8")

    assert first.count("\\section[Ativação e cálculo]") == 1
    assert "Conteúdo revisado e limites." in first
    assert first.count(generator.MARKER) == 1
    assert first == second


def test_inventory_uses_configuration_and_document_sources(tmp_path):
    generator = _load("gen_inventario.py")
    (tmp_path / "specs").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "livro-core").mkdir()
    (tmp_path / "opencode.json").write_text(json.dumps({
        "agent": {"primary": {}, "specialist": {}},
        "mcp": {"local": {}}, "command": {"one": {}, "two": {}, "three": {}},
    }), encoding="utf-8")
    (tmp_path / "specs/SPEC-935-R1.md").write_text("spec", encoding="utf-8")
    (tmp_path / "tests/test_r1.py").write_text("test", encoding="utf-8")
    (tmp_path / "livro-core/mod-01.tex").write_text(
        "\\citref{a}{10.1/a}{b}{c}{d}\n\\citref{e}{10.1/e}{f}{g}{h}\n",
        encoding="utf-8")
    (tmp_path / "livro-core/mod-11-apendices.tex").write_text(
        "\\begin{referencia}source\\end{referencia}\n", encoding="utf-8")

    report = generator.collect_inventory(tmp_path)

    assert report["counts"] == {"agents": 2, "mcp_servers": 1, "commands": 3,
                                "specs": 1, "round_specs": 1, "round_test_files": 1,
                                "references": 1, "citation_calls": 2,
                                "condensed_cards": 0}
    assert report["verification"] == "source_inventory_only"
    assert report["sources"]["opencode.json"]["sha256"]


def test_generated_catalog_matches_authoritative_generator(tmp_path, monkeypatch):
    generator = _load("gen_mod10.py")
    output = tmp_path / "catalog.tex"
    monkeypatch.setattr(generator, "OUT", str(output))

    generator.main()

    assert output.read_text(encoding="utf-8") == (
        ROOT / "livro-core/mod-10-catalogo.tex").read_text(encoding="utf-8")


@pytest.mark.parametrize("current,literal", [(255, "255 fichas"), (212, "212 fichas")])
def test_inventory_gate_accepts_historical_number_when_current(tmp_path, monkeypatch, current, literal):
    gate = _load_inventory_gate(tmp_path, monkeypatch, current, literal)
    gate.test_ac6_inventario_citado_bate_com_o_runtime()


@pytest.mark.parametrize("current,literal", [(254, "255 fichas"), (255, "212 fichas"),
                                             (254, "100/255")])
def test_inventory_gate_rejects_obsolete_literal(tmp_path, monkeypatch, current, literal):
    gate = _load_inventory_gate(tmp_path, monkeypatch, current, literal)
    with pytest.raises(AssertionError, match="obsoleto"):
        gate.test_ac6_inventario_citado_bate_com_o_runtime()


def test_inventory_gate_preserves_explicitly_dated_historical_result(tmp_path, monkeypatch):
    literal = (r"\begin{resultado}\textbf{Retrato histórico de 2026-09-29.} "
               r"Antes 201/212; depois 212/212. O inventário corrente possui "
               r"\CoreAgentCount{} agentes.\end{resultado}")
    gate = _load_inventory_gate(tmp_path, monkeypatch, 255, literal)
    gate.test_ac6_inventario_citado_bate_com_o_runtime()


@pytest.mark.parametrize("literal", [
    r"\begin{resultado}Retrato histórico: 201/212.\end{resultado}",
    r"\begin{resultado}Retrato histórico de 2026-09-29: 201/212.\end{resultado}",
    r"Retrato histórico de 2026-09-29. \CoreAgentCount{} agentes. 201/212",
])
def test_inventory_gate_requires_historical_scope_date_and_current_reference(tmp_path, monkeypatch, literal):
    gate = _load_inventory_gate(tmp_path, monkeypatch, 255, literal)
    with pytest.raises(AssertionError, match="obsoleto"):
        gate.test_ac6_inventario_citado_bate_com_o_runtime()


def _load_inventory_gate(tmp_path, monkeypatch, current, literal):
    spec = importlib.util.spec_from_file_location("r618_gate_contract",
                ROOT / "tests/test_r618_catalogo_runtime_reconciliacao.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    (tmp_path / "livro-core").mkdir()
    (tmp_path / "opencode.json").write_text(json.dumps({
        "agent": {str(i): {} for i in range(current)},
    }), encoding="utf-8")
    catalog = tmp_path / "livro-core/mod-10-catalogo.tex"
    catalog.write_text(r"\textbf{" + str(current) + "} agentes\n" + literal, encoding="utf-8")
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "MOD10", catalog)
    return gate


def test_new_activation_section_contains_six_citation_fields():
    """A macro real possui seis campos, inclusive autoria/localizador."""
    generator = _load("gen_mod14_ativacao.py")
    rendered = generator.render(generator.MODULES[0])
    tail = rendered.split(r"\citref", 1)[1]
    fields = []
    position = 0
    while position < len(tail):
        while position < len(tail) and tail[position].isspace():
            position += 1
        if position >= len(tail) or tail[position] != "{":
            break
        start = position + 1
        depth = 1
        position += 1
        while position < len(tail) and depth:
            if tail[position] == "{" and tail[position - 1] != "\\":
                depth += 1
            elif tail[position] == "}" and tail[position - 1] != "\\":
                depth -= 1
            position += 1
        assert depth == 0
        fields.append(tail[start:position - 1])
    assert len(fields) == 6
    assert all(field.strip() for field in fields)
    assert "p." in fields[5]


def test_activation_generator_retires_marker_of_renamed_reviewed_section(tmp_path, monkeypatch):
    """Uma seção editorial com novo título não volta ao template histórico."""
    generator = _load("gen_mod14_ativacao.py")
    entry = generator.MODULES[0]
    path = tmp_path / entry[0]
    reviewed = (generator.MARKER + "\n\\section[Economia interna]{Economia revisada}\n"
                "Conteúdo curado e limites de interpretação.\n")
    path.write_text(reviewed, encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "MODULES", [entry])
    generator.main()
    first = path.read_text(encoding="utf-8")
    generator.main()
    assert path.read_text(encoding="utf-8") == first
    assert generator.MARKER not in first
    assert "\\section[Economia interna]" in first
    assert "Conteúdo curado e limites de interpretação." in first
    assert "\\section[Ativação e cálculo]" not in first


def test_activation_injector_respects_authoritative_catalog_generator(tmp_path, monkeypatch):
    generator = _load("gen_mod14_ativacao.py")
    entry = next(item for item in generator.MODULES if item[0] == "mod-10-catalogo.tex")
    path = tmp_path / entry[0]
    generated = "% ARQUIVO GERADO por gen_mod10.py\nCatálogo e leitura curada.\n"
    path.write_text(generated, encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "MODULES", [entry])
    generator.main()
    assert path.read_text(encoding="utf-8") == generated


def test_mcp_inventory_reports_declarations_without_exposing_connection_parameters():
    generator = _load("gen_inventario.py")
    config = {"mcp": {
        "first": {"type": "local", "command": ["python", "server.py"],
                  "environment": {"TOKEN": "secret-not-for-book"}},
        "second": {"type": "remote", "enabled": False,
                   "url": "https://example.test/?token=secret-not-for-book"},
    }}
    block = generator.render_mcp_inventory(config)
    assert r"\pth{first}" in block and r"\pth{second}" in block
    assert "local" in block and "remote" in block
    assert "desabilitado" in block
    assert "secret-not-for-book" not in block
    assert "não comprova" in block


def _asset_inventory_checkout(root):
    (root / "livro-core").mkdir(parents=True)
    (root / "specs").mkdir()
    (root / "tests").mkdir()
    (root / "opencode.json").write_text(json.dumps({"agent": {}, "mcp": {}, "command": {}}))
    (root / "livro-core/mod-11-apendices.tex").write_text("Bibliografia da fixture.")
    return root


def test_inventory_expands_explicit_asset_directory_without_changing_counts_or_existing_hashes(tmp_path):
    import hashlib
    generator = _load("gen_inventario.py")
    root = _asset_inventory_checkout(tmp_path / "root")
    direct = root / "source.py"
    direct.write_bytes(b"source-original\n")
    module = root / "livro-core/mod-23.tex"
    module.write_text(r"\fontecore{source.py}{fonte-direta}")
    baseline = generator.collect_inventory(root)
    assets = root / "assets"
    (assets / "nested").mkdir(parents=True)
    payloads = {"assets/z.png": b"PNG-fixture", "assets/a.pptx": b"PPTX-fixture",
                "assets/nested/mapping.json": b'{"fixture":true}', "assets/.manifest": b"manifest"}
    for name, data in payloads.items():
        (root / name).write_bytes(data)
    (root / "unmentioned").mkdir()
    (root / "unmentioned/no-evidence.png").write_bytes(b"not-cited")
    module.write_text(r"\fontecore{source.py}{fonte-direta}" + "\n" + r"\fontecore{assets}{kit-local}")
    report = generator.collect_inventory(root)
    assert report["counts"] == baseline["counts"]
    assert report["sources"]["source.py"] == baseline["sources"]["source.py"]
    assert report["sources"]["opencode.json"] == baseline["sources"]["opencode.json"]
    for name, data in payloads.items():
        assert report["sources"][name]["sha256"] == hashlib.sha256(data).hexdigest()
    assert "unmentioned/no-evidence.png" not in report["sources"]
    assert list(report["sources"]) == sorted(report["sources"])
    assert generator.collect_inventory(root) == report


def test_asset_inventory_never_reads_file_or_directory_links_outside_workspace(tmp_path, monkeypatch):
    import hashlib
    generator = _load("gen_inventario.py")
    root = _asset_inventory_checkout(tmp_path / "root")
    assets = root / "assets"
    assets.mkdir()
    (assets / "valid.png").write_bytes(b"local-fixture")
    outside = tmp_path / "outside"
    outside.mkdir()
    external = outside / "external.png"
    external.write_bytes(b"outside-fixture-must-not-be-read")
    try:
        (assets / "escape-file.png").symlink_to(external)
        (assets / "escape-dir").symlink_to(outside, target_is_directory=True)
        (root / "escape-root").symlink_to(outside, target_is_directory=True)
        (assets / "cycle").symlink_to(assets, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("A plataforma desta fixture não permite criar links simbólicos.")
    (root / "livro-core/mod-24.tex").write_text(
        r"\fontecore{assets}{kit-local}" + "\n" + r"\fontecore{escape-root}{fora}" +
        "\n" + r"\fontecore{../outside/external.png}{arquivo-fora}")
    read_bytes = Path.read_bytes
    def guarded_read(path):
        if path.resolve() == external.resolve():
            pytest.fail("Inventário leu um asset fora do workspace.")
        return read_bytes(path)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    report = generator.collect_inventory(root)
    assert report["sources"]["assets/valid.png"]["sha256"] == hashlib.sha256(b"local-fixture").hexdigest()
    assert not any("escape" in path or "cycle" in path or "external" in path for path in report["sources"])



def test_book_code_labels_preserve_command_spaces(tmp_path):
    """A extração do PDF precisa conservar argumentos de comandos copiáveis."""
    import shutil
    import subprocess

    if not shutil.which("pdflatex") or not shutil.which("pdftotext"):
        pytest.skip("Ferramentas TeX/PDF locais indisponíveis para conferência tipográfica")
    source = tmp_path / "command-spaces.tex"
    macro = (ROOT / "livro-core/macros.tex").as_posix()
    import re
    inventory_command = re.search(r"\\pth\{(python3 livro-core/gen[^}]+)\}", (ROOT / "livro-core/mod-11-apendices.tex").read_text())[1]
    source.write_text(
        r"\documentclass[a4paper,11pt]{book}" + "\n"
        + r"\input{" + macro + "}\n"
        + r"\begin{document}" + "\n"
        + r"\pth{python3 -m marceloclaro.cli browser}" + "\n\n"
        + r"\cod{make install}" + "\n"
        + r"\pth{" + inventory_command + "}\n"
        + r"\end{document}", encoding="utf-8")
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         "-output-directory", str(tmp_path), str(source)],
        cwd=ROOT / "livro-core", capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stdout[-3000:]
    text = subprocess.check_output(
        ["pdftotext", "-layout", str(source.with_suffix(".pdf")), "-"], text=True)
    normalized = " ".join(text.split())
    assert "python3 -m marceloclaro.cli browser" in normalized
    assert "make install" in normalized
    assert "python3 livro-core/gen_inventario.py" in normalized
