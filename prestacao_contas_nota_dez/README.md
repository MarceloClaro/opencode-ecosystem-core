# Auditor e Executor de Prestação de Contas — Prêmio Escola Nota Dez

Plugin do OpenCode Ecosystem Core para auditar diligências da SEDUC/CE
(Prêmio Escola Nota Dez / FECOP) e gerar **minutas** de resposta item a item.

## O que faz

| Etapa | Entrada | Saída |
|---|---|---|
| **OCR** | PDF escaneado (Epson Scan 2) | Texto por página (tesseract `por`, cache em `/tmp/opencode/pcn_ocr_cache`) |
| **Auditoria** | Texto da diligência | Estrutura: cabeçalho (processo, unidade, município, CNPJ, NE, valor, ano), blocos por licitação e **demandas** com página referida; checklist + score interno |
| **Executor** | JSON da auditoria | Minuta de ofício-resposta em Markdown + planilha CSV de controle |

## Uso

```bash
# 1) Auditar um PDF de diligência
python3 -m prestacao_contas_nota_dez.src.cli audit \
    "/mnt/c/Users/marce/OneDrive/Documentos/img20260924_14524484.pdf" \
    --out exemplos/

# 2) Gerar minuta + controle a partir da auditoria
python3 -m prestacao_contas_nota_dez.src.cli execute exemplos/audit_img20260924_14524484.pdf.json

# 3) Conciliação aritmética de escopo financeiro (ferramenta auxiliar)
python3 -m prestacao_contas_nota_dez.src.conciliar --help
```

## Referências integradas

Em `references/` (proveniência: plugin `contas-escolares-airam-veras` do Codex,
integrado por compatibilidade e auditado):

- `regras-comuns.md` / `base-documental.md` / `fontes-oficiais.md` — enquadramento
  normativo e conferência documental.
- `manual-2019-ocr.md` — OCR auxiliar do Manual de Orientações 2019 (34 páginas);
  **imagem prevalece sobre o OCR**; não tratar como manual integral.
- `checklist-base.csv` — lista adaptável de verificação (não é declaração de
  obrigações universais).
- `modelo-resposta.md` — estrutura editorial de resposta administrativa (não é
  formulário oficial da SEDUC).
- `proveniencia.json` — cadeia de procedência das referências.
- `src/conciliar.py` — conferência aritmética de escopo financeiro (repasse,
  despesas, tarifas, saldos); não valida conformidade legal.

## Estados (modelo contas-escolares-airam-veras)

Cada item do checklist carrega duas dimensões independentes:

- **Estado documental**: `não examinado` (inicial) → `conferido` | `incompleto` |
  `não localizado no material recebido` | `ilegível` | `não se aplica, com justificativa`.
- **Estado de tramitação**: `identificado` (inicial) → `em obtenção` |
  `minuta preparada` | `correção evidenciada` | `encaminhado` | `aceite comprovado pelo órgão`.

Não equiparar os dois eixos: "minuta preparada" ≠ "correção evidenciada" ≠ "aceite pelo órgão".

## Anti-overclaim (regra R110)

- O **score de cobertura** é **interno**: mede quantos apontamentos foram
  parseados e têm providência+documento registrados. **Não** é aprovação do
  órgão concedente nem certificação.
- Os artefatos gerados são **minutas**: o preenchimento final (providência
  adotada, documento comprobatório, assinaturas, carimbos) é **responsabilidade
  humana**, conferido contra a documentação original e a legislação vigente.
- Prestação de contas de recursos públicos é domínio sensível: o plugin é
  **apoio computacional** para organizar a resposta, não parecer jurídico.

## Testes

```bash
python3 -m pytest prestacao_contas_nota_dez/tests/test_r597_prestacao_contas.py -q
```

## Estrutura

```
prestacao_contas_nota_dez/
├── plugin.json          # metadados do plugin (agent-plugins)
├── README.md
├── src/
│   ├── ocr.py           # PDF → texto (pdftoppm + tesseract, cache)
│   ├── diligencia.py    # parse: cabeçalho, blocos, demandas
│   ├── auditor.py       # checklist + score interno + estados documental/tramitação
│   ├── executor.py      # minuta administrativa + CSV de controle
│   ├── verificacao.py   # checklist base C01–C40 (references/checklist-base.csv)
│   ├── relatorio.py     # relatório de conferência anti-overclaim
│   ├── conciliar.py     # conciliação aritmética (apoiada)
│   └── cli.py           # CLI audit / execute
├── references/          # manual-2019-ocr, checklist-base, modelo-resposta etc.
├── tests/test_r597_*.py # TDD (R597: 8 testes; R597b melhorias: 8 testes)
└── exemplos/            # saídas geradas (com .gitignore para PDFs pesados)
```

## Requisitos

- `poppler-utils` (pdftoppm/pdfinfo) e `tesseract-ocr` com idioma `por`.
- Python 3.10+.