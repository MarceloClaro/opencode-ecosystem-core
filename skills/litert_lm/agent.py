"""
LiteRT-LM Agent — Agente A2A de Inferência On-Device
=====================================================
Agente-executor que encapsula o LiteRTLMSkill como um agente de primeira
classe no ecossistema OpenCode. Registrável no Blackboard com capacidades
próprias, torna "executar inferência on-device" uma tarefa delegável via
o runtime multiagente — sujeita a matching por atenção, Trust Engine e
Token Economy.

Uso:
    agent = LiteRTLMAgent()
    result = agent.execute({"action": "run", "model_ref": "...", "prompt": "..."})

Ver SPEC-935-R209 (skill) e este módulo (agente A2A).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .skill import LiteRTLMSkill

LITERT_AGENT_ID = "litert-lm-agent"
LITERT_CAPABILITIES = [
    "litert-lm:list",
    "litert-lm:run",
    "litert-lm:chat",
    "litert-lm:import",
    "litert-lm:serve",
    "litert-lm:info",
    "litert-lm:delete",
    "inference-on-device",
    "llm-on-device",
]


class LiteRTLMAgent:
    """Agente-executor que realiza inferência on-device via LiteRT-LM.

    Encapsula LiteRTLMSkill e expõe cada operação como uma ação delegável
    pelo Blackboard. O retorno segue o padrão do ecossistema:
    ``{"ok": True, ...}`` em sucesso, ``{"ok": False, "error": ...}``
    em falha.
    """

    agent_id = LITERT_AGENT_ID
    name = "LiteRT-LM Agent"
    description = (
        "Agente de inferência on-device via LiteRT-LM (Google AI Edge). "
        "Executa modelos LLM localmente (Gemma 4, Qwen3) com suporte a "
        "texto, imagem (visão), streaming e servidor OpenAI-compatible. "
        "Operações: list, run, chat, import, serve, info, delete."
    )
    capabilities = LITERT_CAPABILITIES

    def __init__(self, skill: Optional[LiteRTLMSkill] = None):
        self.skill = skill or LiteRTLMSkill()

    # ── Registro A2A ─────────────────────────────────────────────────────

    def register_payload(self) -> Dict[str, Any]:
        """Payload para ``metabus.publish('agent.register', ...)``."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": list(self.capabilities),
            "schema": {
                "action": (
                    "str — operação: list | run | chat | import | serve | info | delete"
                ),
                "model_ref": "str — ID ou caminho do modelo (opcional em list)",
                "prompt": "str — texto do prompt (obrigatório em run)",
                "images": "List[str] — caminhos de imagens (opcional em run/chat)",
                "backend": "str — cpu | gpu (opcional, default cpu)",
                "temperature": "float — temperatura de amostragem (opcional)",
                "max_tokens": "int — máx. tokens de saída (opcional)",
                "repo_id": "str — repositório HuggingFace (obrigatório em import)",
                "port": "int — porta do servidor (opcional, default 9379)",
            },
        }

    # ── Execução ─────────────────────────────────────────────────────────

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executa a ação solicitada e retorna resultado padronizado.

        Args:
            context: Dicionário com ``action`` e parâmetros específicos.

        Returns:
            ``{"ok": True, ...}`` em sucesso ou
            ``{"ok": False, "error": str}`` em falha (sem exceção).
        """
        ctx = context or {}
        action = ctx.get("action", "list")

        try:
            if action == "list":
                return self._action_list()
            elif action == "run":
                return self._action_run(ctx)
            elif action == "chat":
                return self._action_chat(ctx)
            elif action == "import":
                return self._action_import(ctx)
            elif action == "serve":
                return self._action_serve(ctx)
            elif action == "info":
                return self._action_info(ctx)
            elif action == "delete":
                return self._action_delete(ctx)
            else:
                return {"ok": False, "error": f"ação desconhecida: {action}"}
        except Exception as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # ── Ações ────────────────────────────────────────────────────────────

    def _action_list(self) -> Dict[str, Any]:
        models = self.skill.list_models()
        return {
            "ok": True,
            "models": [
                {
                    "model_id": m.model_id,
                    "path": m.model_path,
                    "size_bytes": m.file_size_bytes,
                }
                for m in models
            ],
            "count": len(models),
        }

    def _action_run(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        model_ref = ctx.get("model_ref")
        prompt = ctx.get("prompt")
        if not model_ref:
            return {"ok": False, "error": "'model_ref' é obrigatório para run"}
        if not prompt:
            return {"ok": False, "error": "'prompt' é obrigatório para run"}

        output = self.skill.run(
            model_ref,
            prompt=prompt,
            images=ctx.get("images"),
            backend=ctx.get("backend", "cpu"),
            temperature=ctx.get("temperature"),
            top_k=ctx.get("top_k"),
            top_p=ctx.get("top_p"),
            seed=ctx.get("seed"),
            max_tokens=ctx.get("max_tokens"),
            no_template=ctx.get("no_template", False),
        )
        return {"ok": True, "output": output, "model": model_ref}

    def _action_chat(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        model_ref = ctx.get("model_ref")
        if not model_ref:
            return {"ok": False, "error": "'model_ref' é obrigatório para chat"}

        prompt = ctx.get("prompt", "")
        images = ctx.get("images")

        session = self.skill.chat(
            model_ref,
            backend=ctx.get("backend", "cpu"),
            temperature=ctx.get("temperature"),
            top_k=ctx.get("top_k"),
            top_p=ctx.get("top_p"),
            seed=ctx.get("seed"),
            max_tokens=ctx.get("max_tokens"),
            system_instruction=ctx.get("system_instruction"),
            no_template=ctx.get("no_template", False),
            stream=False,
            max_num_images=len(images) if images else 0,
            vision_backend=ctx.get("vision_backend"),
        )
        try:
            output = session.send(prompt, attachments=images)
            return {"ok": True, "output": output, "model": model_ref}
        finally:
            session.close()

    def _action_import(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        repo_id = ctx.get("repo_id")
        if not repo_id:
            return {"ok": False, "error": "'repo_id' é obrigatório para import"}
        info = self.skill.import_model(
            repo_id,
            filename=ctx.get("filename"),
            token=ctx.get("token"),
        )
        return {
            "ok": True,
            "model_id": info.model_id,
            "path": info.model_path,
            "size_bytes": info.file_size_bytes,
        }

    def _action_serve(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        model_ref = ctx.get("model_ref")
        if not model_ref:
            return {"ok": False, "error": "'model_ref' é obrigatório para serve"}
        server = self.skill.serve(
            model_ref,
            host=ctx.get("host", "0.0.0.0"),
            port=ctx.get("port", 9379),
            backend=ctx.get("backend", "cpu"),
            max_tokens=ctx.get("max_tokens", 4096),
            temperature=ctx.get("temperature", 0.7),
        )
        return {
            "ok": True,
            "server": f"{server.host}:{server.port}",
            "model": model_ref,
            "endpoint": f"/v1/chat/completions",
        }

    def _action_info(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        model_ref = ctx.get("model_ref")
        if not model_ref:
            return {"ok": False, "error": "'model_ref' é obrigatório para info"}
        metadata = self.skill.inspect(model_ref)
        return {"ok": True, "model": model_ref, "metadata": metadata}

    def _action_delete(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        model_ref = ctx.get("model_ref")
        if not model_ref:
            return {"ok": False, "error": "'model_ref' é obrigatório para delete"}
        removed = self.skill.delete_model(model_ref)
        return {"ok": True, "removed": removed, "model": model_ref}
