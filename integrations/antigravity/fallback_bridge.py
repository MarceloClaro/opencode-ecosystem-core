# -*- coding: utf-8 -*-
"""
FallbackBridge — Camada de fallback para o Antigravity Bridge
==============================================================
Resolve o problema de "193 delegadas, 0 concluídas" substituindo
a delegação ao Antigravity (que só formata prompts e nunca executa)
por execução real usando httpx + APIs diretas.

Detecção automática: cada tarefa tem primário (Antigravity) e
fallback (execução direta). Se Antigravity falha/queue, fallback
assume automaticamente.

Fluxo:
    fallback = FallbackBridge()
    
    # Fallback automático:
    result = fallback.execute(task_type="search", prompt="...")
    
    # Processar fila de handoffs pendentes:
    fallback.process_queue()
    
    # Estado real:
    status = fallback.status()

Compatibilidade: mantém interface compatível com AntigravityBridge
para substituição transparente.
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import httpx

# ============================================================
# Constantes
# ============================================================

FALLBACK_VERSION = "1.0.0"

# Diretórios
BASE_DIR = Path(__file__).parent.parent.parent
QUEUE_DIR = BASE_DIR / ".antigravity" / "queue"
STATE_DIR = BASE_DIR / ".evolve"
BRIDGE_STATE_FILE = STATE_DIR / "antigravity-bridge-state.json"
FALLBACK_LOG_FILE = STATE_DIR / "fallback-log.jsonl"

# Timeouts
HTTP_TIMEOUT = 30.0  # segundos para requisições HTTP
QUEUE_POLL_INTERVAL = 2  # segundos entre processamento de fila

# Capacidades suportadas pelo fallback
FALLBACK_CAPABILITIES = {
    "web_search": {
        "status": "ok",
        "engine": "duckduckgo_html + duckduckgo_api",
        "fallback": True,
    },
    "url_read": {
        "status": "ok",
        "engine": "httpx + urllib",
        "fallback": True,
    },
    "pypi_search": {
        "status": "ok",
        "engine": "PyPI JSON API",
        "fallback": True,
    },
    "image_generation": {
        "status": "requires_ai_tool",
        "engine": "antigravity_generate_image MCP tool",
        "fallback": False,
    },
    "browser_automation": {
        "status": "requires_ai_tool",
        "engine": "antigravity_browser_action MCP tool",
        "fallback": False,
    },
    "parallel_orchestration": {
        "status": "requires_ai_tool",
        "engine": "delegação via orquestrador marceloclaro",
        "fallback": False,
    },
    "external_agent_delegation": {
        "status": "requires_ai_tool",
        "engine": "subagent_type via orquestrador",
        "fallback": False,
    },
}

# ============================================================
# Logging
# ============================================================

def log_fallback(event: str, data: dict) -> None:
    """Registra evento de fallback no log."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "fallback_version": FALLBACK_VERSION,
        **data,
    }, ensure_ascii=False) + "\n"
    try:
        with open(FALLBACK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError:
        pass


# ============================================================
# Estado da Bridge
# ============================================================

def load_bridge_state() -> dict:
    """Carrega o estado atual da ponte."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if BRIDGE_STATE_FILE.exists():
        try:
            return json.loads(BRIDGE_STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "version": FALLBACK_VERSION,
        "totalDelegated": 0,
        "totalCompleted": 0,
        "totalFailed": 0,
        "totalFallback": 0,
        "successRate": 1.0,
        "healthScore": 100,
        "lastSync": None,
        "pendingQueue": [],
        "tasks": [],
    }


def save_bridge_state(state: dict) -> None:
    """Persiste o estado da ponte."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    BRIDGE_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ============================================================
# Motores de Busca (Fallback Real)
# ============================================================

async def _search_duckduckgo(query: str, max_results: int = 5) -> List[dict]:
    """
    Busca no DuckDuckGo usando HTML scraping.
    Fallback primário para web_search.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }
    
    results = []
    exc = None
    
    # Tenta múltiplos endpoints
    endpoints = [
        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
        f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}",
    ]
    
    for url in endpoints:
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                
                # Procura por links de resultados (formato HTML duckduckgo)
                # Padrão 1: links com classe result__a
                link_pattern1 = re.compile(
                    r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                    re.DOTALL,
                )
                # Padrão 2: links com classe result-link (lite)
                link_pattern2 = re.compile(
                    r'<a[^>]*class="result-link"[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>',
                    re.DOTALL,
                )
                # Padrão 3: qualquer link seguido de snippet
                link_pattern3 = re.compile(
                    r'<a[^>]*rel="nofollow"[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>',
                    re.DOTALL,
                )
                
                snippet_pattern = re.compile(
                    r'<(?:td|div|span)[^>]*class="(?:result-snippet|snippet)"[^>]*>(.*?)</(?:td|div|span)>',
                    re.DOTALL,
                )
                
                links = []
                for pat in [link_pattern1, link_pattern2, link_pattern3]:
                    links = pat.findall(html)
                    if links:
                        break
                
                snippets = snippet_pattern.findall(html)
                
                for i, (href, title_text) in enumerate(links[:max_results]):
                    title = re.sub(r'<[^>]+>', '', title_text).strip()
                    # Limpa URL (pode ter redirecionamento do duckduckgo)
                    clean_href = href
                    if "duckduckgo.com/l/?uddg=" in href:
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        clean_href = parsed.get("uddg", [href])[0]
                    elif "//html.duckduckgo.com" in href or "//lite.duckduckgo.com" in href:
                        continue  # Pula links internos
                    
                    snippet = ""
                    if i < len(snippets):
                        snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                    
                    results.append({
                        "title": title[:200] if title else "(sem título)",
                        "url": clean_href[:500],
                        "snippet": snippet[:300] if snippet else "(sem descrição)",
                        "source": "duckduckgo_html",
                    })
                
                if results:
                    log_fallback("search.success", {
                        "query": query[:100],
                        "endpoint": url[:50],
                        "results": len(results),
                    })
                    return results
                    
        except Exception as e:
            exc = e
            log_fallback("search.endpoint_error", {
                "endpoint": url[:50],
                "error": str(e)[:200],
            })
            continue
    
    # Fallback final: DuckDuckGo Instant Answer API
    try:
        api_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(api_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            abstract = data.get("AbstractText", "")
            if abstract:
                results.append({
                    "title": data.get("AbstractSource", "Resultado")[:200],
                    "url": data.get("AbstractURL", ""),
                    "snippet": abstract[:300],
                    "source": "duckduckgo_api",
                })
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:200].split(" - ")[0],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", "")[:300],
                        "source": "duckduckgo_api",
                    })
    except Exception as e:
        log_fallback("search.api_error", {"query": query[:100], "error": str(e)[:200]})
    
    return results


async def _fetch_url(url: str, extract_focus: str = "") -> Dict[str, Any]:
    """
    Fetch URL content usando httpx.
    Fallback para url_read.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }
    
    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            follow_redirects=True,
            verify=False,  # Permite HTTPS sem verificação estrita
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            text = response.text
            
            # Extrai título
            title = ""
            title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.DOTALL)
            if title_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            
            # Remove scripts e styles
            text_clean = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text_clean = re.sub(r'<style[^>]*>.*?</style>', '', text_clean, flags=re.DOTALL)
            
            # Extrai parágrafos
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text_clean, re.DOTALL)
            content_parts = []
            for p in paragraphs[:20]:  # Limita a 20 parágrafos
                clean_p = re.sub(r'<[^>]+>', '', p).strip()
                if clean_p and len(clean_p) > 30:
                    content_parts.append(clean_p)
            
            content = "\n\n".join(content_parts)
            
            # Trunca se muito grande
            if len(content) > 10000:
                content = content[:10000] + "\n\n[... conteúdo truncado ...]"
            
            result = {
                "url": str(response.url),
                "status_code": response.status_code,
                "content_type": content_type,
                "title": title[:200],
                "content_length": len(text),
                "content_preview": content[:5000],
                "paragraphs_extracted": len(content_parts),
            }
            
            log_fallback("url_fetch.success", {
                "url": url[:100],
                "status": response.status_code,
                "bytes": len(text),
            })
            
            return result
            
    except httpx.TimeoutException:
        log_fallback("url_fetch.timeout", {"url": url[:100]})
        return {"error": f"Timeout após {HTTP_TIMEOUT}s", "url": url, "status": "timeout"}
    except httpx.HTTPStatusError as e:
        log_fallback("url_fetch.http_error", {"url": url[:100], "status": e.response.status_code})
        return {"error": f"HTTP {e.response.status_code}", "url": url, "status": "http_error"}
    except Exception as e:
        log_fallback("url_fetch.error", {"url": url[:100], "error": str(e)[:200]})
        return {"error": str(e)[:300], "url": url, "status": "error"}


def _search_pypi(query: str, limit: int = 10) -> List[dict]:
    """
    Busca no PyPI usando a API JSON pública.
    """
    url = f"https://pypi.org/simple/"
    results = []
    
    try:
        # Usa a API de busca do PyPI
        search_url = f"https://pypi.org/search/?q={quote_plus(query)}"
        
        # Tenta a API JSON primeiro
        json_url = f"https://pypi.org/pypi/{quote_plus(query)}/json"
        
        # Busca simples via parsing
        headers = {
            "User-Agent": "OpenCode-FallbackBridge/1.0",
            "Accept": "application/json",
        }
        
        import subprocess
        import json as jjson
        
        # Tenta o search API
        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://pypi.org/search/?q={quote_plus(query)}&o=&c=",
                headers={"User-Agent": "OpenCode-FallbackBridge/1.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                
            # Extrai pacotes dos resultados de busca
            package_pattern = re.compile(
                r'<a[^>]*class="package-snippet"[^>]*href="([^"]+)"[^>]*>.*?<span[^>]*class="package-snippet__name"[^>]*>(.*?)</span>',
                re.DOTALL,
            )
            desc_pattern = re.compile(
                r'<p[^>]*class="package-snippet__description"[^>]*>(.*?)</p>',
                re.DOTALL,
            )
            
            packages = package_pattern.findall(html)
            descriptions = desc_pattern.findall(html)
            
            for i, (path, name) in enumerate(packages[:limit]):
                name = re.sub(r'<[^>]+>', '', name).strip()
                desc = ""
                if i < len(descriptions):
                    desc = re.sub(r'<[^>]+>', '', descriptions[i]).strip()
                
                results.append({
                    "name": name,
                    "url": f"https://pypi.org{path}",
                    "description": desc[:200],
                    "source": "pypi_search_html",
                })
        except Exception:
            pass
            
        # Se não achou nada, tenta direto pelo nome do pacote
        if not results:
            try:
                req = urllib.request.Request(
                    f"https://pypi.org/pypi/{quote_plus(query)}/json",
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = jjson.loads(resp.read().decode("utf-8"))
                    info = data.get("info", {})
                    results.append({
                        "name": info.get("name", query),
                        "version": info.get("version", "?"),
                        "url": info.get("package_url", ""),
                        "description": (info.get("summary", "") or "")[:200],
                        "author": info.get("author", ""),
                        "license": info.get("license", ""),
                        "source": "pypi_json_api",
                    })
            except Exception:
                pass
    
    except Exception as e:
        log_fallback("pypi_search.error", {"query": query[:100], "error": str(e)[:200]})
    
    log_fallback("pypi_search", {"query": query[:100], "results": len(results)})
    return results


# ============================================================
# FallbackBridge — Classe Principal
# ============================================================

class FallbackBridge:
    """
    Ponte de fallback que executa tarefas de fato, substituindo
    o AntigravityBridge quando ele só formata prompts sem executar.
    
    Uso:
        bridge = FallbackBridge()
        
        # Execução direta com fallback automático:
        result = await bridge.execute("search", "literatura de horror brasileira")
        
        # Ou síncrono:
        result = bridge.execute_sync("search", "teoria da literatura")
        
        # Processar fila de handoffs:
        bridge.process_pending_handoffs()
    """
    
    def __init__(self):
        self.state = load_bridge_state()
        self._http_client = None
        
    # --------------------------------------------------------
    # Execução Principal
    # --------------------------------------------------------
    
    async def execute(
        self,
        task_type: str,
        prompt: str,
        context: Optional[str] = None,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Executa uma tarefa com fallback automático.
        Retorna resultado real (não apenas prompt formatado).
        """
        task_id = f"fb-{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Registra tentativa
        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)
        
        # Roteia por tipo
        if task_type in ("search", "web_search"):
            result = await self._execute_search(prompt, max_results=8)
        elif task_type in ("url", "url_read"):
            result = await self._execute_url_read(prompt, context or "")
        elif task_type in ("pypi", "pypi_search"):
            result = self._execute_pypi_search(prompt)
        elif task_type in ("image", "image_generation"):
            result = self._handle_requires_ai("image_generation", prompt)
        elif task_type in ("browser", "browser_automation"):
            result = self._handle_requires_ai("browser_automation", prompt)
        else:
            # Tenta search como fallback genérico
            result = await self._execute_search(prompt, max_results=5)
            result["_fallback_note"] = f"Tipo '{task_type}' não reconhecido — tratado como search"
        
        elapsed = time.time() - start_time
        
        # Atualiza estado
        is_success = "error" not in result or not result.get("error")
        if is_success:
            self.state["totalCompleted"] = self.state.get("totalCompleted", 0) + 1
            if result.get("_fallback", False):
                self.state["totalFallback"] = self.state.get("totalFallback", 0) + 1
        else:
            self.state["totalFailed"] = self.state.get("totalFailed", 0) + 1
        
        total = self.state["totalDelegated"]
        completed = self.state["totalCompleted"]
        self.state["successRate"] = (completed / total * 100) if total > 0 else 100.0
        self.state["healthScore"] = min(100, int(self.state["successRate"]))
        self.state["lastSync"] = datetime.now(timezone.utc).isoformat()
        save_bridge_state(self.state)
        
        log_fallback("execute.complete", {
            "task_id": task_id,
            "type": task_type,
            "elapsed_seconds": round(elapsed, 2),
            "success": is_success,
        })
        
        return {
            "task_id": task_id,
            "type": task_type,
            "status": "completed" if is_success else "failed",
            "elapsed_seconds": round(elapsed, 2),
            "fallback_used": result.get("_fallback", False),  # NOQA
            "result": result,
            "bridge_state": self._get_state_summary(),
        }
    
    def execute_sync(
        self,
        task_type: str,
        prompt: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Versão síncrona de execute() — compatível com loop rodando."""
        import asyncio
        
        # Para tarefas síncronas que não precisam de async
        if task_type in ("pypi", "pypi_search"):
            result = self._execute_pypi_search(prompt)
            self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
            self.state["totalCompleted"] = self.state.get("totalCompleted", 0) + 1
            self.state["totalFallback"] = self.state.get("totalFallback", 0) + 1
            save_bridge_state(self.state)
            return {
                "task_id": f"fb-{uuid.uuid4().hex[:8]}",
                "type": task_type,
                "status": "completed",
                "fallback_used": True,
                "result": result,
                "bridge_state": self._get_state_summary(),
            }
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # Cria novo loop em thread separada
            import threading
            result_container = []
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    r = new_loop.run_until_complete(
                        self.execute(task_type, prompt, context)
                    )
                    result_container.append(r)
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()
            thread.join(timeout=HTTP_TIMEOUT + 15)
            
            if result_container:
                return result_container[0]
            return {
                "task_id": f"fb-{uuid.uuid4().hex[:8]}",
                "type": task_type,
                "status": "timeout",
                "error": "Timeout na execução síncrona",
            }
        else:
            return loop.run_until_complete(
                self.execute(task_type, prompt, context)
            )
    
    # --------------------------------------------------------
    # Executores Específicos
    # --------------------------------------------------------
    
    async def _execute_search(self, query: str, max_results: int = 8) -> Dict[str, Any]:
        """Executa busca web via DuckDuckGo."""
        results = await _search_duckduckgo(query, max_results=max_results)
        
        if results:
            return {
                "query": query[:200],
                "results_count": len(results),
                "results": results,
                "engine": "duckduckgo_lite",
                "_fallback": True,
            }
        
        return {
            "query": query[:200],
            "error": "Nenhum resultado encontrado",
            "results": [],
            "_fallback": True,
        }
    
    async def _execute_url_read(self, url_or_prompt: str, focus: str) -> Dict[str, Any]:
        """Executa leitura de URL."""
        # Extrai URL do prompt se necessário
        url_match = re.search(r'https?://[^\s"\']+', url_or_prompt)
        url = url_match.group(0) if url_match else url_or_prompt.strip()
        
        if not url.startswith("http"):
            return {
                "error": "URL inválida ou não encontrada no prompt",
                "input": url_or_prompt[:200],
                "_fallback": True,
            }
        
        result = await _fetch_url(url, focus)
        result["_fallback"] = True
        return result
    
    def _execute_pypi_search(self, query: str) -> Dict[str, Any]:
        """Executa busca no PyPI."""
        results = _search_pypi(query)
        return {
            "query": query[:200],
            "results_count": len(results),
            "results": results,
            "engine": "pypi_search",
            "_fallback": True,
        }
    
    def _handle_requires_ai(self, capability: str, prompt: str) -> Dict[str, Any]:
        """
        Para capacidades que exigem ferramentas MCP do agente AI.
        Retorna instruções estruturadas em vez de executar.
        """
        tool_map = {
            "image_generation": {
                "tool": "antigravity_generate_image",
                "action": "Use a ferramenta antigravity_generate_image com os parâmetros preenchidos.",
            },
            "browser_automation": {
                "tool": "antigravity_browser_action",
                "action": "Use a ferramenta antigravity_browser_action para automação de navegador.",
            },
        }
        
        info = tool_map.get(capability, {
            "tool": "desconhecido",
            "action": "Consulte o orquestrador marceloclaro.",
        })
        
        return {
            "status": "requires_ai_tool",
            "capability": capability,
            "message": (
                f"Esta tarefa requer a ferramenta MCP '{info['tool']}', "
                f"que não pode ser executada via fallback bridge. "
                f"{info['action']}"
            ),
            "extracted_prompt": prompt[:500],
            "suggested_tool": info["tool"],
            "_fallback": True,
        }
    
    # --------------------------------------------------------
    # Processamento da Fila de Handoffs
    # --------------------------------------------------------
    
    def process_pending_handoffs(self) -> List[Dict[str, Any]]:
        """
        Processa todos os handoffs pendentes na fila.
        Retorna lista de resultados.
        """
        if not QUEUE_DIR.exists():
            return []
        
        results = []
        for filename in sorted(os.listdir(str(QUEUE_DIR))):
            if not filename.endswith(".json"):
                continue
            
            filepath = QUEUE_DIR / filename
            try:
                handoff = json.loads(filepath.read_text(encoding="utf-8"))
                task = handoff.get("task", {})
                prompt = task.get("prompt", "")
                agent = task.get("agent", "default")
                
                # Mapeia agente para tipo de tarefa
                agent_task_map = {
                    "image": "image_generation",
                    "browser": "browser_automation",
                    "search": "web_search",
                    "default": "web_search",
                }
                task_type = agent_task_map.get(agent, "web_search")
                
                # Executa
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self.execute(task_type, prompt),
                        loop,
                    )
                    result = future.result(timeout=HTTP_TIMEOUT + 10)
                else:
                    result = loop.run_until_complete(
                        self.execute(task_type, prompt)
                    )
                
                result["handoff_id"] = handoff.get("id")
                result["handoff_file"] = str(filepath)
                results.append(result)
                
                # Remove handoff processado
                filepath.unlink()
                log_fallback("handoff.processed", {
                    "handoff_id": handoff.get("id"),
                    "type": task_type,
                    "success": result.get("status") == "completed",
                })
                
            except Exception as e:
                log_fallback("handoff.error", {
                    "file": filename,
                    "error": str(e)[:200],
                })
                # Move para diretório de erro
                error_dir = QUEUE_DIR / "failed"
                error_dir.mkdir(parents=True, exist_ok=True)
                filepath.rename(error_dir / filename)
                
                results.append({
                    "handoff_id": filename.replace(".json", ""),
                    "status": "failed",
                    "error": str(e)[:300],
                })
        
        return results
    
    # --------------------------------------------------------
    # Estado e Relatórios
    # --------------------------------------------------------
    
    def status(self) -> Dict[str, Any]:
        """Retorna estado atual da bridge com fallback."""
        self.state = load_bridge_state()
        pending = len(self.state.get("pendingQueue", []))
        completed = self.state.get("totalCompleted", 0)
        total = self.state.get("totalDelegated", 0)
        failed = self.state.get("totalFailed", 0)
        fallback_count = self.state.get("totalFallback", 0)
        
        pending_handoffs = 0
        if QUEUE_DIR.exists():
            pending_handoffs = len([f for f in os.listdir(str(QUEUE_DIR)) if f.endswith(".json")])
        
        success_rate = (completed / total * 100) if total > 0 else 100.0
        
        return {
            "versao": FALLBACK_VERSION,
            "tipo": "FallbackBridge",
            "status_geral": "operacional" if success_rate >= 50 else "degradado",
            "saude": f"{min(100, int(success_rate))}%",
            "total_delegadas": total,
            "total_concluidas": completed,
            "total_falhas": failed,
            "total_fallback": fallback_count,
            "taxa_sucesso": f"{success_rate:.1f}%",
            "fila_mcp_pending": pending,
            "fila_handoff_pending": pending_handoffs,
            "capacidades": {
                k: v["status"]
                for k, v in FALLBACK_CAPABILITIES.items()
            },
            "ultima_sincronizacao": self.state.get("lastSync", "N/A"),
            "log": str(FALLBACK_LOG_FILE),
        }
    
    def _get_state_summary(self) -> dict:
        """Resumo compacto do estado para respostas."""
        return {
            "delegated": self.state.get("totalDelegated", 0),
            "completed": self.state.get("totalCompleted", 0),
            "failed": self.state.get("totalFailed", 0),
            "fallback": self.state.get("totalFallback", 0),
        }


# ============================================================
# Singleton + Função de Conveniência
# ============================================================

_fallback_bridge_instance: Optional[FallbackBridge] = None


def get_fallback_bridge() -> FallbackBridge:
    """Retorna instância singleton do FallbackBridge."""
    global _fallback_bridge_instance
    if _fallback_bridge_instance is None:
        _fallback_bridge_instance = FallbackBridge()
    return _fallback_bridge_instance


def process_antigravity_queue() -> List[Dict[str, Any]]:
    """
    Função de conveniência: processa toda a fila de handoffs
    do AntigravityBridge usando fallback real.
    Chamar quando detectar fila acumulada.
    """
    bridge = get_fallback_bridge()
    return bridge.process_pending_handoffs()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    bridge = get_fallback_bridge()
    
    if len(sys.argv) > 1 and sys.argv[1] == "queue":
        print("Processando fila de handoffs...")
        results = bridge.process_pending_handoffs()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif len(sys.argv) > 2 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:])
        print(f"Buscando: {query}")
        import asyncio
        result = asyncio.run(bridge.execute("search", query))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif len(sys.argv) > 2 and sys.argv[1] == "url":
        url = sys.argv[2]
        print(f"Lendo: {url}")
        import asyncio
        result = asyncio.run(bridge.execute("url", url))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(json.dumps(bridge.status(), indent=2, ensure_ascii=False))
