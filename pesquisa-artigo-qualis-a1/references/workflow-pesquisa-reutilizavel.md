# Workflow reutilizável de pesquisa e esqueleto de artigo

Usar este procedimento quando o usuário solicitar um esqueleto, protocolo ou primeira versão de artigo sobre tema novo, especialmente quando houver três ou mais subtemas independentes, PDF-modelo, exigência de fontes atuais ou necessidade de comparar literatura técnica, pedagógica e normativa.

## Entradas mínimas

Registrar tema e interpretação dos termos ambíguos; tipo de manuscrito; área e nível; público/contexto; pergunta provisória; idioma; período de busca; fontes ou PDF fornecidos; norma de citação; periódico/programa, se houver; e se há dados reais. Se “assimilação” puder significar substituição, perguntar ou registrar a interpretação adotada antes de redigir.

## Etapas operacionais

1. **Desambiguar e delimitar.** Converter o tema em um recorte investigável. Normalizar erros de digitação sem apagar a forma original; registrar alterações relevantes, como `chucks → chunks`.
2. **Decompor a busca.** Separar o tema em 3–5 frentes independentes, por exemplo: fundamentos pedagógicos; engenharia e letramento em IA; agentes/prompts/skills; hooks/lógica/chunks; ética, privacidade e políticas. Não misturar todas as perguntas em uma única busca.
3. **Pesquisar por frente.** Para cada frente, coletar fontes acadêmicas, normativas, institucionais e técnicas pertinentes. Exigir título, autoria/entidade, ano, DOI ou URL oficial resolvível, afirmação sustentada, tipo de evidência e limitação.
4. **Triangular.** Distinguir artigo revisado por pares, revisão, preprint, norma, orientação, documentação de fornecedor e proposta legislativa. Dar prioridade a fontes primárias e oficiais; usar fontes técnicas de fornecedor apenas para definir funcionamento de um produto, nunca como prova de eficácia pedagógica.
5. **Consolidar.** Comparar convergências, divergências, implicações e lacunas entre as frentes. Formular uma tese provisória e marcar cada afirmação como fato da fonte, inferência, hipótese, proposta ou resultado ainda não disponível.
6. **Projetar o artigo.** Montar título, resumo-protocolo, problema, pergunta, objetivos, referencial, glossário, arquitetura conceitual, método, sequência didática, resultados esperados e limitações. Se não houver dados, usar `protocolo`, `proposta` ou `resultados esperados`, nunca resultados observados.
7. **Auditar.** Verificar DOI/URL, metadados, correspondência citação–referência, atualidade, status jurídico, coerência entre método e alegações, risco de plágio e ausência de números inventados. Registrar pendências bloqueadoras.
8. **Entregar.** Salvar um Markdown completo e rotulado (`esqueleto`, `protocolo`, `rascunho` ou `com pendências`) com referências auditadas, referências pendentes separadas, matriz de rastreabilidade e perguntas de banca.

## Ficha obrigatória por fonte

```text
ID:
Referência completa:
Tipo: [artigo / revisão / norma / orientação / documentação / preprint / proposta]
DOI ou URL oficial:
Data de acesso:
Status: [verificada / não verificada / retratada / proposta / temporalmente sensível]
Afirmação sustentada:
Trecho, resumo ou seção conferida:
Limitação:
Uso permitido no artigo:
```

## Estrutura mínima da síntese de cada frente

- **Achados:** o que as fontes sustentam.
- **Implicações:** como isso altera problema, método ou sequência didática.
- **Lacunas:** o que ainda não foi demonstrado.
- **Contradições:** posições divergentes e qualidade relativa das evidências.
- **Fontes auditadas:** referências com DOI/URL e status.

## Regras para o caso de PDF-modelo

Ler a estrutura visual e textual, identificando título, resumo, seções, colunas, equações, tabelas, figuras, declarações editoriais, referências e metadados. Tratar o PDF como exemplo de apresentação, nunca como evidência de Qualis, validade, política editorial ou regra universal. Reproduzir duas colunas, numeração ou estilo apenas se a norma oficial do periódico exigir ou se o usuário pedir explicitamente.

## Auditoria final específica do workflow

Antes de declarar conclusão, conferir:

- cada afirmação central tem fonte ou está rotulada como hipótese/proposta;
- toda fonte central tem DOI/identificador/URL oficial conferido;
- nenhuma fonte foi usada além do que seu desenho sustenta;
- toda citação tem referência e toda referência citada aparece no texto;
- legislação vigente não foi confundida com orientação, consulta ou projeto de lei;
- documentação técnica não foi confundida com evidência educacional;
- hooks, skills e chunks propostos foram identificados como proposta quando não houver literatura validando-os;
- não há resultados, amostra, aprovação ética ou métricas inventados;
- o relatório separa limitações da literatura e limitações do estudo proposto;
- o arquivo final informa pendências e não promete nota, Qualis ou aceitação.

## Padrão de saída

Entregar: título provisório; status; resumo estruturado; problema; pergunta; objetivos; tese/hipótese; referencial; glossário; arquitetura; método; módulos; sequência didática; exemplos técnicos; resultados esperados; ética; limitações; conclusão provisória; referências auditadas; pendências; rubrica de banca. Adaptar a ordem ao gênero e ao periódico.
