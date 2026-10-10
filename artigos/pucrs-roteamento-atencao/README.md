# Dissertação — roteamento inspirado em atenção

**Roteamento inspirado em atenção: formalização do núcleo matemático em Lean 4 e avaliação empírica interna**

Autor: Marcelo Claro Laranjeira. Revisão editorial e normativa: 10 de outubro de 2026.

Esta pasta disponibiliza a dissertação revista, com 97 páginas, e sua fonte LaTeX consolidada. A composição utiliza a base ABNT NBR 14724:2024, versão corrigida 2025; NBR 10520:2023; NBR 6023:2025; NBR 6028:2021; NBR 6024:2012 e NBR 6027:2012, conforme as fontes registradas no relatório.

## Documentos

- [Site interativo da pesquisa](https://marceloclaro.github.io/opencode-ecosystem-core/) e [código do site MIRA](site/).
- [Dissertação em PDF](output/pdf/dissertacao-abnt.pdf).
- [Fonte LaTeX consolidada](dissertacao-abnt.tex).
- [Relatório da revisão e pendências](revisao-abnt/relatorio_revisao_abnt.md).
- [Auditoria das 51 referências](revisao-abnt/auditoria_referencias.md) e [metadados consultados](revisao-abnt/auditoria_referencias.json).
- [Conferência do PDF](revisao-abnt/conferencia_pdf.json).
- [Manifesto dos arquivos publicados](manifesto_publicacao.json), com hashes SHA-256.

## Estado do trabalho

A versão é uma minuta revista para preparação da submissão. Permanecem pendentes o nome oficial do programa, área de concentração, linha de pesquisa, denominação do título, identificação do orientador, ficha catalográfica e dados da defesa/banca. A conferência com o modelo específico da PUCRS depende de acesso institucional. A disponibilização no GitHub não equivale à submissão à universidade, aprovação de banca ou validação externa.

Os resultados empíricos são sintéticos e internos. A formalização se refere ao modelo matemático sobre os reais; não certifica integralmente a execução em ponto flutuante. Os intervalos preservados são exploratórios e não consideram o agrupamento das decisões por piscina. A demonstração sobre cartões do catálogo calcula rankings e não executa os agentes. Comparação externa, análise estatística com agrupamento e reprodução independente permanecem pendentes.

Esta publicação disponibiliza os artefatos da revisão. Não registra uma reexecução dos experimentos nem um novo resultado científico.

## Compilação

A fonte consolidada incorpora os módulos, códigos, resultados e transcrições utilizados na versão revista. Não requer os caminhos locais de inclusão do arquivo modular original. Requer uma distribuição LaTeX com XeLaTeX, a classe `abntex2` e os pacotes indicados no preâmbulo, além das fontes TeX Gyre Termes e DejaVu Sans Mono.

```bash
cd artigos/pucrs-roteamento-atencao
latexmk -xelatex -interaction=nonstopmode -halt-on-error dissertacao-abnt.tex
```

O PDF de referência está em `output/pdf/dissertacao-abnt.pdf`. Esta compilação local gera `dissertacao-abnt.pdf` no diretório corrente; a igualdade byte a byte também depende do ambiente e dos metadados de geração.

## Proveniência

Os manifestos de entrega e de fontes em `revisao-abnt/` documentam o espaço de trabalho da revisão. Incluem caminhos e arquivos mantidos apenas localmente, como a fonte modular e a cópia anterior; não representam a lista de arquivos deste pacote público. Para conferir o pacote GitHub, utilize `manifesto_publicacao.json`.

As cópias anteriores, imagens de conferência, arquivos temporários de compilação e scripts auxiliares de revisão foram mantidos localmente. A fonte consolidada preserva as listagens incorporadas à dissertação.
