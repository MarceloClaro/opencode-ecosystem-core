"""R1085: dossiê verificável e objetos de build fora do intervalo a publicar."""
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1085/parecer-repositorios.md"
BASE = "0e501aedf56e9b085f7bf650002983ca7d522a0b"
RESIDUES = (
    "literatura/livros/ia-odontologia/template/main.xdv",
    "literatura/molambudos/Molambudos_VictoriaRegia/tri/main_kdp_print_160x230mm.synctex(busy)",
)


def test_parecer_distingue_projetos_licencas_e_aprovacao_auditiva():
    text = REPORT.read_text(encoding="utf-8")
    for term in (
        "digitalsamba/claude-code-video-toolkit",
        "travisvn/chatterbox-tts-api",
        "assafkip/claudemy",
        "AGPL-3.0", "MIT", "XTTS", "pt-BR", "consentimento",
        "revisão auditiva humana", "não instalado", "não executado",
    ):
        assert term in text, term


def test_residuos_nao_entram_no_historico_a_publicar():
    for path in RESIDUES:
        result = subprocess.run(
            ["git", "log", "--format=%H", f"{BASE}..HEAD", "--", path],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        assert not result.stdout.strip(), (path, result.stdout)
        entry = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", path],
            cwd=ROOT, check=False, capture_output=True,
        )
        assert entry.returncode != 0, path
