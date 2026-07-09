# Evoluções — Índice

## Sessões Registradas

| Arquivo | Data | Issues | Correções | Resultado |
|---------|------|--------|-----------|-----------|
| `insight_20260528.md` | 2026-05-28 | 4 → 0 | 4 (3 text shortening, 1 raggedright) | 16/16 GREEN |
| `insight_20260528_round10.md` | 2026-05-28 | — | Menu reescrito: estático → adaptativo | DiscoveryEngine + plugin system |

## Sobre

Este diretório é gerado pelo estágio **LEARN** do pipeline AutoEvolve
(`orchestration/refinement_loop.py`). Cada arquivo `insight_<data>.md`
contém:

- Tendências de qualidade entre sessões
- Padrões de correção mais frequentes
- Métricas finais do documento
- Recomendações para a próxima sessão

Para executar o pipeline e gerar novos insights:

```powershell
python orchestration\refinement_loop.py
```
