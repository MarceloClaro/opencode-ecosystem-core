# Template - Log de Busca

## Finalidade

Este arquivo registra, de forma auditavel, como a busca bibliografica foi planejada, executada e refinada. Ele deve permitir que um terceiro reconstrua:

- onde a busca foi feita;
- com quais strings;
- sob quais filtros;
- com quais resultados;
- e por que certas fontes entraram ou sairam.

## Cabecalho

```md
# Log de Busca

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Janela temporal]
[Area/subarea]
```

## Bloco 1 - Estrategia geral

```md
## Estrategia geral

[Pergunta central]
- ...

[Subperguntas da busca]
- ...

[Bases obrigatorias]
- ...

[Descritores em portugues]
- ...

[Descritores em ingles]
- ...

[Criterios de inclusao]
- ...

[Criterios de exclusao]
- ...
```

## Bloco 2 - Execucao por base

```md
| ID | Base | String literal | Filtros | Data | Resultados brutos | Abertos | Lidos integralmente | Selecionados | Status | Observacao |
|---|---|---|---|---|---|---|---|---|---|---|
| B01 | Scopus | TITLE-ABS-KEY("...") | 2021-2026; article | 2026-03-17 | 124 | 18 | 11 | 4 | OK | Busca central para subquestao 1 |
```

## Bloco 3 - Refinamentos

```md
| ID do refinamento | Busca relacionada | Motivo do refinamento | Acao tomada | Impacto no pool de fontes |
|---|---|---|---|---|
| R01 | B01 | Muitos falsos positivos | Adicao de NOT e filtro por area | Reducao de 124 para 42 resultados relevantes |
```

## Bloco 4 - Saturacao e cobertura

```md
### Saturacao
- Houve saturacao?
- Em quais temas?
- O que ainda ficou fraco?

### Cobertura
- Fontes fundacionais: [ok/pendente]
- Fontes recentes: [ok/pendente]
- Fontes criticas: [ok/pendente]
- Fontes metodologicas: [ok/pendente]
- Fontes contextuais/brasileiras: [ok/pendente]
```

## Bloco 5 - Alertas

```md
### Riscos da busca
- ...

### Lacunas remanescentes
- ...

### Recomendacao ao gerente
- PRONTO
- PRONTO COM RESSALVAS
- BLOQUEADO
```
