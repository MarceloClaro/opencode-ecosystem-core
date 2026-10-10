# Revisão da dissertação para submissão

Data da revisão: 10 de outubro de 2026.

**Resultado:** versão revista em português brasileiro, com composição ABNT atualizada, PDF compilado e fonte LaTeX consolidada. A preparação editorial está concluída; a submissão definitiva depende dos dados autorais e institucionais indicados abaixo. Esta revisão não equivale à aprovação de banca ou a uma certificação externa da pesquisa.

## Arquivos

- `output/pdf/dissertacao-abnt.pdf`: PDF revisto, com 97 páginas.
- `dissertacao-abnt.tex`: fonte consolidada, com módulos e listagens incorporados; não depende dos caminhos externos das listagens.
- `dissertacao.tex` e `modulos/`: fonte modular atualizada.
- `dissertacao.pdf`: cópia atualizada do PDF no local original.
- `revisao-abnt/original/`: cópia da dissertação, dos módulos e do histórico anteriores à revisão.
- `revisao-abnt/auditoria_referencias.json` e `.md`: metadados, fontes consultadas, alterações e limites da auditoria bibliográfica.
- `revisao-abnt/conferencia_pdf.json`: resultados das verificações documentais e de área da página.
- `revisao-abnt/manifesto_fontes.json`: hashes dos arquivos utilizados na consolidação.

## Base normativa consultada

| Norma | Aplicação | Fonte consultada |
| --- | --- | --- |
| ABNT NBR 14724:2024, versão corrigida 2025 | Estrutura, apresentação, margens, espaçamento e paginação | [Texto normativo disponibilizado pela Prefeitura do Rio](https://vigilanciasanitaria.prefeitura.rio/wp-content/uploads/sites/84/2025/10/ABNT-NBR-14724-2025-informacao-e-documentacao-trabalho-academico.pdf) |
| ABNT NBR 10520:2023 | Citações e sistema autor-data | [Texto normativo disponibilizado pela FURG](https://ppgletras.furg.br/images/ABNT/2023_abnt-10520-citacoes.pdf) |
| ABNT NBR 6023:2025 | Referências | [Texto normativo disponibilizado pela FHO](https://www.fho.edu.br/assets/documentos/FHO_Biblioteca_Referencia_ABNT_6023_2025.pdf) |
| ABNT NBR 6028:2021 | Resumo, abstract e palavras-chave | [Texto normativo disponibilizado pela Fatec Zona Sul](https://fateczonasul.edu.br/wp-content/uploads/2023/03/NBR-6028.pdf) |
| ABNT NBR 6024:2012 | Numeração progressiva | [Texto normativo disponibilizado pela UFSC](https://cnm.paginas.ufsc.br/files/2020/02/ABNT-NBR-6024.pdf) |
| ABNT NBR 6027:2012 | Sumário | [Texto normativo disponibilizado pela Fatec Zona Sul](https://fateczonasul.edu.br/wp-content/uploads/2023/03/NBR-6027.pdf) |

A [Biblioteca da PUCRS](https://biblioteca.pucrs.br/apoio-a-pesquisa/modelos-de-normas-tecnicas-de-documentacao/) informa que seus modelos seguem as normas vigentes, mas exige login individual para acesso ao conteúdo. Foi aplicada a base ABNT consultada. A comparação final com o modelo específico do programa e da instituição permanece pendente; não foram presumidas exigências institucionais não acessíveis.

## Alterações de apresentação

- Papel A4; margens superior e esquerda de 3 cm, inferior e direita de 2 cm. A configuração preserva essas medidas, impedindo que o arredondamento automático da classe amplie a área textual.
- Fonte serifada de tamanho 12 no corpo, entrelinhas de 1,5 e recuo de parágrafo de 1,25 cm; títulos com hierarquia uniforme. A família TeX Gyre Termes é uma escolha editorial, não uma imposição da ABNT.
- Tabelas em fonte menor e espaçamento simples, títulos acima e indicação de elaboração própria abaixo; todas as tabelas têm chamada no texto. O histórico evolutivo passou a permitir quebra entre páginas.
- Referências em espaço simples, alinhamento à esquerda e separação entre entradas. Chamadas autor-data com caixa normal; até três autores identificados e uso uniforme de *et al.* para quatro ou mais.
- Elementos pré-textuais reordenados: folha de rosto, ficha, aprovação pendente, agradecimentos, resumo, abstract, listas e sumário. A ficha não entra na contagem; os números aparecem a partir da parte textual.
- Referências e glossário antecedem os apêndices. As remissões do corpo utilizam “seção” e identificadores automáticos; o comando interno `chapter` foi preservado para a hierarquia da classe.
- Resumo e abstract reescritos em parágrafo único, com objetivo, método, resultados e limites. Palavras-chave em linha própria, separadas por ponto e vírgula e terminadas por ponto.

## Revisão editorial e científica

O título passou a ser **Roteamento inspirado em atenção: formalização do núcleo matemático em Lean 4 e avaliação empírica interna**. A alteração corresponde aos procedimentos registrados: os experimentos medem arrependimento, acerto e latência, sem aprendizagem dos pesos ou avaliação de calibração probabilística.

Foram corrigidas ou delimitadas as seguintes afirmações:

- T11 demonstra um limite da exponencial deslocada em aritmética real; não certifica integralmente a execução IEEE-754. T3 documenta existência de maximizador; não prova sozinho a correção do roteador concreto.
- Os intervalos registrados usam desvio com divisor `n` e ignoram o agrupamento de 40 decisões por piscina. Foram mantidos os valores originais e classificados como resumos exploratórios. Não houve recálculo inferencial.
- Bancada principal, ablações e correlações utilizam conjuntos ou sequências de sorteios distintos. O pareamento vale dentro das comparações de cada ablação.
- A variação de `q_w` reescala o arrependimento entre elegíveis com cobertura unitária; não representa validação com diferentes critérios de qualidade.
- A condição de confiança ruidosa também arredonda a confiança para 0 ou 1. Esse tratamento foi explicitado, preservando o código e os resultados existentes.
- O estudo com onze cartões do catálogo calcula elegibilidade e rankings para cinco descrições; não executa os agentes nem mede a qualidade de suas respostas.
- O total de testes aleatórios relatado foi restringido a 20 mil vetores. Não foi identificado um registro individualizável da segunda execução que permitisse sustentar 40 mil.
- Foram retiradas alegações de pesos “aprendidos”, equivalência estatística com o acaso, relação dose–resposta e descarte da influência das sementes.
- “Reprodução publicada” foi substituída por artefatos locais de reprodução. O depósito público não possui endereço identificado no material revisto.
- Demonstrações e inventários de literatura redundantes foram retirados do corpo. Os apêndices de código, resultados, especificações e transcrições foram preservados; a versão original permanece disponível.

Os dados e as provas não foram reexecutados como parte da revisão editorial. A transcrição histórica registra 63 testes aprovados, mas isso não comprova a execução atual de toda a fonte incorporada. As revisões auxiliares foram internas e automatizadas, sem revisão cega, aprovação de banca ou validação externa.

## Referências e verificações

A auditoria consultou 41 registros Crossref, nove páginas arXiv e um registro oficial NeurIPS: **51 referências**, incluindo 50 DOIs confirmados e uma obra com endereço oficial dos anais. Todas têm disponibilidade e data de acesso; os preprints originais foram preservados. A auditoria bibliográfica confirma identidade e metadados, sem validar todas as afirmações científicas atribuídas às obras.

O diagnóstico do projeto, executado antes das edições, apresentou 18 verificações aprovadas e duas advertências, sem falhas; especificações, registro evolutivo e memória do projeto estavam acessíveis. A composição final foi compilada com XeLaTeX no ambiente WSL existente. O compilador do editor integrado retornou `Unable to find standard directories for platform`; essa limitação de ambiente não impediu a geração local do PDF. A fonte consolidada foi aberta no editor e preservada.

A conferência do PDF encontrou 97 páginas A4, nenhuma citação sem referência, nenhuma referência sem citação, nenhuma remissão indefinida e nenhum texto fora da área considerada na verificação de limites. As páginas de capa, rosto, resumo, corpo, tabelas, referências, glossário e apêndices foram renderizadas para revisão visual. Os logs não registram caixas excedentes nem caracteres ausentes. Persistem advertências de depreciação da classe e remoção de delimitadores matemáticos em um marcador de navegação, sem prejuízo do texto impresso.

## Pendências para a submissão definitiva

1. Informar nome oficial do programa, denominação do título, área de concentração, linha de pesquisa e nome/titulação do orientador.
2. Obter a ficha catalográfica institucional para a versão final.
3. Preencher data, composição e assinaturas da banca somente após os respectivos atos de defesa/aprovação.
4. Confirmar declarações éticas e demais documentos exigidos pelo programa; não foi presumida dispensa institucional.
5. Comparar a versão com o modelo específico da PUCRS e com as regras do programa, acessíveis mediante login institucional.
6. Definir o depósito público dos artefatos e seu identificador persistente. Análise estatística com agrupamento, certificação numérica, comparação externa e reprodução independente continuam como limitações/trabalhos futuros, explicitados no próprio texto.

Registro evolutivo da revisão: **R779**, sem escore atribuído e sem auditoria externa declarada.
