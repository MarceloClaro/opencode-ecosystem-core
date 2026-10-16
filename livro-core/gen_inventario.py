"""R814: inventário reproduzível das fontes, sem consultar provedores externos."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
BEGIN = "% BEGIN-R814-INVENTARIO"
END = "% END-R814-INVENTARIO"


def _inside_workspace(path: Path, root: Path) -> bool:
    try:
        return path.resolve().is_relative_to(root)
    except (OSError, RuntimeError):
        # Link quebrado/cíclico não fornece evidência local legível.
        return False


def _cited_files(root: Path, modules: list[Path]) -> set[Path]:
    """Expande só fontes citadas; diretórios filhos simbólicos ficam inertes."""
    files = set()
    def fail_walk(error):
        raise error
    for module in modules:
        names = re.findall(r"\\fontecore\{([^}]+)\}", module.read_text(encoding="utf-8"))
        for name in names:
            path = root / name
            if not _inside_workspace(path, root):
                continue
            if path.is_file():
                files.add(path)
            elif path.is_dir():
                for directory, children, filenames in os.walk(path, followlinks=False, onerror=fail_walk):
                    current = Path(directory)
                    children[:] = sorted(child for child in children
                                         if child not in {'.lake', '__pycache__', '.git'}
                                         and not (current / child).is_symlink())
                    for filename in sorted(filenames):
                        candidate = current / filename
                        if _inside_workspace(candidate, root) and candidate.is_file():
                            files.add(candidate)
    return files


def collect_inventory(root: Path) -> dict:
    root = Path(root).resolve()
    config_path = root / "opencode.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    modules = sorted((root / "livro-core").glob("mod-*.tex"))
    bibliography = root / "livro-core/mod-11-apendices.tex"
    condensed = root / "livro-core/mod-14-lote-categorias.tex"
    local_paths = _cited_files(root, modules)
    authoritative = {root / 'livro-core' / name for name in (
        'main.tex', 'macros.tex', 'gen_mod10.py', 'gen_mod14_ativacao.py', 'gen_inventario.py')}
    authoritative.update((root / 'livro-core/lean').glob('*.lean'))
    authoritative.update(root / name for name in (
        'livro-core/lean/lean-toolchain', 'livro-core/lean/lakefile.toml',
        'livro-core/lean/lake-manifest.json', 'scripts/verify_book_lean.py',
        'docs/VERIFICACAO_FORMAL_LIVRO_R908.md', 'docs/book-math-map-r908.json',
        'docs/PREFACIO_ASSINATURA_COGNITIVA_R909.md', 'docs/preface-sources-r909.json',
        'livro-core/gen_lean_axioms.py', 'livro-core/lean-axiomas.tex',
        'scripts/book_local_deductions.py', 'docs/DEDUCOES_LOCAIS_LIVRO_R910.md'))
    sources = {str(path.relative_to(root)): {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    } for path in sorted({config_path, *modules, *local_paths, *authoritative}) if path.is_file()}
    return {
        "counts": {
            "agents": len(config.get("agent", {})),
            "mcp_servers": len(config.get("mcp", {})),
            "commands": len(config.get("command", {})),
            "specs": len(list((root / "specs").glob("*.md"))),
            "round_specs": len(list((root / "specs").glob("SPEC-935-R*.md"))),
            "round_test_files": len(list((root / "tests").glob("test_r*.py"))),
            "references": bibliography.read_text(encoding="utf-8").count(r"\begin{referencia}"),
            "citation_calls": sum(len(re.findall(r"\\citref\{", path.read_text(encoding="utf-8")))
                                  for path in modules),
            "condensed_cards": len(re.findall(r"\\elemento\{ficha-", condensed.read_text(encoding="utf-8")))
                               if condensed.exists() else 0,
        },
        "verification": "source_inventory_only",
        "sources": sources,
        "scope": "Configuração e fontes locais; não confirma execução, desempenho ou validade científica.",
    }


def _replace_block(path: Path, block: str, anchor: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    generated = f"{BEGIN}\n{block.rstrip()}\n{END}"
    if BEGIN in text:
        if END not in text:
            raise ValueError(f"Bloco de inventário incompleto: {path}")
        text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                      lambda _: generated, text, count=1, flags=re.S)
    else:
        section = anchor or r"\section{Biblioteca de referências auditadas}"
        if section not in text:
            raise ValueError(f"Âncora do inventário ausente: {path}")
        text = text.replace(section, generated + "\n\n" + section, 1)
    path.write_text(text, encoding="utf-8")


def render_mcp_inventory(config: dict) -> str:
    """Documenta somente nomes/tipos/ativação; parâmetros de conexão ficam fora."""
    rows = []
    for name, server in sorted(config.get("mcp", {}).items()):
        kind = str(server.get("type", "não informado"))
        state = "desabilitado" if server.get("enabled") is False else "habilitado na configuração"
        rows.append(r"\pth{" + name + "} & " + kind + " & " + state + r" \\")
    return (r"\begin{resultado}" + "\n" +
            r"\textbf{Inventário corrente de declarações MCP.} Fonte: \pth{opencode.json}," + "\n" +
            r"gerada por \pth{gen_inventario.py}. Esta edição declara " +
            str(len(rows)) + " servidores.\n" +
            r"{\footnotesize\begin{tabularx}{\textwidth}{YYY}" + "\n" +
            r"\toprule Nome & Tipo declarado & Ativação declarada \\ \midrule" + "\n" +
            "\n".join(rows) + "\n" + r"\bottomrule\end{tabularx}}" + "\n" +
            "Habilitação na configuração não comprova processo iniciado, autenticação, " +
            "conectividade, descoberta de ferramentas ou operação concluída. " +
            "Comandos, URLs e variáveis de conexão não são publicados nesta tabela.\n" +
            r"\end{resultado}")


def main(root: Path = ROOT) -> dict:
    root = Path(root)
    report = collect_inventory(root)
    counts = report["counts"]
    integrations = root / "livro-core/mod-07-integracoes.tex"
    if integrations.exists():
        config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
        _replace_block(integrations, render_mcp_inventory(config), r"\section{Servidores MCP nativos}")
    macro_names = {
        "agents": "CoreAgentCount", "mcp_servers": "CoreMCPCount",
        "commands": "CoreCommandCount", "specs": "CoreSpecCount",
        "round_specs": "CoreRoundSpecCount", "round_test_files": "CoreTestSuiteCount",
        "references": "CoreReferenceCount", "citation_calls": "CoreCitationCallCount",
        "condensed_cards": "CoreCondensedCardCount",
    }
    macro_text = "% R814: gerado por gen_inventario.py; não editar à mão.\n" + "\n".join(
        f"\\newcommand{{\\{macro}}}{{{counts[key]}}}" for key, macro in macro_names.items())
    (root / "livro-core/inventario-core.tex").write_text(macro_text + "\n", encoding="utf-8")
    block = rf"""\begin{{resultado}}
\textbf{{Inventário de fontes desta edição.}} A configuração declara
\textbf{{{counts['agents']}}} agentes, \textbf{{{counts['mcp_servers']}}} servidores MCP e
\textbf{{{counts['commands']}}} comandos. O repositório contém {counts['specs']} specs,
das quais {counts['round_specs']} são da série R, e {counts['round_test_files']} arquivos
\pth{{test_r*.py}}. A biblioteca contém {counts['references']} blocos de referência;
as fontes dos módulos contêm {counts['citation_calls']} chamadas de \cod{{\string\citref}}
e {counts['condensed_cards']} fichas condensadas de categoria.
\textbf{{Como reproduzir.}} Execute \pth{{python3 livro-core/gen_inventario.py}};
o arquivo \pth{{livro-core/inventario-core.json}} conserva os hashes SHA-256 das
fontes lidas. Contam-se registros e chamadas no código-fonte, não inferências,
fontes independentes nem resultados científicos confirmados. A quantidade de
citações não avalia sua pertinência: a fonte precisa sustentar a afirmação.
\end{{resultado}}"""
    _replace_block(root / "livro-core/mod-11-apendices.tex", block)
    condensed_path = root / "livro-core/mod-14-lote-categorias.tex"
    if condensed_path.exists():
        condensed_block = rf"""\begin{{resultado}}
\textbf{{Inventário de granularidades.}} Nesta edição, \pth{{opencode.json}}
declara {counts['agents']} agentes, enquanto este capítulo contém
{counts['condensed_cards']} fichas de categoria. A fonte dessas duas contagens
é \pth{{gen_inventario.py}}. Uma categoria pode reunir vários agentes:
o quociente entre esses totais não mede cobertura de agentes. Para medir
cobertura, compare identificadores de conjuntos da mesma natureza.
\end{{resultado}}"""
        _replace_block(condensed_path, condensed_block, r"\section[Leitura guiada]")
    report = collect_inventory(root)
    (root / "livro-core/inventario-core.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False))
    return report


if __name__ == "__main__":
    main()
