# Template - Relatorio ABNT

## Finalidade

Este relatorio documenta a conformidade do manuscrito com ABNT, a consistencia entre corpo, notas e referencias, e as pendencias normativas que precisam ser corrigidas antes da liberacao final.

## Cabecalho

```md
# Relatorio ABNT

[Projeto]
[Versao avaliada]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Status geral]
```

## Bloco 1 - Formato geral

```md
| Item | Regra esperada | Status | Evidencia/observacao | Correcao necessaria |
|---|---|---|---|---|
| Papel | A4 | OK | - | - |
| Margens | 3/3/2/2 cm | PENDENTE | margem direita divergente | Ajustar no DOCX final |
| Fonte | Times 12 ou Arial 12 | OK | - | - |
| Espacamento | 1,5 | OK | - | - |
| Recuo de paragrafo | 1,25 cm | OK | - | - |
| Hierarquia de titulos | Padronizada | PENDENTE | 2 subtitulos fora do padrao | Normalizar |
```

## Bloco 2 - Citacoes no corpo

```md
| ID | Local | Tipo | Regra ABNT | Status | Problema | Correcao |
|---|---|---|---|---|---|---|
| C01 | 2.2/P4 | Indireta | Autor + ano + pagina | OK | - | - |
| C02 | 3.1/P2 | Direta curta | Aspas + pagina | ERRO | pagina ausente | Inserir p. XX |
```

## Bloco 3 - Notas de rodape auditaveis

```md
| ID da nota | Local | Cadeia completa | Selecao | Autoridade | Funcao no paragrafo | Relevancia para a pesquisa | Limite de uso | Status |
|---|---|---|---|---|---|---|---|---|
| N01 | 2.2/P4 | OK | OK | OK | OK | OK | PENDENTE | PRONTO COM RESSALVAS |
```

## Bloco 4 - Referencias finais

```md
| ID | Referencia abreviada | Corpo do texto | Nota | Lista final | DOI/URL | Ordem alfabetica | Status |
|---|---|---|---|---|---|---|---|
| R01 | SILVA (2021) | OK | OK | OK | DOI valido | OK | OK |
| R02 | JONES (2020) | OK | OK | AUSENTE | URL ausente | OK | ERRO |
```

## Bloco 5 - Inconsistencias bidirecionais

### Citacoes no corpo sem referencia final
- ...

### Referencias finais sem uso no corpo
- ...

### Notas com funcao auditavel insuficiente
- ...

## Bloco 6 - Classificacao das falhas

```md
### Falhas leves
- ...

### Falhas moderadas
- ...

### Falhas altas
- ...

### Falhas fatais
- ...
```

## Regras de bloqueio

Bloquear a liberacao quando houver:

- citacao nuclear sem pagina;
- citacao no corpo sem referencia final;
- referencia final sem rastreabilidade minima;
- nota de rodape sem funcao auditavel em citacao central;
- divergencia nao resolvida entre corpo, nota e lista final.

## Parecer final

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Justificativa]
- ...

[Correcoes obrigatorias antes do proximo gate]
- ...
```
