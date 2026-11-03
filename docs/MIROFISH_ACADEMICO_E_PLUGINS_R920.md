# MiroFish acadêmico e plugins locais — R920–R923

## Demonstração executada

Motor **MIT local** composto com verificações acadêmicas do Core, sem OASIS
externo/AGPL, LLM, pareceristas humanos ou dados empíricos. Protocolo didático:

- 7 etapas: projeto, metodologia, qualificação, análise, resultados, pré-defesa e defesa;
- 3 situações: base, banca divergente e indisponibilidade hipotética de fonte;
- grupos efêmeros: cientistas de método/resultados e banca interdisciplinar;
- 21 casos, 42 rounds, 84 ações; reserva consumida de 252 ações;
- uma revisão-base de 29 papéis por execução, reutilizada entre os casos.

Repetir com seed 42 preservou a trajetória
`e128925d78e1bb2a7d902b6298ae3a2285624ffc788ea49935bd10d75691d591`.
`completed` significa execução operacional concluída. A pesquisa didática
ficou `blocked`, com 13 objeções pendentes. Sentimento não vira nota nem
aprovação; perguntas têm origem, alvos e evidências exigidas, sem respostas inventadas.

```python
from marceloclaro.orchestrator import MarceloClaroOrchestrator
core = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
# project segue o intake existente: artifact_path, claims, sources, context etc.
plano = core.academic_rigor_action({
    "operation": "simulation_plan", "project": project, "seed": 42,
    "cases": [{"case_id": "defesa-adversa", "stage": "defesa",
               "group": "banca_interdisciplinar", "scenario": "banca_divergente",
               "rounds": 4, "agents": 6}],
    "limits": {"max_actions": 128, "timeout_seconds": 30}
})
resultado = core.academic_rigor_action({"operation": "simulation_run", "plan": plano})
```

Artefato/fontes são revalidados antes de executar; orçamento global, não por
cenário. Cancelamento/prazo são cooperativos entre casos. Saída parcial é
explícita. Para perguntas/respostas interativas reais, usar `banca_start`,
`banca_question`, `banca_answer` com turn_id e `banca_report`; não equivale a
uma defesa acadêmica efetivamente realizada ou a julgamento humano.

## Plugins locais selecionados

| Plugin | Resultado observado | Limite |
|---|---|---|
| Sequence Viewer 0.1.52 | 3 arquivos instrucionais/licença MIT no registro canônico existente | Sem scripts, MCP do host, ativação ou inferência |
| Zotero 0.1.2 | reference_only, motivo license_missing | MIT no manifesto não substitui texto de licença; nada copiado |
| Outros pacotes legados | Preservados, sem nova cópia em lote | O caminho novo não saneia retroativamente importações anteriores |

Bits 777 sintéticos foram reconhecidos pela montagem efetiva 9p/DrvFS, não
por prefixo de caminho. Textos UTF-8 inertes, licenças e políticas permanecem
sujeitos aos gates. Origem sem chmod; destino sem bit executável. Scripts,
hooks, transportes, credenciais e corpos restritos não são importados.
Versões antigas retidas continuam version_mismatch no status, sem atualização
silenciosa ou bloqueio de plugins independentes. O escopo selecionado não
percorre corpos/credenciais de plugins não selecionados.

```python
inventario = core.scientific_plugin_action(
    "inventory_local", cache_root="/mnt/c/Users/marce/.codex/plugins/cache",
    plugin_ids=["sequence-viewer", "zotero"])
copia = core.scientific_plugin_action(
    "extract_selected", cache_root="/mnt/c/Users/marce/.codex/plugins/cache",
    plugin_ids=["sequence-viewer", "zotero"])
```

Não controla GUI do ChatGPT, transfere OAuth ou cria capacidades hospedadas.
Instruções dependentes de scripts/conectores não importados são referências
para handoff ao host, não ferramentas funcionais por mera cópia.

Reprodução didática: `python3 -m scripts.demo_core_r923`.
Fixture: `examples/academic-simulation-r920/protocol.md`.
Saídas: `outputs/core-r923/`, estado acadêmico e observações MetaBus sem
promoção de confiança. Repetir reexecuta casos; extração é idempotente para
os mesmos bytes. Hash local não comprova validade semântica/revisão externa.
