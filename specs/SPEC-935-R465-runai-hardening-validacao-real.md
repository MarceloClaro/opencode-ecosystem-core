# SPEC-935-R465: Hardening e Validação Real da Integração runai

## Objetivo
Levar a integração opcional do `runai` (R464) do nível de *bridge mockável*
para o nível de **validação real de ambiente**, com smoke test não destrutivo,
surface CLI mais completa e utilidade prática verificável no ecossistema.

## Motivação
- R464 provou o contrato de integração via testes herméticos.
- Ainda faltava validar o comportamento real do binário no ambiente e ampliar o
  wrapper com operações de inspeção segura.
- O usuário pediu que o `runai` ficasse **funcional e testado**; isso exige:
  1. validação do binário real quando instalado;
  2. wrapper mais completo (`version`, `help`, `catalog aliases`);
  3. smoke tests não destrutivos;
  4. inventário honesto no ecossistema, sem fingir provider HTTP.

## Escopo
### Incluído
- Revisar/usar o instalador estável já inspecionado (`@canirun/runai`).
- Expandir o wrapper com `version()`, `help()`, aliases e catalog metadata.
- Adicionar smoke test real opcional baseado em ambiente (`RUNAI_REAL=1`).
- Integrar `runai` ao inventário do `ModelRouter.status()` como **provisionador**.
- Manter o `doctor` como warn-only quando ausente.

### Excluído
- Rotear `route_and_complete()` para `runai` como se fosse provider OpenAI.
- Baixar modelo pesado por padrão durante testes automáticos.
- Declarar benchmark superioridade de qualidade de resposta.

## Critérios de Aceitação
- [D1] O wrapper expõe `help()` e `version()` com retorno estruturado.
- [D2] Há aliases canônicos do ecossistema → IDs `runai` quando aplicável.
- [D3] `ModelRouter.status()` passa a inventariar `runai` como provisionador
      opcional, sem alterar a rota de completude.
- [D4] Smoke test real opcional valida `runai doctor` quando o binário existir.
- [D5] Testes herméticos cobrem as novas operações e a integração ao router.
- [D6] `doctor` segue sem falhas estruturais após a integração.

## Anti-overclaim
- “Funcional” aqui significa: **bridge operacional, comandos validados e smoke
  test real opcional**. Não significa que todo modelo do canirun.ai foi
  benchmarkado ou que há inferência HTTP integrada ao router.

## Registro
- Autores: Marcelo Claro Laranjeira
- Data: 02 de setembro de 2026
- Ciclo: R465
