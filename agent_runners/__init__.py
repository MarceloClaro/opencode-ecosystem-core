"""agent_runners — executores externos opcionais da fábrica de pesquisa (SPEC-935-R471).

Política R471:
- Invocação externa apenas; nunca `shell=True`; argumentos em lista.
- Nenhuma credencial, rede ou secreto neste pacote.
- Todo despacho gera recibo de auditoria (`orchestrator=marceloclaro`).
- Fail-closed: allowlist/modos/task validados antes de qualquer execução.
"""