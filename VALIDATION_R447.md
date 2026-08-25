# Recibo local de auditoria — SPEC-935-R447

## Escopo

Este recibo consolida a auditoria **somente de leitura** que identificou os
bloqueadores depois remediados por `SPEC-935-R448` a `SPEC-935-R453`. Ele não é
release, certificação externa, auditoria independente nem reconstituição
forense completa do stdout histórico da primeira execução.

## Ambiente registrado

| Campo | Valor observado |
|---|---|
| Base Git (`git rev-parse HEAD`) | `067ba78156663daa8c3e9b98d2e75b68d8b85278` |
| Estado do checkout | árvore local em revisão, com remediações posteriores ainda não commitadas; a base Git não representa sozinha o snapshot integral da auditoria. |
| Runtime | Python 3.14.4 |
| Plataforma | Linux 6.18.33.2-microsoft-standard-WSL2 |
| Doctor | `python3 -m marceloclaro.cli doctor` observou 18 checks aprovados e 1 aviso para a CLI opcional `scihub-cli`. |

## Comandos executados

- `python3 -m marceloclaro.cli doctor` — executado localmente para registrar a
  saúde do ambiente e seus limites operacionais.
- `pytest --collect-only -q` — comando obrigatório da auditoria. O fechamento
  documental R454 não reconstitui o stdout original da coleta e, por isso, não
  o reapresenta como evidência primária do snapshot atual.
- `pytest -q` — a rodada histórica motivou as remediações R448–R453, mas a
  execução integral correspondente não foi preservada neste recibo como artefato
  bruto. As validações locais posteriores ficaram registradas em
  `VALIDATION_R448.md`, `VALIDATION_R452.md` e `VALIDATION_R453.md`.

O objetivo desta rodada era diagnosticar e priorizar riscos, não introduzir
correções durante a própria avaliação.

## Achados

| ID | Domínio | Severidade | Evidência rastreável | Recomendação |
|---|---|---|---|---|
| R447-A1 | SDD | alta | `sdd/spec_engine.py` promovia critérios Markdown por evidência global, sem vínculo explícito por critério; o fechamento estrutural foi formalizado depois em `SPEC-935-R454`. | Exigir associação criterion→nodeid e prova runtime local por critério. |
| R447-A2 | Segurança de instalação | alta | `installer/common/install_clis.sh` e wrappers privilegiados precisavam validar checkout, artefato e destino antes de efeitos privilegiados ou CLIs externas. | Antecipar preflights, restringir `PATH` e falhar fechado antes de `sudo`, WSL, Brew ou instaladores externos. |
| R447-A3 | Soundness formal | média | `integrations/deepmind/formal_verifier.py` aceitava caminhos formais e budgets que exigiam endurecimento adicional. | Rejeitar contramodelos, limitar domínio/recursos e fechar fallbacks positivos. |
| R447-A4 | Documentação | média | `README.md`, `MANUAL.md` e `ARCHITECTURE.md` precisavam distinguir métricas internas de validação externa e registrar limites operacionais. | Reconciliar documentação, remover ambiguidades e preservar anti-overclaim. |

## Revisões por domínio

### Arquitetura

- o ecossistema já expunha trilhas formais (`specs/`, `tests/`, `evolution/`),
  mas a ligação entre contrato Markdown e evidência executável ainda era ampla
  demais para sustentar uma contagem granular de critérios.

### Qualidade e testes

- a auditoria registrou a necessidade de coleta/execução explícitas e de gates
  herméticos; as validações posteriores ficaram concentradas nos recibos R448,
  R452 e R453, que documentam as execuções locais preservadas.

### Segurança

- instaladores privilegiados, procedência de artefatos e reutilização de PATH
  exigiam endurecimento fail-closed antes de qualquer uso operacional sensível.

### Documentação

- os documentos institucionais precisavam reduzir alegações implícitas de
  prontidão, certificação ou cobertura não observada diretamente.

## Recomendações priorizadas

1. **Alta prioridade / esforço moderado:** vincular critérios executáveis a
   testes reais e impedir promoção coletiva por uma única suíte verde.
2. **Alta prioridade / esforço moderado:** mover preflights de checkout,
   diretório e artefato para antes de qualquer privilégio, download ou CLI.
3. **Média prioridade / esforço moderado:** endurecer soundness formal com
   contramodelos, budgets globais e rejeição de sintaxe fora do fragmento.
4. **Média prioridade / esforço baixo:** reconciliar README, MANUAL,
   ARCHITECTURE e recibos locais com linguagem anti-overclaim.

Nenhuma recomendação acima constitui certificação externa, garantia absoluta,
E2E Windows elevado já executado ou prova de qualidade “super-humana”.

## Limites conhecidos

- este recibo não substitui os recibos técnicos posteriores nem reconstitui o
  stdout bruto da coleta/execução originais;
- a auditoria R447 foi deliberadamente somente leitura; as correções ocorreram
  nas specs sucessoras, não dentro deste ciclo;
- os resultados permanecem locais ao checkout e ao ambiente observados.
