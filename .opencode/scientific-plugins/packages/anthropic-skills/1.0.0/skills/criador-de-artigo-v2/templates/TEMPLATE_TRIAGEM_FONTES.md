# Template - Triagem de Fontes

## Finalidade

Este arquivo registra a decisao de incluir, excluir, priorizar ou manter em observacao cada fonte candidata.

## Cabecalho

```md
# Triagem de Fontes

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Tabela principal

```md
| ID | Referencia curta | Tipo | Texto integral | Papel potencial | Decisao | Motivo da decisao | Risco | Observacao |
|---|---|---|---|---|---|---|---|---|
| F01 | SILVA (2023) | Artigo empirico | Sim | Suporte empirico | Incluida | Alta aderencia ao problema e dados robustos | Baixo | Usar em 2.3 e 5.1 |
| F02 | JONES (2020) | Revisao narrativa | Sim | Contexto | Excluida | Muito generica para o recorte do estudo | Medio | - |
| F03 | BRASIL (2018) | Norma oficial | Sim | Referencia normativa | Prioritaria | Fonte primaria obrigatoria | Baixo | Usar no cap. 3 |
```

## Categorias de decisao permitidas

- `Incluida`
- `Prioritaria`
- `Excluida`
- `Em observacao`
- `Substituida`

## Bloco de justificativas especiais

```md
### Fontes incluidas apesar de limite metodologico
- ...

### Fontes excluidas apesar de prestigio
- ...

### Fontes que exigem leitura complementar
- ...
```

## Checklist de fechamento

```md
□ Toda fonte prioritaria possui texto integral?
□ Toda exclusao relevante foi justificada?
□ Toda fonte primaria obrigatoria foi preservada?
□ As fontes criticas e divergentes estao representadas?
□ Ha equilibrio entre prestigio e aderencia?
```
