"""R824: ações delimitadas em um navegador Playwright MCP real e isolado."""
from __future__ import annotations

from datetime import timedelta
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from integrations.execution_control import ExecutionCancelled, is_cancelled


def _origin(url: str, *, origin_only: bool = False) -> str:
    if not isinstance(url, str) or not url.strip() or len(url) > 4096 or any(ord(c) < 32 for c in url):
        raise ValueError("URL HTTP(S) explícita inválida.")
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Somente URLs HTTP(S) são admitidas.")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("Credenciais embutidas na URL não são admitidas.")
        if origin_only and (parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
            raise ValueError("Uma origem não pode conter caminho, consulta ou fragmento.")
        host = parsed.hostname.encode("idna").decode("ascii").lower()
        if any(c.isspace() for c in host) or "%" in host:
            raise ValueError("Host inválido.")
        host = f"[{host}]" if ":" in host else host
        port = parsed.port
        if port is not None and port < 1:
            raise ValueError("Porta explícita deve ser positiva.")
        default = 443 if parsed.scheme.lower() == "https" else 80
        return f"{parsed.scheme.lower()}://{host}" + (f":{port}" if port and port != default else "")
    except (UnicodeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc


class BrowserBridge:
    VERSION = "0.0.83"
    REPOSITORY = "https://github.com/microsoft/playwright-mcp"
    MAX_RESPONSE_BYTES = 8 * 1024 * 1024
    ROLES = frozenset({"button", "textbox", "link", "checkbox", "radio", "combobox", "tab", "menuitem"})

    def __init__(self, repo_root: str | Path | None = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()

    @staticmethod
    def _home() -> Path:
        return Path(os.environ.get("CORE_BROWSER_HOME") or Path.home() / ".local/share/opencode-core/playwright-mcp").expanduser().resolve()

    def status(self) -> dict[str, Any]:
        home = self._home()
        override = os.environ.get("CORE_BROWSER_NODE_BIN")
        node = Path(override).expanduser() if override is not None else Path(shutil.which("node") or "/absent-node")
        node_ok = node.is_file() and os.access(node, os.X_OK)
        package = home / "node_modules/@playwright/mcp/package.json"
        try:
            metadata = json.loads(package.read_text())
        except (OSError, ValueError):
            metadata = {}
        launcher = package.parent / "cli.js"
        browsers = sorted(home.glob("browsers/chromium-*/chrome-linux*/chrome"))
        executable = next((path for path in browsers if path.is_file() and os.access(path, os.X_OK)), None)
        missing = []
        if metadata.get("name") != "@playwright/mcp" or metadata.get("version") != self.VERSION:
            missing.append("pacote oficial @playwright/mcp@" + self.VERSION)
        if not launcher.is_file():
            missing.append("launcher MCP")
        if not node_ok:
            missing.append("Node executável")
        if executable is None:
            missing.append("Chromium instalado no runtime")
        if importlib.util.find_spec("mcp") is None:
            missing.append("SDK MCP Python")
        return {"operation": "status", "status": "completed" if not missing else "unavailable",
                "success": not missing, "available": not missing, "verification": "installation_only",
                "browser_executed": False, "externally_validated": False,
                "runtime": {"home": str(home), "node": str(node.resolve()) if node_ok else None,
                            "launcher": str(launcher), "browser": str(executable) if executable else None},
                "provenance": {"repository": self.REPOSITORY, "version": metadata.get("version")},
                "error": ", ".join(missing) or None}

    def _validate(self, config: Any) -> dict[str, Any]:
        if not isinstance(config, dict) or set(config) - {"operation", "url", "steps", "allowed_origins", "timeout_seconds", "screenshot"}:
            raise ValueError("Configuração de navegador deve conter somente campos admitidos.")
        operation = config.get("operation")
        if not isinstance(operation, str) or operation not in {"status", "run"}:
            raise ValueError("Use operation=status ou run.")
        if operation == "status":
            if set(config) != {"operation"}:
                raise ValueError("Status não aceita argumentos de execução.")
            return {"operation": "status"}
        url = config.get("url")
        origin = _origin(url)
        raw_origins = config.get("allowed_origins", [origin])
        if not isinstance(raw_origins, list) or not 1 <= len(raw_origins) <= 8:
            raise ValueError("Informe de 1 a 8 origens explícitas.")
        origins = sorted(set(_origin(value, origin_only=True) for value in raw_origins))
        if origin not in origins:
            raise ValueError("A URL inicial precisa pertencer às origens autorizadas.")
        timeout = config.get("timeout_seconds", 60)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 120:
            raise ValueError("Prazo deve ser finito, positivo e até 120 segundos.")
        screenshot = config.get("screenshot", False)
        if not isinstance(screenshot, bool):
            raise ValueError("screenshot deve ser booleano.")
        steps = config.get("steps", [])
        if not isinstance(steps, list) or len(steps) > 16:
            raise ValueError("Admite-se no máximo 16 passos.")
        validated = []
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError("Cada passo deve ser objeto.")
            action = step.get("action")
            if not isinstance(action, str):
                raise ValueError("A ação deve ser texto explícito.")
            fields = {"action"} if action in {"read", "snapshot"} else {"action", "role", "name"}
            if action == "fill":
                fields.add("value")
            if action not in {"read", "snapshot", "click", "fill"} or set(step) != fields:
                raise ValueError("Passo contém ação ou campos não admitidos.")
            if action in {"click", "fill"}:
                if not isinstance(step["role"], str) or step["role"] not in self.ROLES or (action == "fill" and step["role"] != "textbox"):
                    raise ValueError("Papel acessível incompatível com a ação.")
                if not isinstance(step["name"], str) or not 0 < len(step["name"]) <= 500 or "\x00" in step["name"]:
                    raise ValueError("Nome acessível explícito inválido.")
            if action == "fill" and (not isinstance(step["value"], str) or len(step["value"]) > 2000 or "\x00" in step["value"]):
                raise ValueError("Valor de preenchimento inválido.")
            validated.append(dict(step))
        request = {"operation": "run", "url": url.strip(), "allowed_origins": origins,
                   "steps": validated, "timeout_seconds": float(timeout), "screenshot": screenshot}
        # json.loads aceita escapes com surrogates isolados; o transporte e os
        # hashes exigem UTF-8 válido. Recusar antes de descobrir/iniciar o provider.
        try:
            json.dumps(request, ensure_ascii=False).encode("utf-8")
        except UnicodeError as exc:
            raise ValueError("A configuração deve conter texto UTF-8 válido.") from exc
        return request

    @staticmethod
    def _step_code(step: dict[str, Any]) -> str:
        encode = lambda value: json.dumps(value, ensure_ascii=False)
        if step["action"] in {"click", "fill"}:
            locator = f"page.getByRole({encode(step['role'])}, {{name: {encode(step['name'])}, exact: true}})"
            operation = locator + (f".fill({encode(step['value'])})" if step["action"] == "fill" else ".click()")
            return f"async (page) => {{ await {operation}; return {{stage: {encode(step['action'])}, url: page.url()}}; }}"
        return "async (page) => ({stage: 'read', url: page.url(), title: await page.title(), text: (await page.locator('body').innerText()).slice(0,16000)})"

    @staticmethod
    def _result(response: dict[str, Any]) -> dict[str, Any]:
        if response.get("isError"):
            raise ValueError("O provider retornou erro; consulte a evidência integral.")
        value = response.get("structuredContent")
        if isinstance(value, dict) and "stage" in value:
            return value
        for item in response.get("content", []):
            if item.get("type") != "text":
                continue
            text = item.get("text", "")
            if "### Result\n" in text:
                try:
                    value, _ = json.JSONDecoder().raw_decode(text.split("### Result\n", 1)[1].lstrip())
                    if isinstance(value, dict) and "stage" in value:
                        return value
                except ValueError:
                    pass
        raise ValueError("Resposta de ação sem resultado estruturado reconhecido.")

    async def _exchange(self, config, inventory, captured, errlog):
        from integrations.browser_proxy import BrowserOriginProxy
        async with BrowserOriginProxy(config["allowed_origins"], _origin) as proxy:
            try:
                await self._exchange_with_proxy(config, inventory, captured, errlog, proxy.url)
            finally:
                captured["network_guard"] = {"method": "session_http_connect_proxy",
                    "decisions_total": proxy.decisions_total, "decisions": proxy.decisions,
                    "limited_scope": "Tráfego HTTP/CONNECT que o navegador envia ao proxy; não certifica isolamento universal."}

    async def _exchange_with_proxy(self, config, inventory, captured, errlog, proxy_url):
        import anyio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        runtime = inventory["runtime"]
        directory = self.repo_root / ".opencode/browser/runs" / str(uuid4())
        if not directory.resolve().is_relative_to(self.repo_root):
            raise ValueError("Diretório de execução fora do workspace.")
        directory.mkdir(parents=True)
        environment = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(Path(runtime["home"]) / "browsers"))
        # Não herdar configurações implícitas de proxy, perfil, CDP ou extensão.
        for key in list(environment):
            if key.startswith("PLAYWRIGHT_MCP_"):
                environment.pop(key)
        parameters = StdioServerParameters(command=runtime["node"],
            args=[runtime["launcher"], "--headless", "--isolated", "--sandbox", "--block-service-workers",
                  "--executable-path", runtime["browser"], "--output-dir", str(directory),
                  "--proxy-server", proxy_url, "--proxy-bypass", "<-loopback>",
                  "--timeout-action", str(max(1000, int(config["timeout_seconds"] * 1000))),
                  "--timeout-navigation", str(max(1000, int(config["timeout_seconds"] * 1000)))],
            cwd=str(self.repo_root), env=environment)
        async with stdio_client(parameters, errlog=errlog) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=config["timeout_seconds"])) as session:
                async def call(name, arguments):
                    response = (await session.call_tool(name, arguments)).model_dump(mode="json", by_alias=True, exclude_none=True)
                    captured["responses"].append({"tool": name, "response": response})
                    if len(json.dumps(captured, ensure_ascii=False).encode()) > self.MAX_RESPONSE_BYTES:
                        raise ValueError("Evidência excede o limite de 8 MiB.")
                    if response.get("isError"):
                        raise ValueError("Provider retornou isError; consulte a evidência.")
                    return response
                async def watch(scope):
                    while True:
                        if is_cancelled():
                            scope.cancel()
                            return
                        await anyio.sleep(0.05)
                closed = False
                try:
                    with anyio.fail_after(config["timeout_seconds"]) as scope:
                        async with anyio.create_task_group() as group:
                            group.start_soon(watch, scope)
                            identity = await session.initialize()
                            captured["server"] = identity.serverInfo.model_dump(mode="json")
                            names = {item.name for item in (await session.list_tools()).tools}
                            captured["tools"] = sorted(names)
                            code_tool = "browser_run_code" if "browser_run_code" in names else "browser_run_code_unsafe"
                            captured["code_tool"] = code_tool
                            required = {code_tool, "browser_close", "browser_snapshot", "browser_console_messages"}
                            if config["screenshot"]:
                                required.add("browser_take_screenshot")
                            if not required.issubset(names):
                                raise ValueError("Catálogo incompatível com as ações delimitadas.")
                            bootstrap = "async (page) => ({stage: 'bootstrap', url: page.url()})"
                            self._result(await call(code_tool, {"code": bootstrap}))
                            captured["browser_executed"] = True
                            navigate = "async (page) => { await page.goto(" + json.dumps(config["url"], ensure_ascii=False) + \
                                ", {waitUntil: 'domcontentloaded'}); return {stage: 'navigate', url: page.url(), title: await page.title()}; }"
                            actions = [{"action": "navigate", "code": navigate}] + config["steps"]
                            for step in actions:
                                if is_cancelled():
                                    raise ExecutionCancelled("Operação de navegador cancelada.")
                                if step["action"] == "snapshot":
                                    await call("browser_snapshot", {})
                                    continue
                                code = step["code"] if step["action"] == "navigate" else self._step_code(step)
                                result = self._result(await call(code_tool, {"code": code}))
                                if _origin(result.get("url", "")) not in config["allowed_origins"]:
                                    raise ValueError("A navegação saiu das origens autorizadas.")
                                captured["results"].append(result)
                            await call("browser_console_messages", {"level": "error"})
                            if config["screenshot"]:
                                await call("browser_take_screenshot", {"type": "png", "filename": str(directory / "snapshot.png")})
                                captured["artifacts"] = []
                                for image in directory.glob("**/snapshot.png"):
                                    if image.is_symlink() or not image.resolve().is_relative_to(directory.resolve()):
                                        raise ValueError("Imagem fora do diretório de execução.")
                                    data = image.read_bytes()
                                    if len(data) > self.MAX_RESPONSE_BYTES:
                                        raise ValueError("Imagem excede limite de 8 MiB.")
                                    captured["artifacts"].append({"path": str(image), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
                                if not captured["artifacts"]:
                                    raise ValueError("Provider não entregou a imagem no diretório delimitado.")
                            group.cancel_scope.cancel()
                    if is_cancelled():
                        raise ExecutionCancelled("Operação de navegador cancelada.")
                finally:
                    # Prazo de limpeza separado do prazo que já expirou/cancelou.
                    with anyio.move_on_after(5, shield=True):
                        response = await call("browser_close", {})
                        closed = not response.get("isError", False)
                    captured["browser_close_confirmed"] = closed
                if not closed:
                    raise ValueError("Provider não confirmou o fechamento do navegador.")

    def action(self, config: Any) -> dict[str, Any]:
        request = self._validate(config)
        inventory = self.status()
        if request["operation"] == "status":
            return inventory
        if not inventory["available"]:
            return {**inventory, "operation": "run"}
        captured = {"results": [], "responses": [], "browser_executed": False,
                    "allowed_origins": request["allowed_origins"], "data_authority": "untrusted_page_content"}
        started = time.monotonic()
        status, error = "completed", None
        try:
            if is_cancelled():
                raise ExecutionCancelled("Cancelado antes de iniciar o browser.")
            import anyio
            import sniffio
            with tempfile.TemporaryFile(mode="w+") as log:
                # asyncio.to_thread copia o marcador sniffio do loop MCP, embora
                # o worker não tenha loop. Preservar o Event R825 e limpar só
                # esse marcador durante a criação do loop privado.
                library_token = sniffio.current_async_library_cvar.set(None)
                try:
                    anyio.run(self._exchange, request, inventory, captured, log)
                    if is_cancelled():
                        raise ExecutionCancelled("Cancelado durante a conclusão do navegador.")
                finally:
                    sniffio.current_async_library_cvar.reset(library_token)
                    log.seek(0)
                    captured["stderr_excerpt"] = log.read(2000)
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            status = "cancelled" if is_cancelled() or isinstance(exc, ExecutionCancelled) else "failed"
            leaves = []
            def describe(value):
                nested = getattr(value, "exceptions", None)
                if nested:
                    for child in nested:
                        describe(child)
                else:
                    leaves.append(type(value).__name__ + ": " + str(value))
            describe(exc)
            error = "; ".join(leaves)[:1000]
        digest = hashlib.sha256(json.dumps(captured, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        return {"operation": "run", "status": status, "success": status == "completed",
                "browser_executed": captured["browser_executed"], "response": captured,
                "response_sha256": digest, "request_sha256": hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                "provenance": inventory["provenance"], "duration_seconds": time.monotonic() - started,
                "error": error, "externally_validated": False}


def compact_browser_report(report: dict[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    result = {key: value for key, value in report.items() if key != "response"}
    response = report.get("response")
    if response is None:
        return result
    payload = json.dumps(response, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    base = Path(root or Path(__file__).resolve().parents[1]).resolve()
    directory = base / ".opencode/browser/evidence"
    temporary = None
    try:
        if report.get("response_sha256", digest) != digest:
            raise ValueError("Hash da resposta diverge da evidência.")
        if not directory.resolve().is_relative_to(base):
            raise ValueError("Diretório de evidência fora do workspace.")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (digest + ".json")
        if path.is_symlink():
            raise ValueError("Destino de evidência contém link simbólico.")
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        result["evidence_artifact"] = {"path": str(path), "sha256": digest, "bytes": len(payload), "complete": True}
        results = response.get("results", [])
        result["completed_actions"] = [str(item.get("stage", "unknown"))[:32] for item in results]
        if results:
            last = results[-1]
            result["final_page"] = {"url": str(last.get("url", ""))[:600],
                                    "title": str(last.get("title", ""))[:200],
                                    "text_excerpt": str(last.get("text", ""))[:800]}
        result["browser_close_confirmed"] = response.get("browser_close_confirmed", False)
        result["artifacts"] = response.get("artifacts", [])
        result["response_delivery"] = "summary_with_complete_local_artifact"
    except (OSError, ValueError) as exc:
        result.update(status="failed", success=False, error_code="evidence_export_failed", error=str(exc))
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return result
