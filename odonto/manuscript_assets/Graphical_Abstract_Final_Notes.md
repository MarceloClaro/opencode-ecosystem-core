# Resumo gráfico — arquivos finais EN e PT

## Arquivos

- Submissão: `Graphical_Abstract_Final.pdf` (vetorial; formato preferido pela orientação geral da Elsevier).
- Edição: `Graphical_Abstract_Final.svg` (texto editável, fonte Arial).
- Prévia: `Graphical_Abstract_Final.png` (6000 × 2400 pixels; 400 dpi; proporção 2,5:1).
- Versão portuguesa: os mesmos três formatos com sufixo `_PT`.
- Reprodução: `render_graphical_abstract_final.py` lê os valores diretamente de `calibrated_clinical_internal_validation_corrected_sklearn190.json`.
- Evidência técnica: `graphical_abstract_final_quality.json` registra dimensões, fonte, resumo criptográfico do JSON e verificação geométrica de textos.

O resumo gráfico anterior permanece preservado nos arquivos `Graphical_Abstract.*`; os arquivos `Final` o substituem no novo pacote. A versão anterior apresentava uma proporção diferente da recomendada e não incluía os resultados da recalibração.

## Legenda em inglês

**Graphical abstract.** Exploratory tooth-level early-childhood caries prediction in a public longitudinal cohort. Five outer and three inner folds were grouped by child. Intercept-and-slope recalibration was fitted only on training children and evaluated on held-out children. The Brier score measures probabilistic error; lower values are better. Differences are recalibrated minus uncalibrated scores, with paired 95% intervals from 1,000 child-cluster bootstrap resamples of fixed out-of-fold predictions. These intervals do not include uncertainty from refitting the entire modelling pipeline. The minimal model's interval excludes zero; the spatial model's interval includes zero. Neither the incremental clinical value of spatial information nor clinical utility has been established. Created using reproducible Matplotlib code (version 3.11.1) from the corrected aggregate results. OpenAI Codex (GPT-6, 1 October 2026) assisted with programming, layout and translation; no generative image model or patient image was used. Human authors must review the final content and approve this disclosure before submission.

## Legenda em português

**Resumo gráfico.** Predição exploratória de cárie na primeira infância por dente em uma coorte longitudinal pública. Cinco partições externas e três internas foram agrupadas por criança. A recalibração de intercepto e inclinação foi ajustada apenas nas crianças do treinamento e avaliada em crianças retidas para teste. O escore de Brier mede o erro probabilístico; valores menores são melhores. As diferenças correspondem ao escore recalibrado menos o não calibrado, com intervalos pareados de 95% calculados por 1.000 reamostragens bootstrap de crianças sobre as predições fixas fora da amostra. Esses intervalos não incluem a incerteza decorrente do reajuste de todo o procedimento de modelagem. O intervalo do modelo mínimo exclui zero; o do modelo espacial inclui zero. O valor clínico adicional da informação espacial e a utilidade clínica ainda não foram estabelecidos. Produzido com código reprodutível em Matplotlib (versão 3.11.1), a partir dos resultados agregados corrigidos. OpenAI Codex (GPT-6, 1º de outubro de 2026) auxiliou na programação, diagramação e tradução; não foram usados gerador de imagens nem imagens de pacientes. Os autores humanos devem revisar o conteúdo final e aprovar esta declaração antes da submissão.

## Proveniência e interpretação

Fonte clínica: Yang F, Teng F, Zhang Y, et al. *Single-tooth resolved, whole-mouth prediction of early childhood caries via spatiotemporal variations of plaque microbiota*. Cell Host & Microbe. 2025;33(6):1019–1032.e6. DOI: [10.1016/j.chom.2025.05.006](https://doi.org/10.1016/j.chom.2025.05.006). Tabela pública: [Single-tooth-ECC](https://github.com/HuangShiLab/Single-tooth-ECC), `Table_S1.xlsx`, planilha `all_metadata`.

Os resultados mostrados são da análise secundária OdontoCA, não das análises microbiômicas do artigo-fonte. O JSON corrigido informa 996 transições, 83 eventos, 81 crianças, semente 20260930 e separação corrigida dos grupos. Os resultados da execução histórica com outra política de particionamento não foram usados.

O GA não apresenta estimativa de benefício clínico, limiar de tratamento, validação externa, diagnóstico por imagem ou superioridade demonstrada do modelo espacial. Os dois intervalos exibidos comparam a recalibração com a ausência de recalibração dentro de cada modelo; não comparam os modelos entre si. A seleção exploratória da estratégia de recalibração é uma limitação discutida no manuscrito.

## Orientações editoriais consultadas em 1º de outubro de 2026

A [orientação geral de resumo gráfico da Elsevier](https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract) recomenda arquivo separado, leitura clara, mínimo de 1328 × 531 pixels a 300 dpi e proporção de 500:200 em imagens maiores. PDF consta entre os formatos preferidos. Os arquivos entregues excedem os requisitos de tamanho e resolução e mantêm essa proporção.

A [política de IA da Elsevier](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals), atualizada em junho de 2026, exige transparência na programação assistida e nas visualizações derivadas de dados. A seção específica de resumos gráficos orienta o uso de ferramentas científicas ou profissionais de ilustração e veda geradores de imagem de propósito geral. Estes arquivos foram renderizados deterministicamente por Matplotlib a partir de texto e estatísticas agregadas; o auxílio de Codex na programação está declarado. Essa descrição não equivale a uma aprovação prévia do periódico.

A URL das [diretrizes específicas do Journal of Dentistry](https://www.sciencedirect.com/journal/journal-of-dentistry/publish/guide-for-authors) foi consultada, mas a leitura automatizada retornou erro de acesso. Os critérios específicos fornecidos pelo usuário foram mantidos; não se afirma que as exigências de outros periódicos se apliquem ao Journal of Dentistry.

O texto de notas e legendas é material de apoio, separado do arquivo visual. O resumo gráfico não contém autores, afiliações, fotografias, ícones de terceiros, título genérico “Graphical abstract” ou referências bibliográficas no corpo da figura.
