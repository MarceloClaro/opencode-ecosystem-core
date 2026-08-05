---
spec_id: SPEC-935-R403
title: Molambudos — dossiê de estudo acadêmico em três línguas, com estado de validação explícito
component: projetos/molambudos/Molambudos_VictoriaRegia/dossie
status: verified
test_file: tests/test_r399_molambudos_selo_e_capa.py
---

# SPEC-935-R403 — Dossiê de Estudo

**Data:** 2026-08-05
**Motivação:** *"agora faça uma ficha dossiê sobre o projeto Molambudos em 3
línguas, apresentando o projeto literário, suas influências literária e
narrativa, técnicas, objetivos, uma análise completa e minuciosa, as teorias
envolvidas e intencionais do autor, suas limitações e impactos — um dossiê de
estudo sobre a obra a nível acadêmico rigoroso"*.

## 1. Forma e posição do artefato

Três documentos autônomos em `dossie/`: `dossie_pt.tex`, `dossie_en.tex`,
`dossie_zh.tex` (6, 6 e 7 páginas A4). PT e EN compilam com `pdflatex`; ZH com
`xelatex` + `xeCJK` + Noto Serif CJK SC.

**Aparato crítico separado, não parte da ficção.** Incluí-lo no miolo
quebraria o quadro diegético que a obra constrói: o livro se apresenta como
arquivo pericial, e um estudo crítico dentro dele destruiria a moldura. Um
pesquisador lê o dossiê em uma língua; por isso três documentos, não um
trilíngue intercalado.

## 2. Conteúdo

| Seção | O que traz |
|---|---|
| Ficha técnica | dados de identificação e extensão medida por edição |
| Projeto literário | os três movimentos declarados; a cadeia de transmissão |
| Arquitetura formal | famílias, partes, atos, rede de rotas |
| Linhagem | afinidades formais verificáveis |
| Técnicas narrativas | indução, inversão da ausência, instrumento clínico |
| Fundamentos teóricos | quadros aplicáveis, com o que na obra os convoca |
| Base histórica e ética | análise da *Nota Histórica* e do aviso ao leitor |
| Análise crítica | forças e pontos discutíveis |
| Limitações verificadas | quatro, com números |
| Estado de validação | o que foi e o que **não** foi validado |
| Agenda de pesquisa | cinco questões abertas |

## 3. Números medidos, não estimados

Todos os dados foram extraídos dos arquivos-fonte em 2026-08-05:

| Métrica | Valor |
|---|---|
| Fragmentos | 84 (MEM 27, DOC 27, LUC 17, CONT 13) |
| Palavras PT / EN | 43.730 / 44.978 |
| Caracteres ZH | 70.750 |
| Extensão: menor / maior | 130 (MEM-26) / 2.310 (DOC-03) |
| Fragmentos com 2ª pessoa sustentada | 27 de 84 |
| Partes | Sertão 9, Colônia 16, Diário 25, Lúcia 20, Contaminação 14+Epílogo |
| Atos | Trauma 9, Institucionalização 41, Ciclo 35 |
| Paginação (digital / impressão) | PT 415/435, EN 411/427, ZH 387/397, tri 1.061/1.115 |

O dossiê registra que contagem em palavras não é comparável entre chinês e
línguas ocidentais, e usa caracteres para o chinês.

## 4. Disciplina epistêmica aplicada

Três decisões que distinguem o dossiê de material promocional:

### 4.1 Linhagem não é genealogia de leitura

A seção de influências abre com ressalva explícita: identifica **afinidades
formais verificáveis no texto** e *"não afirma que o autor leu as obras
citadas nem que delas derivou conscientemente"*. Compara com *Drácula*,
*House of Leaves*, *O Jogo da Amarelinha*, Calvino, *Vidas Secas*, Goffman e
Arbex — como parentesco de procedimento, que é o que a crítica pode comparar.

### 4.2 Teoria mobilizada não é intenção autoral

O pedido mencionava *"teorias envolvidas e intencionais do autor"*. A obra não
declara filiação teórica. O dossiê apresenta os quadros como **aplicáveis por
um estudo crítico**, indicando o que na obra os convoca, sem atribuir intenção
ao autor. A exceção é registrada como tal: a *Nota Histórica* declara a chave
de trauma intergeracional explicitamente, e o dossiê cita a passagem.

### 4.3 Impacto não foi inventado

O pedido mencionava *"impactos"*. A obra não foi publicada. O dossiê declara
recepção crítica **inexistente** e impacto **não mensurável**, em vez de
estimar. A tabela de validação separa:

| Verificado | Não realizado |
|---|---|
| integridade de compilação das 5 edições | revisão por pares acadêmica |
| paridade de rotas fonte×impresso (648/648) | revisão editorial profissional externa |
| convergência e ausência de aprisionamento | verificação historiográfica por especialista |
| integridade dos fragmentos (SHA-256) | revisão nativa das traduções EN e ZH |

Com ressalva final: *"as quatro primeiras linhas são verificações técnicas
internas: dizem que o objeto está bem construído, não que é bom"*, e pedido
para que qualquer alegação de mérito derivada do dossiê seja tratada como
infundada até haver validação externa.

## 5. Análise crítica com os dois lados

O dossiê registra quatro forças e três pontos discutíveis. O mais sério:

> A metáfora sobrenatural pode aliviar o horror histórico. Ao dar ao
> sofrimento uma causa fantástica, a obra corre o risco de deslocar a
> responsabilidade política para uma entidade. A *Nota Histórica* antecipa a
> objeção e a responde; se a resposta basta é questão crítica aberta.

Os outros dois: as notas do editor interrompem a indução no pico; a densidade
de segunda pessoa em 27 fragmentos pode saturar na leitura linear.

## 6. Limitações registradas

As quatro limitações verificadas ao longo dos ciclos R397–R402 estão no
dossiê com números, incluindo a mais séria — **as três edições não são o mesmo
livro**, com dez fragmentos divergentes e os casos extremos nomeados.

## 7. Efeito colateral: dois testes que mediam o proxy

Ampliar os mapas de `0.85` para `0.90\textheight` (R402) quebrou
`test_r239::test_main_tex_margin_params` e
`test_r240::test_main_tex_graph_framing`, que fixavam a **fração exata**. Nada
de real havia quebrado — o preflight seguia com zero violações.

Ambos foram reescritos para exigir a **propriedade**: escala relativa à página
(nunca absoluta) e restrição em **ambas** as dimensões da inclusão. A segunda
condição não é preciosismo: com apenas `height=`, `keepaspectratio` deixa a
largura crescer livremente, que foi exatamente como o Mapa 2 estourou a página
no R401.

## 8. Critérios de aceitação

1. Três dossiês autônomos, um por língua, compilando sem erro. ✔
2. Edição ZH renderizando CJK corretamente. ✔
3. Todos os números medidos sobre os arquivos-fonte, não estimados. ✔
4. Linhagem declarada como afinidade formal, não como genealogia de leitura. ✔
5. Teoria apresentada como quadro aplicável, não como intenção autoral. ✔
6. Impacto e recepção declarados inexistentes/não mensuráveis, não estimados. ✔
7. Análise crítica registrando pontos discutíveis, não só forças. ✔
8. Suíte completa verde: 2730 aprovados, 0 falhas. ✔
