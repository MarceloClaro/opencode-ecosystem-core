# Pacote editorial — artigo Maria do Socorro Araujo Martins Leite

**Tema:** inclusão escolar de estudantes com Transtorno do Espectro Autista (TEA) nos anos iniciais.
**Data:** 5 de novembro de 2026.

## O que há neste pacote

| Arquivo | Para que serve |
|---|---|
| `00_ORIGINAL.md` | Cópia imutável do arquivo recebido. Não editar. |
| `00_ORIGINAL.sha256` | Hash que comprova a integridade do original. |
| `01_ARTIGO_CORRIGIDO_ABNT.md` | Versão com intervenção mínima: mantém a estrutura e a voz da autora; corrige erros objetivos de texto, citação e referência. |
| `02_ARTIGO_QUALIS_A1.md` | Versão reestruturada como revisão narrativa: metodologia declarada, três eixos, síntese integrativa, limitações. |
| `01_ARTIGO_CORRIGIDO_ABNT.docx` / `.pdf` | Versão corrigida em ABNT (12 páginas). |
| `02_ARTIGO_QUALIS_A1.docx` / `.pdf` | Versão reestruturada em ABNT (16 páginas). |
| `RELATORIO_AUDITORIA.md` | Diagnóstico completo, decisões e pendências. **Ler primeiro.** |
| `RELATORIO_REFERENCIAS.md` | Verificação das 15 referências via Crossref, Google Acadêmico e páginas editoriais. |
| `RELATORIO_SCANNERS.md` | Registro e interpretação dos cinco scanners (`/diagnose`). |
| `DADOS_AUTORA.md` | Campos de afiliação, ORCID e nota de autoria a preencher. |
| `ADAPTACAO_PERIODICO.md` | Opções de título/palavras-chave e checklist para o periódico-alvo. |
| `CONFORMIDADE_METODOLOGIA_CIENTIFICA.md` | Comparação item a item com o manual de Metodologia Científica (PDF de 66 p.). |
| `SPEC-986.md` | Especificação e critérios de aceitação usados no trabalho. |
| `dados/` | Respostas brutas da API Crossref e saídas dos scanners. |
| `scripts/` | Scripts reprodutíveis de correção, verificação e compilação. |
| `templates/` | Cabeçalho LaTeX e referência DOCX usados na renderização. |

## Qual versão usar

- **Para submeter a um periódico ou programa:** comece por `02_ARTIGO_QUALIS_A1.*`. Ela tem metodologia, pergunta, objetivos, síntese e limitações. Ajuste o formato ao template do destino.
- **Para preservar o texto original com correções pontuais:** use `01_ARTIGO_CORRIGIDO_ABNT.*`.
- **Para entender o que mudou e o que precisa de decisão humana:** leia `RELATORIO_AUDITORIA.md` e `RELATORIO_REFERENCIAS.md`.

## Pendências antes de submeter

1. Confirmar **Santos e Lopes (2021)** e a **autoria de Ribeiro (2019)**, que o Google Acadêmico atribui a MCCA Menezes. Silva e Oliveira (2016) foi substituída por Cabral e Marin (2017).
2. Confirmar a substituição de **Mendonça e Oliveira (2017)** por **Bezerra e Pantoni (2022)**.
3. Confirmar a data de **Nunes, Azevedo e Schmidt (2013)** — a obra é de 2013, não de 2021.
4. Preencher **afiliação institucional e ORCID**.
5. Adaptar título, palavras-chave e formatação ao periódico-alvo.

## Aviso importante

O nome `02_ARTIGO_QUALIS_A1.md` indica **alvo de estrutura e rigor**, não classificação alcançada. Nenhuma etapa deste trabalho declara o artigo como "Qualis A1", "aprovado", "aceito" ou "verificado por pares". A qualidade editorial depende de avaliação humana e do processo do periódico.

## Como reproduzir

```bash
cd artigos/ARTIGO_MARIA_SOCORRO_TEA

# 1. Regerar a versão corrigida a partir do original
python3 scripts/gerar_corrigido.py

# 2. Inserir marcadores LaTeX de resumo/referências (idempotente)
python3 scripts/marcar_latex.py

# 3. Gerar o modelo DOCX ABNT
python3 scripts/gerar_reference_docx.py

# 4. Compilar DOCX e PDF
python3 scripts/build.py

# 5. Verificar todos os critérios
python3 scripts/verificar_artefatos.py --pdf --docx
```

A versão reestruturada (`02_ARTIGO_QUALIS_A1.md`) é um texto autoral produzido nesta auditoria; ela não é gerada por script. Se for editada, rode apenas as etapas 3–5.
