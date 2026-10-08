# Template - Ambiente de Execucao

## Cabecalho

```md
# Ambiente de Execucao

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Especificacao do ambiente

```md
| Item | Valor | Observacao |
|---|---|---|
| Sistema operacional | Ubuntu 22.04 | Ambiente principal |
| Linguagem principal | Python 3.11 | Execucao de pipeline |
| Linguagens secundarias | R 4.3 | Analise complementar |
| CPU/GPU | RTX 4090 / 24 GB | Treino multimodal |
| Seeds globais | 42, 123, 2026 | Robustez |
```

## Dependencias criticas

```md
| Dependencia | Versao | Fonte de verificacao | Impacto |
|---|---|---|---|
| scikit-learn | 1.5.x | docs oficiais | Modelos basicos |
| PyTorch | 2.x | docs oficiais | Redes neurais |
```

## Instrucoes minimas

```md
### Ordem de execucao
1. ...
2. ...
3. ...

### Outputs esperados
- ...
```
