# SPEC-935-R464: Integração Opcional do runai como Provisionador Local de Modelos

## Objetivo
Integrar o `runai` (CLI da canirun.ai) ao OpenCode Ecosystem Core como um
**provisionador opcional** de modelos locais via GGUF + `llama.cpp`, reduzindo
fricção de onboarding e eliminando a seleção manual de quantização por
hardware. O escopo desta spec é **provisionamento e diagnóstico**, não a
substituição dos providers HTTP já existentes (LiteRT-LM/Colibri).

## Contexto e Motivação
- O ecossistema já possui inferência local via **LiteRT-LM** e **Colibri**,
  porém ambos assumem stacks/modelos previamente preparados.
- O `runai` resolve um gargalo diferente: **descobrir o modelo**, escolher a
  **quantização compatível com o hardware**, baixar o artefato e abrir um chat
  local sem caça manual a arquivos GGUF.
- A página e o instalador estável documentam explicitamente:
  - `runai doctor`
  - `runai pull <model-id>`
  - `runai run <model-id>`
- Não há, nesta spec, alegação de API HTTP estável nem de integração direta com
  `ModelRouter.route_and_complete()` como provider de completude.

## Escopo
### Incluído
- Wrapper Python `integrations/runai.py` para:
  - detectar disponibilidade do binário;
  - executar `runai doctor`;
  - executar `runai pull <model-id>`;
  - executar `runai run <model-id>` em modo subprocesso interativo/best-effort;
  - listar um catálogo **curado/local** de aliases compatíveis com o ecossistema;
  - fornecer `provider_info()` / `health_check()` seguros.
- Integração com `doctor.py` como check opcional (`warn`, nunca `fail`).
- Exposição no pacote `integrations`/`evolution` quando aplicável.

### Excluído
- Inventar flags de CLI não documentadas.
- Afirmar que `runai` expõe endpoint OpenAI-compatible.
- Trocar LiteRT-LM/Colibri como caminho padrão de inferência.
- Persistir qualquer ciclo auditado novo sem solicitação explícita do usuário.

## Critérios de Aceitação (SDD/TDD)
- [C1] `RunAIProvisioner.is_available()` detecta o binário `runai` no PATH.
- [C2] `doctor()` expõe check `runai` como `pass` quando disponível e `warn`
      quando ausente, com hint de instalação seguro.
- [C3] `RunAIProvisioner.doctor()` executa `runai doctor` e retorna resultado
      estruturado (`ok`, `exit_code`, `stdout`, `stderr`).
- [C4] `RunAIProvisioner.pull(model_id)` executa `runai pull <model-id>` com
      quoting seguro, timeout e retorno estruturado.
- [C5] `RunAIProvisioner.run(model_id)` executa `runai run <model-id>` em
      subprocesso best-effort e retorna PID/estado, sem alegar protocolo HTTP.
- [C6] Há um catálogo mínimo curado de aliases (`qwen3.5-4b`, `gemma4-e2b-it`,
      `phi-4-mini-reasoning`) mapeado apenas para conveniência local.
- [C7] Testes com mocks cobrem: disponibilidade, ausência do binário,
      `doctor`, `pull`, `run`, timeout/erro e check no `doctor.py`.
- [C8] O `doctor` geral permanece verde (18+/19) e os testes novos passam.

## Arquitetura
```
integrations/runai.py          -> RunAIProvisioner (CLI bridge seguro)
marceloclaro/doctor.py         -> _check_runai()
tests/test_runai_integration.py -> TDD do bridge e do check do doctor
```

## Anti-overclaim
- `runai` será tratado como **provisionador/launcher CLI**, não como provider
  de completude programática até que documentação estável prove isso.
- A integração melhora **onboarding e provisionamento**; não prova por si só
  melhor qualidade de resposta do modelo.
- Modelos listados no catálogo do wrapper são aliases de conveniência, não um
  espelho completo do canirun.ai.

## Registro
- Autores: Marcelo Claro Laranjeira
- Data: 02 de setembro de 2026
- Ciclo: R464
