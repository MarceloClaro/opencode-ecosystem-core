# Template - Pipeline de Visao Computacional e Multimodalidade

## Cabecalho

```md
# Pipeline de Visao Computacional e Multimodalidade

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Tarefa]
```

## Bloco 1 - Dados e anotacoes

```md
| ID | Dataset | Modalidade | Unidade de anotacao | Split | Risco de leakage | Observacao |
|---|---|---|---|---|---|---|
| V01 | Base X | Imagem | imagem inteira | train/val/test | Baixo | split por paciente |
```

## Bloco 2 - Preprocessamento e augmentations

```md
| Etapa | Objetivo | Parametros | Aplicada em | Risco |
|---|---|---|---|---|
| Resize | padronizar entrada | 224x224 | train/val/test | Baixo |
| MixUp | regularizacao | alpha=0.2 | train | Medio |
```

## Bloco 3 - Arquitetura e treino

```md
| Componente | Escolha | Justificativa | Dependencia oficial |
|---|---|---|---|
| Backbone | ViT-B/16 | baseline forte multimodal | docs oficiais |
| Loss | focal loss | desbalanceamento | docs oficiais |
```

## Bloco 4 - Avaliacao e erro

```md
### Metricas principais
- ...

### Analise por classe/slice
- ...

### Shift de dominio
- ...

### Falhas tipicas
- ...
```

## Bloco 5 - Interpretabilidade e limites

```md
### Ferramentas interpretativas
- ...

### Limites do uso interpretativo
- ...

### Condicoes de bloqueio
- ...
```
