"""Registra o ciclo do projeto, sem alegar auditoria científica externa."""
import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from evolution.cycles import EvolutionRegistry

registry = EvolutionRegistry()
objective = "SPEC-935-R640: conectar rede coordenada Transformer, executores e memória"
existing = next((cycle for cycle in registry.cycles if cycle.objective == objective), None)
if existing is None:
    shutil.copy2(registry.state_path, ROOT / ".backups/r640/cycles-before-record.json")
    existing = registry.record(objective, [
        "Orquestrador marceloclaro padrão; oitavo MCP ecosystem-network e comando ecosystem",
        "Execução de leitura Claude/Antigravity/Codex com prazo, passos e fallback explícito",
        "Instruções federadas com hashes, conclusão Blackboard e reflexão MetaBus",
        "Relatórios legados distinguem instalação, preview e execução",
        "Provas reais Codex e Antigravity; Claude recusado por saldo; MCP default concluiu via fallback",
    ], lessons=[
        "Binário instalado não comprova autenticação, saldo ou inferência",
        "Ambiente MCP pode remover WSL_DISTRO_NAME: detectar pelo sistema e converter com wslpath",
        "Antigravity usa response/status SUCCESS; configuração de flags deve preservar plan",
        "Conclusão rejeitada pelo gate não pode persistir completed/success=True",
        "Atenção multicritério e avaliação heurística não são treinamento nem validação científica externa",
    ])
print(json.dumps({"round_id": existing.round_id, "total_cycles": len(registry.cycles),
                  "audited": existing.audited, "objective": existing.objective}, ensure_ascii=False))
