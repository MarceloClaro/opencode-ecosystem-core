# -*- coding: utf-8 -*-
"""
CLI LiteRT-LM — Interface de Linha de Comando para Modelos On-Device
====================================================================
Comandos: list, run, chat, import, serve, info, delete

Uso:
    litert-lm list
    litert-lm run gemma-4-E2B-it --prompt "Olá!"
    litert-lm chat gemma-4-E2B-it
    litert-lm import litert-community/gemma-4-E2B-it-litert-lm
    litert-lm serve gemma-4-E2B-it --port 9379
    litert-lm info gemma-4-E2B-it
    litert-lm delete gemma-4-E2B-it
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Optional

import click

from .model_manager import ModelNotFoundError
from .skill import LiteRTLMSkill


# ── Helpers ───────────────────────────────────────────────────────────────────


def _create_skill(verbose: bool = False) -> LiteRTLMSkill:
    """Cria instância da skill com configuração padrão."""
    return LiteRTLMSkill(verbose=verbose)


def _format_size(size_bytes: int) -> str:
    """Formata tamanho em bytes para string legível."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


_WINDOWS_DRIVE_RE = re.compile(r'^([A-Za-z]):[/\\]', re.ASCII)
_WSL_PATH_RE = re.compile(r'^/mnt/([a-z])/', re.ASCII)
_FILE_URI_RE = re.compile(r'^file:///([a-zA-Z]):/', re.ASCII)
_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.tif'}


def _strip_quotes(text: str) -> str:
    """Remove aspas simples, duplas e espaços ao redor do texto."""
    text = text.strip().strip('"').strip("'").strip()
    return text


def _resolve_image_path(raw_path: str) -> Optional[str]:
    """Tenta converter qualquer formato de caminho para WSL absoluto.

    Formatos aceitos:
      - Windows:  C:\\Users\\...\\image.png
      - Windows:  C:/Users/.../image.png
      - WSL:      /mnt/c/Users/.../image.png
      - URI:      file:///C:/Users/.../image.png
      - Quoted:   "C:\\Users\\...\\image.png"

    Args:
        raw_path: Caminho bruto (pode conter aspas, file://, etc.).

    Returns:
        Caminho absoluto WSL se o arquivo existir, None caso contrário.
    """
    path = _strip_quotes(raw_path)

    # ── Formato file:///C:/... ──
    m = _FILE_URI_RE.match(path)
    if m:
        drive = m.group(1).lower()
        rest = path[m.end():].replace('\\', '/')
        wsl_path = f'/mnt/{drive}/{rest.lstrip("/")}'
        if os.path.isfile(wsl_path):
            return wsl_path

    # ── Formato Windows nativo: C:\... ou C:/... ──
    m = _WINDOWS_DRIVE_RE.match(path)
    if m:
        drive = m.group(1).lower()
        rest = path[m.end():].replace('\\', '/')
        wsl_path = f'/mnt/{drive}/{rest.lstrip("/")}'
        if os.path.isfile(wsl_path):
            return wsl_path

    # ── Formato WSL nativo: /mnt/c/... ──
    m = _WSL_PATH_RE.match(path)
    if m:
        if os.path.isfile(path):
            return os.path.abspath(path)

    # ── Caminho absoluto Unix (já convertido) ──
    if path.startswith('/') and os.path.isfile(path):
        return os.path.abspath(path)

    return None


def _detect_images(text: str) -> tuple:
    """Detecta se a entrada contém caminhos de imagem arrastados/solados.

    Esta função é chamada a cada input do usuário, tanto no modo
    prompt_toolkit quanto no fallback click. Ela converte automaticamente
    caminhos Windows (C:\\...) para WSL (/mnt/c/...) e extrai imagens
    do texto digitado.

    Returns:
        Tupla (prompt, attachments):
            - prompt: texto limpo (sem os caminhos de imagem).
            - attachments: lista de caminhos WSL absolutos das imagens.
            Se não houver imagens: (text_original, None).
    """
    stripped = _strip_quotes(text)

    # ── Caso 1: entrada é SOMENTE um caminho de imagem ──
    resolved = _resolve_image_path(stripped)
    if resolved:
        ext = os.path.splitext(stripped)[1].lower()
        if ext in _IMAGE_EXTENSIONS:
            click.echo(click.style(
                f"📷 Imagem detectada: {stripped} → {resolved}", fg="cyan"
            ), err=True)
            return ("Descreva esta imagem.", [resolved])

    # ── Caso 2: texto com possíveis caminhos embutidos ──
    # Quebra mantendo quotes agrupadas (para paths com espaços)
    parts = []
    for token in stripped.split():
        # Se o token começa com " mas não termina, junta com o próximo
        if token.startswith('"') and not token.endswith('"'):
            parts.append(token)
        elif parts and parts[-1].startswith('"') and not parts[-1].endswith('"'):
            parts[-1] += ' ' + token
        else:
            parts.append(token)

    image_paths = []
    text_parts = []
    for part in parts:
        resolved = _resolve_image_path(part)
        if resolved and os.path.splitext(_strip_quotes(part))[1].lower() in _IMAGE_EXTENSIONS:
            image_paths.append(resolved)
            click.echo(click.style(
                f"📷 Imagem detectada: {part}", fg="cyan"
            ), err=True)
        else:
            text_parts.append(part)

    if image_paths:
        return (" ".join(text_parts), image_paths)

    # ── Caso 3: sem imagens ──
    return (text, None)


def _consume_stream(response, echo=True):
    """Consome um generator de streaming e retorna o texto completo.

    Args:
        response: Generator de chunks ou string simples.
        echo: Se True, imprime cada chunk ao vivo.

    Returns:
        Texto completo acumulado.
    """
    if not hasattr(response, "__next__"):
        return str(response)

    accumulated = ""
    for chunk in response:
        if isinstance(chunk, dict):
            text = chunk.get("content", [{}])[0].get("text", "")
        elif hasattr(chunk, "texts") and chunk.texts:
            text = chunk.texts[0]
        else:
            text = str(chunk)
        accumulated += text
        if echo:
            click.echo(click.style(text, fg="yellow"), nl=False)
    if echo:
        click.echo()
    return accumulated


# ── Grupo Principal ───────────────────────────────────────────────────────────


@click.group(
    name="litert-lm",
    help="CLI para modelos LiteRT-LM (Google AI Edge on-device LLM).",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("--verbose", is_flag=True, help="Logs detalhados.")
@click.pass_context
def litert_lm_cli(ctx: click.Context, verbose: bool):
    """CLI para gerenciar e executar modelos LiteRT-LM."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# ── Comando: list ─────────────────────────────────────────────────────────────


@litert_lm_cli.command("list")
@click.option("--json", "json_output", is_flag=True, help="Saída em formato JSON.")
@click.pass_context
def list_models(ctx: click.Context, json_output: bool):
    """Lista modelos disponíveis localmente."""
    skill = _create_skill(verbose=ctx.obj["verbose"])
    models = skill.list_models()

    if json_output:
        click.echo(json.dumps(
            [{"model_id": m.model_id, "path": m.model_path,
              "size_bytes": m.file_size_bytes} for m in models],
            indent=2, ensure_ascii=False,
        ))
        return

    if not models:
        click.echo("Nenhum modelo encontrado.")
        click.echo("Use 'litert-lm import <repo>' para baixar do HuggingFace.")
        return

    click.echo(click.style("Modelos disponíveis:", bold=True))
    click.echo()
    for m in models:
        size_str = _format_size(m.file_size_bytes)
        click.echo(f"  {click.style(m.model_id, bold=True)}")
        click.echo(f"    Caminho: {m.model_path}")
        click.echo(f"    Tamanho: {size_str}")
        click.echo()


# ── Comando: run ──────────────────────────────────────────────────────────────


@litert_lm_cli.command("run")
@click.argument("model_reference")
@click.option("--prompt", "-p", required=True, help="Prompt a ser executado.")
@click.option("--image", "-i", multiple=True, default=[],
              help="Caminho(s) para imagem(s) (múltiplas permitidas).")
@click.option("--backend", default="cpu", show_default=True,
              type=click.Choice(["cpu", "gpu", "npu"]), help="Backend de inferência.")
@click.option("--temperature", type=float, default=None, help="Temperatura.")
@click.option("--top-k", type=int, default=None, help="Top-K sampling.")
@click.option("--top-p", type=float, default=None, help="Top-P sampling.")
@click.option("--seed", type=int, default=None, help="Seed aleatória.")
@click.option("--max-tokens", type=int, default=None, help="Máx. tokens de saída.")
@click.option("--no-template", is_flag=True, help="Ignorar template de prompt.")
@click.pass_context
def run_model(
    ctx: click.Context,
    model_reference: str,
    prompt: str,
    image: tuple,
    backend: str,
    temperature: Optional[float],
    top_k: Optional[int],
    top_p: Optional[float],
    seed: Optional[int],
    max_tokens: Optional[int],
    no_template: bool,
):
    """Executa um prompt único em MODEL_REFERENCE e exibe a resposta."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    try:
        response = skill.run(
            model_reference,
            prompt=prompt,
            images=list(image) if image else None,
            backend=backend,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            seed=seed,
            max_tokens=max_tokens,
            no_template=no_template,
        )
        click.echo(click.style(response, fg="yellow"))
    except ModelNotFoundError as e:
        click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Erro durante inferência: {e}", fg="red"), err=True)
        if ctx.obj["verbose"]:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# ── Comando: chat ─────────────────────────────────────────────────────────────


@litert_lm_cli.command("chat")
@click.argument("model_reference")
@click.option("--prompt", "-p", default=None, help="Prompt inicial (modo não-interativo).")
@click.option("--image", "-i", multiple=True, default=[],
              help="Caminho(s) para imagem(s) (múltiplas permitidas).")
@click.option("--non-interactive", is_flag=True, hidden=True,
              help="Modo não-interativo para testes.")
@click.option("--backend", default="cpu", show_default=True,
              type=click.Choice(["cpu", "gpu", "npu"]), help="Backend de inferência.")
@click.option("--temperature", type=float, default=None, help="Temperatura.")
@click.option("--top-k", type=int, default=None, help="Top-K sampling.")
@click.option("--top-p", type=float, default=None, help="Top-P sampling.")
@click.option("--seed", type=int, default=None, help="Seed aleatória.")
@click.option("--max-tokens", type=int, default=None, help="Máx. tokens de saída.")
@click.option("--system", "system_instruction", default=None,
              help="Instrução de sistema para o chat.")
@click.option("--no-template", is_flag=True, help="Ignorar template de prompt.")
@click.option("--vision-backend", default=None,
              type=click.Choice(["cpu", "gpu"]),
              help="Backend para encoder de visão (default: igual ao --backend).")
@click.pass_context
def chat_model(
    ctx: click.Context,
    model_reference: str,
    prompt: Optional[str],
    image: tuple,
    non_interactive: bool,
    backend: str,
    temperature: Optional[float],
    top_k: Optional[int],
    top_p: Optional[float],
    seed: Optional[int],
    max_tokens: Optional[int],
    system_instruction: Optional[str],
    no_template: bool,
    vision_backend: Optional[str],
):
    """Inicia chat interativo com MODEL_REFERENCE."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    images = list(image) if image else None

    # Em modo interativo, sempre pré-carrega o VisionExecutor
    # (max_num_images >= 1) para aceitar imagens a qualquer momento
    if not non_interactive and prompt is None:
        # Chat interativo: prepara visão desde o início
        max_num_images = max(len(images) if images else 0, 3)
    else:
        # Modo não-interativo: só ativa visão se houver --image
        max_num_images = len(images) if images else 0

    try:
        session = skill.chat(
            model_reference,
            backend=backend,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            seed=seed,
            max_tokens=max_tokens,
            system_instruction=system_instruction,
            no_template=no_template,
            stream=not non_interactive,
            max_num_images=max_num_images,
            vision_backend=vision_backend,
        )
    except ModelNotFoundError as e:
        click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Erro ao iniciar chat: {e}", fg="red"), err=True)
        sys.exit(1)

    # Modo não-interativo (para testes)
    if prompt or non_interactive:
        try:
            if prompt:
                # Detecta se o --prompt é na verdade um caminho Windows
                clean_prompt, win_images = _detect_images(prompt)
                if win_images:
                    all_images = (images or []) + win_images
                    final_prompt = clean_prompt or "Descreva esta imagem."
                else:
                    all_images = images
                    final_prompt = prompt
                response = session.send(final_prompt, attachments=all_images)
                _consume_stream(response, echo=True)
        except Exception as e:
            click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        finally:
            session.close()
        return

    # Modo interativo
    click.echo(
        click.style(
            "[enter] enviar | [ctrl+j] nova linha | [ctrl+c] limpar/sair",
            fg="cyan",
        )
    )
    click.echo()

    try:
        import prompt_toolkit
        from prompt_toolkit import key_binding
        from prompt_toolkit.history import FileHistory

        # Cria key bindings
        kb = key_binding.KeyBindings()

        @kb.add("enter")
        def _handle_enter(event):
            buffer = event.current_buffer
            if buffer.text.strip():
                buffer.validate_and_handle()

        @kb.add("c-j")
        @kb.add("escape", "enter")
        def _handle_newline(event):
            event.current_buffer.insert_text("\n")

        @kb.add("c-c")
        def _handle_clear_or_exit(event):
            buffer = event.current_buffer
            if buffer.text:
                buffer.text = ""
            else:
                event.app.exit(exception=EOFError)

        # Cria sessão prompt_toolkit
        history_file = os.path.expanduser("~/.litert-lm/history")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        prompt_session = prompt_toolkit.PromptSession(
            history=FileHistory(history_file),
            key_bindings=kb,
        )

        # Flag para anexar imagens apenas na primeira mensagem
        _pending_images = list(images) if images else None

        while True:
            try:
                user_input = prompt_session.prompt(
                    prompt_toolkit.ANSI(
                        click.style("> ", fg="green", bold=True)
                    ),
                    multiline=True,
                )
                if not user_input:
                    continue

                # Detecta caminhos Windows
                clean_input, win_images = _detect_images(user_input)
                if win_images:
                    response = session.send(
                        clean_input or "Descreva esta imagem.",
                        attachments=win_images,
                    )
                    _pending_images = None
                elif _pending_images:
                    response = session.send(
                        user_input, attachments=_pending_images
                    )
                    _pending_images = None
                else:
                    response = session.send(user_input)
                _consume_stream(response, echo=True)
                click.echo()

            except EOFError:
                break
            except KeyboardInterrupt:
                click.echo()
                continue
            except Exception as e:
                click.echo(
                    click.style(f"Erro durante geração: {e}", fg="red"), err=True
                )

    except ImportError:
        click.echo(
            click.style(
                "Aviso: prompt_toolkit não instalado. "
                "Usando modo simples (sem edição multiline).",
                fg="yellow",
            ),
            err=True,
        )
        # Fallback para input() simples
        _pending_images = list(images) if images else None
        try:
            while True:
                user_input = click.prompt(
                    click.style("> ", fg="green", bold=True),
                    default="",
                    show_default=False,
                )
                if not user_input:
                    continue
                # Detecta caminhos Windows
                clean_input, win_images = _detect_images(user_input)
                if win_images:
                    response = session.send(
                        clean_input or "Descreva esta imagem.",
                        attachments=win_images,
                    )
                elif _pending_images:
                    response = session.send(
                        user_input, attachments=_pending_images
                    )
                    _pending_images = None
                else:
                    response = session.send(user_input)
                _consume_stream(response, echo=True)
                click.echo()
        except (EOFError, KeyboardInterrupt):
            pass

    finally:
        session.close()


# ── Comando: import ───────────────────────────────────────────────────────────


@litert_lm_cli.command("import")
@click.argument("huggingface_repo")
@click.option("--filename", default=None,
              help="Nome do arquivo no repositório (opcional — auto-descoberta).")
@click.option("--token", default=None, help="Token HuggingFace (para modelos gated).")
@click.pass_context
def import_model(
    ctx: click.Context,
    huggingface_repo: str,
    filename: Optional[str],
    token: Optional[str],
):
    """Importa modelo do HuggingFace (repositórios litert-community)."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    if filename:
        click.echo(f"Baixando {huggingface_repo}/{filename}...")
    else:
        click.echo(f"Descobrindo arquivo em {huggingface_repo}...")

    try:
        info = skill.import_model(
            repo_id=huggingface_repo,
            filename=filename,
            token=token,
        )
        click.echo(click.style("✓ Modelo importado com sucesso!", fg="green"))
        click.echo(f"  ID:     {info.model_id}")
        click.echo(f"  Path:   {info.model_path}")
        click.echo(f"  Tamanho: {_format_size(info.file_size_bytes)}")
    except ImportError as e:
        click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        click.echo("Instale com: pip install huggingface-hub")
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Erro ao importar: {e}", fg="red"), err=True)
        sys.exit(1)


# ── Comando: serve ────────────────────────────────────────────────────────────


@litert_lm_cli.command("serve")
@click.argument("model_reference")
@click.option("--host", default="0.0.0.0", show_default=True, help="Host.")
@click.option("--port", default=9379, show_default=True, type=int, help="Porta.")
@click.option("--backend", default="cpu", show_default=True,
              type=click.Choice(["cpu", "gpu", "npu"]), help="Backend.")
@click.option("--temperature", default=0.7, type=float, help="Temperatura padrão.")
@click.option("--max-tokens", default=4096, type=int, help="Máx. tokens.")
@click.option("--cors-origin", multiple=True, default=[],
              help="Origens CORS (múltiplas permitidas).")
@click.pass_context
def serve_model(
    ctx: click.Context,
    model_reference: str,
    host: str,
    port: int,
    backend: str,
    temperature: float,
    max_tokens: int,
    cors_origin: tuple,
):
    """Inicia servidor OpenAI-compatible com MODEL_REFERENCE."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    cors_list = list(cors_origin) if cors_origin else ["*"]

    try:
        server = skill.serve(
            model_reference,
            host=host,
            port=port,
            backend=backend,
            cors_origins=cors_list,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        click.echo(
            click.style(
                f"Servidor OpenAI-compatible rodando em http://{host}:{port}",
                fg="green",
                bold=True,
            )
        )
        click.echo(f"  Modelo: {server.model_name}")
        click.echo(f"  Endpoints: /v1/models, /v1/chat/completions")
        click.echo("  Pressione Ctrl+C para parar.")
        click.echo()

        # Se LITERT_LM_DRY_RUN=1, apenas exibe info sem iniciar (útil para testes)
        if os.environ.get("LITERT_LM_DRY_RUN") == "1":
            click.echo("[DRY RUN] Servidor configurado, não iniciado.", err=True)
            return

        # Inicia servidor HTTP
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json as json_module

        class LiteRTRequestHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.server_ref = server
                super().__init__(*args, **kwargs)

            def _send_json(self, data, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods",
                                 "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers",
                                 "Content-Type, Authorization")
                self.end_headers()
                self.wfile.write(json_module.dumps(data).encode("utf-8"))

            def do_OPTIONS(self):
                self._send_json({})

            def do_GET(self):
                if self.path == "/v1/models":
                    models = server.list_models()
                    self._send_json({
                        "object": "list",
                        "data": models,
                    })
                else:
                    self._send_json({"error": "not found"}, 404)

            def do_POST(self):
                if self.path == "/v1/chat/completions":
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    try:
                        request = json_module.loads(body)
                    except json_module.JSONDecodeError:
                        self._send_json({"error": "invalid JSON"}, 400)
                        return

                    messages = request.get("messages", [])
                    stream = request.get("stream", False)
                    temperature = request.get("temperature", 0.7)
                    max_tokens = request.get("max_tokens", 4096)

                    response = server.chat_completion(
                        messages,
                        stream=stream,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    self._send_json(response)
                else:
                    self._send_json({"error": "not found"}, 404)

            def log_message(self, format, *args):
                if ctx.obj["verbose"]:
                    super().log_message(format, *args)

        # Vincula referência do servidor ao handler
        handler = type("Handler", (LiteRTRequestHandler,), {"server_ref": server})

        httpd = HTTPServer((host, port), handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo(click.style("\nServidor encerrado.", fg="cyan"))
        finally:
            httpd.server_close()
            server.close()

    except ModelNotFoundError as e:
        click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Erro ao iniciar servidor: {e}", fg="red"), err=True)
        sys.exit(1)


# ── Comando: info ──────────────────────────────────────────────────────────────


@litert_lm_cli.command("info")
@click.argument("model_reference")
@click.pass_context
def model_info(ctx: click.Context, model_reference: str):
    """Exibe informações detalhadas de MODEL_REFERENCE."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    try:
        metadata = skill.inspect(model_reference)
    except ModelNotFoundError as e:
        click.echo(click.style(f"Erro: {e}", fg="red"), err=True)
        sys.exit(1)

    click.echo(click.style("Informações do Modelo:", bold=True))
    click.echo()
    for key, value in metadata.items():
        key_str = key.replace("_", " ").title()
        click.echo(f"  {key_str}: {value}")


# ── Comando: delete ────────────────────────────────────────────────────────────


@litert_lm_cli.command("delete")
@click.argument("model_reference")
@click.option("--force", "-f", is_flag=True, help="Forçar remoção sem confirmação.")
@click.pass_context
def delete_model(ctx: click.Context, model_reference: str, force: bool):
    """Remove MODEL_REFERENCE do cache local."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    if not force:
        click.confirm(
            f"Tem certeza que deseja remover '{model_reference}'?",
            abort=True,
        )

    try:
        result = skill.delete_model(model_reference)
        if result:
            click.echo(click.style(f"✓ Modelo '{model_reference}' removido.", fg="green"))
        else:
            click.echo(click.style(
                f"Modelo '{model_reference}' não encontrado.", fg="yellow"
            ))
    except Exception as e:
        click.echo(click.style(f"Erro ao remover: {e}", fg="red"), err=True)
        sys.exit(1)


# ── Entrypoint ────────────────────────────────────────────────────────────────


def main(argv: Optional[list] = None) -> None:
    """Entrypoint para console_scripts."""
    litert_lm_cli(argv)


if __name__ == "__main__":
    main()
