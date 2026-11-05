# TCC — Maria do Socorro Araujo Martins Leite

**Título:** A inclusão escolar de estudantes com Transtorno do Espectro Autista nos anos iniciais: políticas, práticas pedagógicas e formação docente
**Formato:** TCC (monografia), conforme o manual de Metodologia Científica.
**Regra de citação:** apenas literatura científica com **DOI ativo e auditável**; legislação como fonte primária com URL oficial.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `TCC_MARIA_SOCORRO.pdf` | TCC completo, 27 páginas, A4, 2,5 cm, 1,5, sumário com 32 entradas |
| `TCC_MARIA_SOCORRO.docx` | Versão editável, Times New Roman 12, 2,5 cm, 1,5 |
| `TCC_CORPO.md` | Corpo textual (introdução ao apêndice) |
| `TCC_PRETEXTUAL.tex` / `.md` | Capa, folha de rosto, resumo, abstract, lista de abreviaturas |
| `TCC_CORPO_14obras_backup.md` | Versão anterior, com 14 obras, mantida para comparação |
| `RELATORIO_DOI_TCC.md` | Auditoria de DOI: 8 aceitas, 6 excluídas, 5 fontes primárias (fora do TCC) |
| `doi_audit.json` | Registro bruto da auditoria de DOI |
| `build_tcc.py` | Script de compilação do PDF e do DOCX |
| `tcc_wrapper.tex` | Preâmbulo LaTeX do TCC |
| `templates/tcc_reference.docx` | Modelo DOCX com 2,5 cm, Times 12, 1,5 |

## Estrutura

- Capa
- Folha de rosto
- Resumo
- Abstract
- Lista de abreviaturas e siglas
- Sumário
- 1 Introdução
- 2 Revisão da literatura
- 3 Metodologia
- 4 Resultados
- 5 Discussão
- 6 Conclusão
- Referências

## Como reconstruir

```bash
cd artigos/ARTIGO_MARIA_SOCORRO_TEA/TCC
python3 build_tcc.py
```

O script:

1. converte `TCC_CORPO.md` em LaTeX;
2. envolve tabelas e URLs/DOIs para não estourar as margens;
3. compila `tcc_wrapper.tex` duas vezes (sumário e páginas);
4. gera o sumário do DOCX a partir do `.toc`;
5. monta o DOCX com o modelo de 2,5 cm.

## Pendências antes de entregar

1. Capa e folha de rosto preenchidas com FACUMINAS, curso, Brasília e título de especialista; linha do orientador removida a pedido.
2. Confirmar com a orientação se a legislação pode permanecer como fonte primária sem DOI.
3. Revisar o texto e a paginação no Word, se o DOCX for o arquivo de entrega.
4. Atualizar o sumário do DOCX se a paginação mudar (o sumário atual usa as páginas do PDF).

## Observação

O PDF é o artefato de referência para paginação e sumário. O DOCX é a versão editável; como a renderização de fontes e quebras pode variar no Word, confira o sumário após qualquer edição.
