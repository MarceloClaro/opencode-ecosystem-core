# Template - Manifesto de Reprodutibilidade

## Cabecalho

```md
# Manifesto de Reprodutibilidade

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Nivel de reproducibilidade pretendido: Bronze / Silver / Gold]
```

## Escopo reproduzivel

```md
### O que pode ser reproduzido integralmente
- ...

### O que pode ser reproduzido parcialmente
- ...

### O que nao pode ser reproduzido e por que
- ...
```

## Dependencias do pacote

```md
| Componente | Artefato associado | Status | Restricao |
|---|---|---|---|
| Ambiente | ambiente_execucao.md | OK | - |
| Dados | catalogo_datasets.md | OK | Dados sensiveis com acesso controlado |
| Codigo | auditoria_codigo.md | PENDENTE | Falta validar modulo X |
| Experimentos | registro_experimentos.md | OK | - |
```

## Julgamento final

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Risco residual]
- ...
```
