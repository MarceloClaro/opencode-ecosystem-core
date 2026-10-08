# Template - Matriz de Evidencias

## Finalidade

Este arquivo mapeia cada afirmacao relevante do manuscrito a uma evidencia verificavel, localizada e funcional. Ele deve ser preenchido antes da redacao final de cada secao substantiva.

## Regras de preenchimento

- uma linha por afirmacao verificavel;
- nao agrupar afirmacoes distintas na mesma linha;
- toda afirmacao central deve ter fonte principal;
- toda afirmacao controversa deve ter, quando possivel, fonte de contraste;
- toda localizacao deve ser precisa;
- todo limite de uso deve ser explicitado.

## Cabecalho do arquivo

```md
# Matriz de Evidencias

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Gate]
[Secao(s) coberta(s)]
```

## Tabela principal

```md
| ID da afirmacao | Secao/paragrafo | Tipo de afirmacao | Texto resumido da afirmacao | Fonte principal | Fonte de contraste | Localizacao exata | Funcao da citacao | O que a fonte sustenta | O que a fonte nao sustenta | Risco | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | 2.1/P3 | Definicao | X e definido como... | AUTOR (2019) | AUTOR (2021) | p. 14-16 | Delimitar conceito | Definicao teorica | Nao valida uso empirico direto | Medio | PRONTO |
| A02 | 3.2/P4 | Metodo | O instrumento Y apresenta consistencia adequada | AUTOR (2022) | - | p. 55; Tabela 2 | Justificar instrumento | Alfa e contexto de validacao | Nao generaliza para toda populacao | Medio | PRONTO COM RESSALVAS |
```

## Tipos de afirmacao permitidos

- `Definicao`
- `Dado contextual`
- `Hipotese`
- `Lacuna`
- `Metodo`
- `Resultado`
- `Contraste`
- `Limitacao`
- `Interpretacao`
- `Implicacao`

## Checkpoint por secao

```md
## Checkpoint - [Secao]

- Quantidade de afirmacoes mapeadas:
- Quantidade de afirmacoes sem contraste quando necessario:
- Quantidade de afirmacoes com risco alto:
- Quantidade de afirmacoes bloqueadas:

### Pendencias criticas
- ...

### Observacoes do revisor cruzado
- ...
```

## Regras de bloqueio

Marcar `Status = BLOQUEADO` quando:

- a fonte principal nao tiver texto integral lido;
- a localizacao for imprecisa;
- a afirmacao exceder o que a fonte sustenta;
- o tipo de afirmacao exigir contraste e nao houver contraponto minimamente plausivel;
- a mesma fonte estiver sendo reutilizada indevidamente para conclusoes diferentes sem nova localizacao.

## Checklist de fechamento

```md
□ Toda afirmacao substantiva da secao aparece na matriz?
□ Toda afirmacao possui fonte principal localizada?
□ Toda afirmacao controversa possui fonte de contraste ou justificativa de ausencia?
□ Todo limite de uso foi explicitado?
□ O revisor cruzado marcou os riscos altos?
□ O gerente pode entender a cadeia de prova sem depender da memoria do agente?
```
