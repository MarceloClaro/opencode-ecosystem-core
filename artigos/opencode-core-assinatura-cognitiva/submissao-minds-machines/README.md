# Pacote de submissão — *Minds and Machines* (Original Research)

**Manuscrito:** The house that helps to think: authored cognitive prostheses, agentic AI, and the limits of epistemic sovereignty

**Autor:** Marcelo Claro Laranjeira

**Status:** rascunho para revisão do autor; não submetido.

**Veículo:** *Minds and Machines* (Springer), artigo de pesquisa original, cerca de 8.000 palavras no texto principal.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`MANUSCRIPT_MINDS_MACHINES.md`](MANUSCRIPT_MINDS_MACHINES.md) / [`.docx`](MANUSCRIPT_MINDS_MACHINES.docx) / [`.pdf`](MANUSCRIPT_MINDS_MACHINES.pdf) | Manuscrito anonimizado em inglês, com uma tabela |
| [`TITLE_PAGE.md`](TITLE_PAGE.md) / [`.docx`](TITLE_PAGE.docx) | Título, autor, afiliação, declarações e preprint |
| [`COVER_LETTER.md`](COVER_LETTER.md) / [`.docx`](COVER_LETTER.docx) | Carta ao editor |
| [`SUPPLEMENTARY_MATERIAL.md`](SUPPLEMENTARY_MATERIAL.md) / [`.docx`](SUPPLEMENTARY_MATERIAL.docx) | Tabelas S1–S4, glossário e inventário do corpus |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Checklist de submissão e pendências |
| [`ADAPTATION_NOTES.md`](ADAPTATION_NOTES.md) | Notas de adaptação, riscos e alternativas de veículo |
| [`REVISAO_FILOSOFICA.md`](REVISAO_FILOSOFICA.md) / [`.pdf`](REVISAO_FILOSOFICA.pdf) | Revisão filosófica do inglês, seção por seção |
| [`LEITURA_PT.md`](LEITURA_PT.md) / [`.docx`](LEITURA_PT.docx) / [`.pdf`](LEITURA_PT.pdf) | Versão em português para leitura do autor |
| [`ARTIGO_PT.md`](ARTIGO_PT.md) / [`.docx`](ARTIGO_PT.docx) / [`.pdf`](ARTIGO_PT.pdf) | Artigo em português com autoria, e-mail, declarações e referências |
| [`build_docx.py`](build_docx.py) | Script local que reconstrói os `.docx` a partir dos `.md` |
| [`reference-custom.docx`](reference-custom.docx) | Referência de estilos usada pelo `pandoc` |

## Estado editorial

- **Texto principal:** cerca de 8.250 palavras, sem abstract, referências, tabelas e material suplementar.
- **Abstract:** cerca de 196 palavras.
- **Palavras-chave:** seis.
- **Revisão filosófica:** `REVISAO_FILOSOFICA.md`.
- **Versão de leitura em português:** `LEITURA_PT.md` / `.docx`, para revisão do autor; não é a versão de submissão.
- **Artigo em português:** `ARTIGO_PT.md` / `.docx` / `.pdf`, com autoria, e-mail, declarações, apêndices e referências com DOI.
- **Tabelas:** uma no texto; S1–S4 no material suplementar.
- **Anonimização:** o manuscrito e o suplemento não contêm nome, ORCID, URL, nome do sistema ou autocitações identificáveis. A identificação fica na title page.
- **Preprint:** a versão em português é declarada como preprint na title page e no manuscrito.
- **Uso de IA:** declarado no método, nas declarações e na title page.
- **Ética:** autoestudo; sem participantes além do autor; sem dados clínicos; consentimento declarado.

## Pendências antes de submeter

1. Revisão do autor: voz, estilo, precisão biográfica e nível de divulgação de saúde.
2. Reduzir as palavras-chave de oito para seis.
3. Confirmar a declaração de uso de IA.
4. Reconciliar as contagens de agentes (374 no `opencode.json`; 366 no bloco do `README.md`).
5. Definir acesso aberto (assinatura sem APC) ou Open Choice (com APC).
6. Preencher revisores sugeridos no sistema de submissão.
7. Confirmar que o manuscrito não está em avaliação em outro veículo.
8. Revisar o `.docx` final e conferir as propriedades do arquivo.

## Como reconstruir os `.docx`

```bash
cd artigos/opencode-core-assinatura-cognitiva/submissao-minds-machines
python3 build_docx.py
```

O script usa `pandoc` e `python-docx`. Ele não submete nada e não altera o argumento do artigo; apenas converte, formata tabelas, restaura marcadores de lista e define metadados.
