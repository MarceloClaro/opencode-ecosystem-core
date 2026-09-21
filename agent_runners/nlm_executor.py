"""Executor de podcast Gemini Notebook (nlm) — SPEC-972, Fase 1 (operador).

Integração estritamente por invocação externa da CLI `nlm`
(pacote PyPI `notebooklm-mcp-cli`, MIT, `jacob-bd/gemini-notebook-mcp-cli`).

Veredito R474/R548: ADOTAR-opt-in — o upstream usa APIs internas não
documentadas do Gemini Notebook e autenticação por cookies de browser;
portanto esta é uma ferramenta EXPLÍCITA do operador, nunca uma etapa
automática do pipeline de pesquisa (ver SPEC-971/SPEC-972).

Invariantes (espelham o padrão canônico de agent_runners/tig_executor.py):
- `shell=False` obrigatório; argumentos sempre em lista.
- Allowlist de notebooks quando configurada; tarefa vazia, operação
  desconhecida, notebook fora da allowlist ou binário ausente => negação
  sem qualquer chamada ao binário (fail-closed).
- Ausência do binário (`shutil.which` / `NLM_BIN`) => indisponível; nunca
  instala nada automaticamente.
- Anti-overclaim: o recibo reporta apenas exit_code/success/motivo/IDs;
  não declara mérito, verificação ou qualidade do conteúdo gerado.
- Nenhum segredo (cookie/token) é lido ou persistido por este módulo; a
  sessão vive em ~/.notebooklm-mcp-cli fora do repositório.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

# Operações reconhecidas por este executor (Fase 1).
ALLOWED_OPERATIONS: Set[str] = {
    "create_notebook",
    "add_source_text",
    "create_audio",
    "download_audio",
}

# Formatos/lengths aceitos pelo `nlm audio create` (help real v0.11.6).
ALLOWED_AUDIO_FORMATS: Set[str] = {"deep_dive", "brief", "critique", "debate"}
ALLOWED_LENGTHS: Set[str] = {"short", "default", "long"}

DEFAULT_PROFILE = "default"
ORCHESTRATOR = "marceloclaro"

# Chaves candidatas a ID no JSON de saída do nlm (busca recursiva rasa).
_ID_KEYS: tuple = ("notebook_id", "artifact_id", "id", "uuid")

Runner = Callable[..., Any]

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


@dataclass
class NlmPodcastReceipt:
    """Recibo auditável de uma operação do executor nlm."""

    orchestrator: str = ORCHESTRATOR
    invoked_at_utc: str = ""
    operation: str = ""
    target: str = ""
    task_sha256: str = ""
    bin_path: Optional[str] = None
    exit_code: Optional[int] = None
    success: bool = False
    reason: str = ""
    result_id: Optional[str] = None
    artifact_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NlmPodcastExecutor:
    """Despacha operações primitivas do pipeline de podcast ao binário `nlm`.

    O runner é injetável para testes herméticos; em produção usa
    `subprocess.run` com `shell=False`.
    """

    def __init__(
        self,
        bin_path: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        notebook_allowlist: Optional[Set[str]] = None,
        profile: str = DEFAULT_PROFILE,
        runner: Optional[Runner] = None,
    ) -> None:
        self.env = env if env is not None else os.environ
        self.profile = profile
        # allowlist vazia/None => operação liberada para qualquer notebook
        # (documentado); configurar no chamador quando restrição for exigida.
        self.notebook_allowlist: Set[str] = (
            set(notebook_allowlist) if notebook_allowlist is not None else set()
        )
        self._runner: Runner = runner or self._default_runner
        self.bin_path = self._resolve_bin(bin_path)

    @staticmethod
    def _default_runner(cmd: Sequence[str], **kwargs: Any) -> Any:
        return subprocess.run(cmd, **kwargs)

    def _resolve_bin(self, bin_path: Optional[str]) -> Optional[str]:
        if bin_path:
            return bin_path
        if os.environ.get("NLM_BIN"):
            return os.environ["NLM_BIN"]
        return shutil.which("nlm")

    def available(self) -> bool:
        return bool(self.bin_path)

    def status(self) -> Dict[str, Any]:
        return {
            "name": "nlm",
            "available": self.available(),
            "bin_path": self.bin_path,
            "profile": self.profile,
            "operations": sorted(ALLOWED_OPERATIONS),
            "formats": sorted(ALLOWED_AUDIO_FORMATS),
            "lengths": sorted(ALLOWED_LENGTHS),
            "note": (
                "integracao por invocacao externa (opt-in do operador); "
                "upstream usa APIs internas nao documentadas do Gemini Notebook"
            ),
        }

    # ── fail-closed central ────────────────────────────────────────────

    def _precheck(
        self, operation: str, task: str, target: str
    ) -> Optional[str]:
        if operation not in ALLOWED_OPERATIONS:
            return f"operacao desconhecida: {operation}"
        if not task.strip():
            return "task vazia; despacho negado"
        if not self.bin_path:
            return "binario nlm indisponivel; nenhuma execucao"
        if operation in ("add_source_text", "create_audio", "download_audio"):
            if not target.strip():
                return "notebook_id vazio; despacho negado"
            if self.notebook_allowlist and target not in self.notebook_allowlist:
                return "notebook_id fora da allowlist; fail-closed"
        return None

    def _invoke(self, cmd: Sequence[str], timeout: int) -> tuple:
        """Executa via runner injetável com tratamento de falhas controlado."""
        try:
            proc = self._runner(
                list(cmd),
                shell=False,
                capture_output=True,
                timeout=timeout,
                env=self.env,
            )
            rc = int(getattr(proc, "returncode", -1))
            stdout = getattr(proc, "stdout", b"") or b""
            stderr = getattr(proc, "stderr", b"") or b""
            return rc, stdout, stderr
        except subprocess.TimeoutExpired:
            return -1, b"", f"timeout ({timeout}s)".encode("utf-8")
        except Exception as exc:  # runner injetado pode falhar de forma estranha
            return -1, b"", f"excecao controlada: {type(exc).__name__}".encode("utf-8")

    def run_operation(
        self,
        operation: str,
        task: str,
        target: str = "",
        timeout: int = 300,
    ) -> NlmPodcastReceipt:
        receipt = NlmPodcastReceipt(
            invoked_at_utc=_utc_now(),
            operation=operation,
            target=target,
            task_sha256=_sha256(task),
            bin_path=self.bin_path,
        )
        error = self._precheck(operation, task, target)
        if error:
            receipt.reason = error
            return receipt

        cmd = self._build_cmd(operation, task, target)
        rc, stdout, stderr = self._invoke(cmd, timeout)

        # download_audio: a geração do artefato no servidor do Gemini Notebook
        # demora (~5-10 min); o download 404 até o artefato ficar completed,
        # então repetimos com espera entre tentativas (retries/wait no task).
        if operation == "download_audio":
            retries, wait = _download_retry_params(task)
            attempts = 0
            while attempts < max(1, retries):
                attempts += 1
                if rc == 0:
                    break
                if attempts >= max(1, retries):
                    break
                time.sleep(max(0.0, wait))
                rc, stdout, stderr = self._invoke(cmd, timeout)

        receipt.exit_code = rc
        if rc != 0:
            err = stderr.decode("utf-8", errors="replace").strip()
            receipt.reason = f"exit={rc}: {err[:300]}" if err else f"exit={rc}"
            return receipt

        out_text = stdout.decode("utf-8", errors="replace") or ""
        parsed_id = _extract_id(out_text)
        if operation in ("create_notebook", "create_audio"):
            if not parsed_id:
                receipt.reason = "sucesso sem id parseavel no stdout"
                return receipt
            receipt.result_id = parsed_id
        elif operation == "download_audio":
            receipt.result_id = target + ":" + (parsed_id or "")
        receipt.exit_code = 0
        receipt.success = True
        receipt.reason = f"operacao {operation} concluida"
        return receipt

    def _build_cmd(
        self, operation: str, task: str, target: str
    ) -> List[str]:
        cmd: List[str] = [self.bin_path or "nlm"]
        if operation == "create_notebook":
            cmd += ["notebook", "create", task, "--json", "--profile", self.profile]
        elif operation == "add_source_text":
            cmd += [
                "source", "add", target, "--text", task,
                "--profile", self.profile,
            ]
        elif operation == "create_audio":
            fmt, length, language = _split_format_length_language(task)
            cmd += [
                "audio", "create", target,
                "--format", fmt, "--length", length, "--language", language,
                "--confirm", "--json", "--profile", self.profile,
            ]
        elif operation == "download_audio":
            out_path, artifact_id, _retries, _wait = _split_download_args(task)
            cmd += [
                "download", "audio", target,
                "--id", artifact_id, "-o", out_path,
            ]
        else:  # pragma: no cover — _precheck já negou
            raise ValueError(operation)
        return cmd

    # ── API primitiva de alto nível ────────────────────────────────────

    def create_notebook(self, title: str, timeout: int = 120) -> NlmPodcastReceipt:
        return self.run_operation("create_notebook", title, timeout=timeout)

    def add_source_text(
        self, notebook_id: str, text: str, timeout: int = 120
    ) -> NlmPodcastReceipt:
        return self.run_operation(
            "add_source_text", text, target=notebook_id, timeout=timeout
        )

    def create_audio(
        self,
        notebook_id: str,
        fmt: str = "deep_dive",
        length: str = "long",
        language: str = "pt-BR",
        timeout: int = 900,
    ) -> NlmPodcastReceipt:
        if fmt not in ALLOWED_AUDIO_FORMATS:
            return NlmPodcastReceipt(
                operation="create_audio", target=notebook_id,
                reason=f"formato invalido: {fmt}", bin_path=self.bin_path,
            )
        if length not in ALLOWED_LENGTHS:
            return NlmPodcastReceipt(
                operation="create_audio", target=notebook_id,
                reason=f"length invalido: {length}", bin_path=self.bin_path,
            )
        task = _join_format_length_language(fmt, length, language)
        return self.run_operation(
            "create_audio", task, target=notebook_id, timeout=timeout
        )

    def download_audio(
        self,
        notebook_id: str,
        artifact_id: str,
        output_dir: str,
        filename: Optional[str] = None,
        retries: int = 8,
        wait: float = 20.0,
        timeout: int = 120,
    ) -> NlmPodcastReceipt:
        """Baixa o áudio para ``output_dir`` (ou filename exato se dado).

        A sintaxe real do `nlm download audio` (v0.11.6) é `-o <arquivo>` e
        NÃO aceita `--profile`. Como a geração do artefato demora no servidor,
        o download tenta até ``retries`` vezes com ``wait`` segundos entre
        tentativas (o artefato ainda processando responde 404).
        """
        output_path = os.path.join(
            output_dir, filename or f"podcast_{notebook_id[:8]}.m4a"
        )
        task = _join_download_args(output_path, artifact_id, retries, wait)
        return self.run_operation(
            "download_audio", task, target=notebook_id, timeout=timeout
        )


# ── helpers internos ──────────────────────────────────────────────────

def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _join_format_length_language(fmt: str, length: str, language: str) -> str:
    return f"{fmt}\x00{length}\x00{language}"


def _split_format_length_language(task: str) -> tuple:
    parts = task.split("\x00")
    fmt = parts[0] if len(parts) > 0 and parts[0] else "deep_dive"
    length = parts[1] if len(parts) > 1 and parts[1] else "long"
    language = parts[2] if len(parts) > 2 and parts[2] else "pt-BR"
    return fmt, length, language


def _join_download_args(
    output_path: str, artifact_id: str, retries: int = 8, wait: float = 20.0
) -> str:
    return "\x00".join([output_path, artifact_id, str(retries), str(wait)])


def _split_download_args(task: str) -> tuple:
    parts = task.split("\x00")
    out_path = parts[0] if parts else ""
    artifact_id = parts[1] if len(parts) > 1 else ""
    retries = parts[2] if len(parts) > 2 else "8"
    wait = parts[3] if len(parts) > 3 else "20"
    return out_path, artifact_id, retries, wait


def _download_retry_params(task: str) -> tuple:
    _out, _art, retries, wait = _split_download_args(task)
    try:
        r = int(retries)
    except (TypeError, ValueError):
        r = 8
    try:
        w = float(wait)
    except (TypeError, ValueError):
        w = 20.0
    return r, w


def _extract_id(output: str) -> Optional[str]:
    """Extrai um ID (notebook/artifact) do stdout JSON do nlm.

    Estratégia: (1) JSON keys conhecidas em busca rasa/recursiva; (2) fallback
    regex de UUID único. Nunca inventa ID.
    """
    if not output:
        return None
    try:
        data = json.loads(output)
    except (ValueError, TypeError):
        data = None
    if isinstance(data, dict):
        found = _dig_dict(data, _ID_KEYS)
        if found:
            return found
    uuids = list(_UUID_RE.findall(output))
    if len(uuids) == 1:
        return uuids[0]
    return None


def _dig_dict(node: Any, keys: tuple, depth: int = 0) -> Optional[str]:
    if depth > 4 or not isinstance(node, dict):
        return None
    for k in keys:
        v = node.get(k)
        if isinstance(v, str) and v:
            return v
    for v in node.values():
        found = _dig_dict(v, keys, depth + 1)
        if found:
            return found
    return None