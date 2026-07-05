# PROMPTS.md — Prompts reutilizáveis versionados

## P01 — Revisão ABNT de anteprojeto
```
Você é um revisor técnico ABNT. Analise o arquivo [ANTEPROJETO_PPGTE_2026.md] e verifique:
1. Ortografia e gramática (português formal)
2. Margens: superior/inferior 2,5cm; esquerda/direita 3,0cm
3. Fonte Times New Roman 12pt, espaço 1,5
4. Referências em ABNT NBR 6023:2018
5. Citações no formato (AUTOR, ano)
6. Zero travessões (—) — substituir por ponto e vírgula ou dois-pontos
7. Todas as siglas expandidas na primeira ocorrência
8. Palavras-chave: 3 a 5, separadas por ponto

Retorne: lista de correções necessárias com localização (linha ou seção).
```

## P02 — Verificação de anonimato
```
Analise o arquivo PDF do anteprojeto e verifique se há qualquer marca de autoria:
- Nome do candidato
- Nome do orientador
- Link para GitHub pessoal
- Menção explícita de "autor do OpenCode Ecosystem"
- Qualquer referência que permita identificar o autor

Retorne: APROVADO (anônimo) ou REPROVADO com lista de trechos problemáticos.
```

## P03 — Conversão Markdown para PDF ABNT
```
Converta o arquivo ANTEPROJETO_PPGTE_2026.md para PDF usando pandoc com template ABNT.
Especificações:
- Margens: sup/inf 2,5cm; esq/dir 3,0cm
- Fonte: Times New Roman 12pt
- Espaçamento: 1,5
- Citações ABNT
- Sem numeração de páginas visível no corpo
- Referências ao final

Comando base: pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="Times New Roman" -V fontsize=12pt
```

## P04 — Pipeline TDD para artefatos
```
Use TDD para validar este artefato. Siga este protocolo, sem pular etapas:
1. Leia a spec inteira (specs/API_SPEC.md, specs/RULES.md) antes de qualquer ação
2. Execute os casos de validação definidos em specs/TESTS_SPEC.md
3. Reporte cada CT como PASSOU ou FALHOU
4. Para cada FALHOU, sugira a correção exata
5. Após correções, reexecute os testes e confirme que todos passam
6. NÃO altere os testes sem aprovação explícita
```

## P05 — Análise de conformidade LGPD
```
Analise a arquitetura do OpenCode Ecosystem (125 agentes, pipeline MASWOS) quanto à conformidade com a LGPD (Lei 13.709/2018). Verifique:
1. Onde dados pessoais são processados (local vs nuvem)
2. Se há criptografia em repouso e em trânsito
3. Se há mecanismo de anonimização/pseudonimização
4. Se há logs de acesso e auditoria
5. Se há consentimento explícito para processamento
6. Se há direito ao esquecimento (exclusão de dados)

Formato: Relatório técnico com achados, riscos e recomendações. Citar artigos da LGPD.
```

## P06 — Busca bibliográfica com rastreabilidade
```
Realize busca bibliográfica sobre "[TEMA]" nas seguintes fontes:
- arXiv (cs.AI, cs.CY)
- Semantic Scholar
- PubMed (se aplicável)
- OpenAlex

Para cada referência encontrada:
1. Extraia título, autores, ano, DOI
2. Verifique se o DOI resolve (fetch real)
3. Classifique relevância (Alta/Média/Baixa)
4. Gere citação ABNT NBR 6023:2018

NUNCA gere referências sem DOI verificado.
```

## P07 — Construção de slide deck para defesa
```
Crie uma apresentação HTML (10 slides) para defesa oral de anteprojeto no PPGTE/UFC.
Especificações:
- Tema: html-ppt-zhangzara-signal (navy + gold, institucional)
- Navegação: ← → teclado
- 10 slides seguindo estrutura em specs/API_SPEC.md
- Cada slide: 1 ideia central, sem poluição visual
- Incluir diagramas da pasta figuras/
- Tempo total: 10 minutos

Use a skill html-ppt para gerar o deck.
```

## P08 — Auditoria TSAC de texto acadêmico
```
Execute auditoria TSAC (87 padrões anti-IA) no texto fornecido.
Verifique:
1. Travessões (—) → substituir por ponto e vírgula
2. Palavras proibidas: "crucial", "essencial", "notadamente", "outrossim", "outrossim"
3. Estruturas de IA: "É importante ressaltar que...", "Neste contexto..."
4. Repetição de padrões sintáticos
5. Adjetivação excessiva

Retorne: texto corrigido + relatório de alterações (formato diff).
```
