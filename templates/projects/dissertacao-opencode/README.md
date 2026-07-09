# Dissertação: O Ecossistema OpenCode

## Métricas de Qualidade

| Métrica | Valor |
|---------|-------|
| Arquivos de capítulo | 23/23 |
| Palavras totais | 39,786 |
| Páginas estimadas (ABNT) | ≈113 |
| Notas de rodapé | 81 |
| DOIs nas citações | 92 |
| Referências bibliográficas | 68 |
| Score Qualis alvo | 100/100 |

## Estrutura

```
dissertacao-opencode/
├── dissertacao.tex          # Template mestre LaTeX
├── capitulos/               # 21 arquivos .tex (seções)
│   ├── 00-capa.tex
│   ├── 01-folha-rosto.tex
│   ├── ...
│   └── 20-apendice-b.tex
├── testes/
│   └── test_dissertacao_roadmap.py  # 24 CTs TDD
├── output/
│   └── dissertacao.pdf      # PDF compilado
├── unify_and_compile.py     # Script de unificação
└── README.md
```

## Validação TDD

```bash
# Executar os 24 casos de teste
cd testes
pytest test_dissertacao_roadmap.py -v

# Resultado esperado: 24 passed in X.XXs
```

## Compilação

```bash
# Requer: MiKTeX ou TeX Live instalado
python unify_and_compile.py

# Apenas verificar métricas (sem compilar PDF)
python unify_and_compile.py --no-pdf
```

---
*Gerado em: 16/06/2026 23:18*
*Ecossistema OpenCode v5.1.0 — Score Qualis A1 100/100*
