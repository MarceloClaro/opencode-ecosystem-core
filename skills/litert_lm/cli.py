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
@click.pass_context
def chat_model(
    ctx: click.Context,
    model_reference: str,
    prompt: Optional[str],
    non_interactive: bool,
    backend: str,
    temperature: Optional[float],
    top_k: Optional[int],
    top_p: Optional[float],
    seed: Optional[int],
    max_tokens: Optional[int],
    system_instruction: Optional[str],
    no_template: bool,
):
    """Inicia chat interativo com MODEL_REFERENCE."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

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
                response = session.send(prompt)
                click.echo(click.style(response, fg="yellow"))
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

                response = session.send(user_input)
                click.echo(click.style(response, fg="yellow"))
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
        try:
            while True:
                user_input = click.prompt(
                    click.style("> ", fg="green", bold=True),
                    default="",
                    show_default=False,
                )
                if not user_input:
                    continue
                response = session.send(user_input)
                click.echo(click.style(response, fg="yellow"))
                click.echo()
        except (EOFError, KeyboardInterrupt):
            pass

    finally:
        session.close()


# ── Comando: import ───────────────────────────────────────────────────────────


@litert_lm_cli.command("import")
@click.argument("huggingface_repo")
@click.option("--filename", default="model.litertlm", show_default=True,
              help="Nome do arquivo no repositório.")
@click.option("--token", default=None, help="Token HuggingFace (para modelos gated).")
@click.pass_context
def import_model(
    ctx: click.Context,
    huggingface_repo: str,
    filename: str,
    token: Optional[str],
):
    """Importa modelo do HuggingFace (repositórios litert-community)."""
    skill = _create_skill(verbose=ctx.obj["verbose"])

    click.echo(f"Baixando {huggingface_repo}/{filename}...")

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
