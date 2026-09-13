# Foundation Agent — espelho 00 (fundação)

> Fundação do conjunto de espelhos (item 2B): padrão-base que todos os 20 pilotos
> seguem quando adaptados ao Core. Não é cópia de código — é o contrato de adaptação.

## Contrato de adaptação (espelho 00)

1. **SDD/TDD obrigatório**: todo piloto adaptado nasce de `specs/SPEC-935-R***.md`
   com critérios de aceitação (CA1…CAN) e testes RED → GREEN → refactor.
2. **Stdlib-first**: dependências externas só com justificativa auditada
   (`THIRD_PARTY_NOTICES.md`); modelos locais (Litert-LM/Colibri) por padrão.
3. **Hermeticidade**: sem rede, sem credenciais, sem código de terceiros nos testes.
4. **Anti-overclaim**: nenhum resultado "superhuman/verificado/Qualis A1" sem
   validação externa (MCI evaluator, CORRIGENDUM.md).
5. **Convergência**: antes de construir, rodar `reverse-scan` (R484) e consultar
   `PolymathicConvergence` (R486) — quem já resolveu parte disso?
6. **Registro**: ciclo no `evolution/cycles.json` + lição no MetaBus ao fechar.

## Formato de um espelho

Cada `examples/agents/NN-*.md` contém: origem (pasta 500-AI-Agents-Projects, MIT),
descrição, framework original, tags, padrão arquitetural, adaptação Core e lição
de design. O `_mirror-manifest.json` consolida os 20 pilotos para ferramentas.

## Fonte

[500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
(MIT, ashishpatel26) — catalogado no `landscape/manifest.json` (R482).