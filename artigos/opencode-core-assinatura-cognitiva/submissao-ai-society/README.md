# Pacote de submissão — *AI & Society* (Open Forum)

**Manuscrito:** The house that helps to think: authored cognitive prostheses, agentic AI, and the care of memory

**Autor:** Marcelo Claro Laranjeira

**Status:** rascunho para revisão do autor; não submetido.

**Veículo:** *AI & Society: Knowledge, Culture and Communication* (Springer), tipo Open Forum, cerca de 8.000 palavras.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`MANUSCRIPT_AI_SOCIETY.md`](MANUSCRIPT_AI_SOCIETY.md) / [`.docx`](MANUSCRIPT_AI_SOCIETY.docx) | Manuscrito anonimizado em inglês, com quatro tabelas |
| [`TITLE_PAGE.md`](TITLE_PAGE.md) / [`.docx`](TITLE_PAGE.docx) | Título, autor, afiliação, declarações e preprint |
| [`COVER_LETTER.md`](COVER_LETTER.md) / [`.docx`](COVER_LETTER.docx) | Carta ao editor |
| [`SUPPLEMENTARY_MATERIAL.md`](SUPPLEMENTARY_MATERIAL.md) / [`.docx`](SUPPLEMENTARY_MATERIAL.docx) | Tabelas S1–S2, glossário e inventário do corpus |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Checklist de submissão e pendências |
| [`ADAPTATION_NOTES.md`](ADAPTATION_NOTES.md) | Notas de adaptação, riscos e alternativas de veículo |
| [`build_docx.py`](build_docx.py) | Script local que reconstrói os `.docx` a partir dos `.md` |
| [`reference-custom.docx`](reference-custom.docx) | Referência de estilos usada pelo `pandoc` |

## Estado editorial

- **Texto principal:** cerca de 7.500 palavras, sem abstract, referências, tabelas e material suplementar.
- **Abstract:** cerca de 200 palavras.
- **Palavras-chave:** seis.
- **Tabelas:** três no texto; S1–S3 e o inventário do corpus no material suplementar.
- **Anonimização:** o manuscrito e o suplemento não contêm nome, ORCID, URL, nome do sistema ou autocitações identificáveis. A identificação fica na title page.
- **Preprint:** a versão em português é declarada como preprint na title page e no manuscrito.
- **Uso de IA:** declarado no método, nas declarações e na title page.
- **Ética:** autoestudo; sem participantes além do autor; sem dados clínicos; consentimento declarado.

## Pendências antes de submeter

1. Revisão do autor: voz, estilo, precisão biográfica e nível de divulgação de saúde.
2. Confirmação da declaração de uso de IA, à luz da política da *AI & Society*.
3. Reconciliar as contagens de agentes (374 no `opencode.json`; 366 no bloco do `README.md`).
4. Definir acesso aberto (assinatura sem APC) ou Open Choice (com APC).
5. Preencher revisores sugeridos no sistema de submissão.
6. Confirmar que o manuscrito não está em avaliação em outro veículo.
7. Revisar o `.docx` final e conferir as propriedades do arquivo.

## Como reconstruir os `.docx`

```bash
cd artigos/opencode-core-assinatura-cognitiva/submissao-ai-society
python3 build_docx.py
```

O script usa `pandoc` e `python-docx`. Ele não submete nada e não altera o argumento do artigo; apenas converte, formata tabelas, restaura marcadores de lista e define metadados.
