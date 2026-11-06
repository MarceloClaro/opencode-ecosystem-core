# TCC — Maria do Socorro Araujo Martins Leite

**Título:** A inclusão escolar de estudantes com Transtorno do Espectro Autista nos anos iniciais: políticas, práticas pedagógicas, formação docente e evidências do Censo Escolar (2021–2024)
**Formato:** TCC (monografia), conforme o manual de Metodologia Científica.
**Regra de citação:** apenas literatura científica com **DOI ativo e auditável**; legislação e Sinopses do INEP como fontes primárias com URL oficial.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `TCC_MARIA_SOCORRO.pdf` | TCC completo, 27 páginas, A4, 2,5 cm, 1,5, sumário com 33 entradas e 6 quadros |
| `TCC_MARIA_SOCORRO.docx` | Versão editável, Times New Roman 12, 2,5 cm, 1,5 |
| `TCC_CORPO.md` | Corpo textual (introdução ao apêndice) |
| `TCC_PRETEXTUAL.tex` / `.md` | Capa, folha de rosto, resumo, abstract, lista de abreviaturas |
| `TCC_CORPO_14obras_backup.md` | Versão anterior, com 14 obras, mantida para comparação |
| `RELATORIO_DOI_TCC.md` | Auditoria de DOI: 20 aceitas, 9 fontes primárias |
| `doi_audit.json` | Registro bruto da auditoria de DOI |
| `build_tcc.py` | Script de compilação do PDF e do DOCX |
| `tcc_wrapper.tex` | Preâmbulo LaTeX do TCC |
| `templates/tcc_reference.docx` | Modelo DOCX com 2,5 cm, Times 12, 1,5 |
| `../dados/serie_nacional_tea.csv` | Série nacional 2021–2024, com taxas e crescimento |
| `../dados/regioes_2024_tea.csv` | Indicadores por região em 2024 |
| `../dados/estados_2024_tea.csv` | Indicadores por UF em 2024 |
| `../dados/cenarios_2025_2027.csv` | Cenários exploratórios |
| `../dados/doi_audit_20.json` | Metadados e status HTTP das 20 obras |
| `../scripts/extrair_dados_inep.py` | Extração e cálculo dos indicadores do Censo |
| `../scripts/auditar_dois_tcc.py` | Auditoria dos 20 DOIs |

## Estrutura

- Capa
- Folha de rosto
- Resumo
- Abstract
- Lista de abreviaturas e siglas
- Sumário
- 1 Introdução
- 2 Referencial teórico (2.1 a 2.4)
- 3 Metodologia (3.1 a 3.5)
- 4 Resultados (4.1 a 4.7)
- 5 Discussão (5.1 a 5.6)
- 6 Conclusão
- Referências

## Como reconstruir

```bash
cd artigos/ARTIGO_MARIA_SOCORRO_TEA

# 1. baixar e extrair a Sinopse 2024 do INEP em /tmp/inep
#    (URL na referência do TCC)

# 2. recalcular os indicadores
python3 scripts/extrair_dados_inep.py

# 3. auditar os 20 DOIs
python3 scripts/auditar_dois_tcc.py

# 4. compilar PDF e DOCX
cd TCC && python3 build_tcc.py
```

O script de compilação:

1. converte `TCC_CORPO.md` em LaTeX;
2. envolve tabelas e URLs/DOIs para não estourar as margens;
3. insere `\needspace` antes dos quadros para evitar títulos órfãos;
4. compila `tcc_wrapper.tex` duas vezes (sumário e páginas);
5. gera o sumário do DOCX a partir do `.toc`;
6. monta o DOCX com o modelo de 2,5 cm.

## Limitação central dos dados

As Sinopses Estatísticas da Educação Básica não publicam o cruzamento entre tipo de deficiência e etapa de ensino. Por isso, os indicadores do TCC se referem ao conjunto da educação básica; a análise específica dos anos iniciais exigiria os microdados do Censo Escolar. Essa limitação está declarada na seção 3.6 e retomada na discussão.

## Pendências antes de entregar

1. Revisar o texto com a orientação antes da submissão.
2. Confirmar se a legislação e as Sinopses podem permanecer como fontes primárias sem DOI (decisão já adotada e declarada).
3. Revisar o texto e a paginação no Word, se o DOCX for o arquivo de entrega.
4. Atualizar o sumário do DOCX se a paginação mudar (o sumário atual usa as páginas do PDF).

## Observação

O PDF é o artefato de referência para paginação e sumário. O DOCX é a versão editável; como a renderização de fontes e quebras pode variar no Word, confira o sumário após qualquer edição.
