# Template - Relatorio de Consistencia Interna

## Finalidade

Este relatorio verifica se o manuscrito permanece coerente do inicio ao fim em problema, objetivos, hipoteses, termos, resultados e conclusoes.

## Cabecalho

```md
# Relatorio de Consistencia Interna

[Projeto]
[Versao avaliada]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Bloco 1 - Coerencia estrutural

```md
| Eixo | Pergunta de controle | Status | Evidencia | Problema detectado | Acao |
|---|---|---|---|---|---|
| Problema | A pergunta central permanece a mesma? | OK | Introducao x conclusao | - | - |
| Objetivos | Todos os objetivos reaparecem em resultados/discussao? | PENDENTE | O4 ausente na discussao | Cobertura parcial | Revisar cap. 5 |
| Hipoteses | Todas as hipoteses sao respondidas? | OK | Cap. 5 e 6 | - | - |
| Termos | O conceito X manteve o mesmo nome e sentido? | ERRO | Termo varia entre cap. 2 e 5 | Ambiguidade conceitual | Normalizar |
```

## Bloco 2 - Coerencia entre capitulos

```md
### Introducao -> Revisao
- ...

### Revisao -> Metodologia
- ...

### Metodologia -> Resultados
- ...

### Resultados -> Discussao
- ...

### Discussao -> Conclusao
- ...
```

## Bloco 3 - Inconsistencias criticas

```md
### Contradicoes
- ...

### Mudancas de termo com impacto conceitual
- ...

### Resultados sem resposta correspondente
- ...

### Conclusoes sem base suficiente
- ...
```

## Bloco 4 - Julgamento final

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Razao principal]
- ...

[Correcoes obrigatorias]
- ...
```
