# Avaliação editorial e científica do OdontoCA

## Fontes examinadas

- [Notebook executado no Colab](https://colab.research.google.com/drive/1JNkdMWv2kE_QMoEf0exn21RMnABCfe0Q) e cópia local `OdontoCA_v1_3_2_FULL_RESEARCH_COM_IMAGEM_FLUXOGRAMA_EXECUTED (3).ipynb`. As 48 células têm o mesmo código e as mesmas saídas nas duas cópias. O arquivo do Colab conserva contadores de execução; a cópia local os zerou.
- Modelo Word original do link fornecido pelo usuário: arquivo `.docx` ilustrativo, com dados fictícios, estrutura de revisão de escopo e autoria do exemplo. Seu conteúdo não foi usado como dado nem como autoria do novo artigo. [O mesmo arquivo no Google Drive](https://docs.google.com/document/d/1GE9f4uCBQ9cvz81k63O2J4oGbT7Tr8Z7/edit) foi editado e renomeado para o manuscrito OdontoCA.
- `Texto colado.txt`: fluxograma Mermaid do OdontoCA v1.9.1. Ele descreve arquitetura e critérios de aceite, sem saídas de execução. Foi preservado em `manuscript_assets/Supplementary_Architecture_v1_9_1.mmd`.
- [Guia oficial do *Journal of Dentistry*](https://www.sciencedirect.com/journal/journal-of-dentistry/publish/guide-for-authors), usado para organizar o rascunho em inglês, com resumo curto, citações numeradas, manuscrito cego e declarações editoriais.

## Parecer

**O trabalho disponível demonstra uma prova de conceito técnica com dados sintéticos. Não demonstra acurácia clínica.** O título do notebook menciona “FULL RESEARCH”, mas o perfil efetivamente salvo é `CI_SMOKE`. O relatório final declara `NOT_RUN` para reprodução clínica, pareamento Qiita e auditoria de imagens, `NOT_REQUESTED` para treino visual e `NOT_PERFORMED` para validação externa.

| Evidência da execução v1.3.2 | Resultado |
|:--|:--|
| Crianças simuladas | 36 |
| Transições dentárias sintéticas elegíveis | 686 |
| Eventos `H→C` | 54 (7,87%) |
| Validação | 3 folds externos e 2 internos, agrupados por criança |
| Testes | 24 `PASS`, 2 `SKIP` dependentes de dados reais |
| Autômato: PR-AUC / ROC-AUC | 0,081743 / 0,534546 |
| Clínico-espacial: PR-AUC / ROC-AUC | 0,105386 / 0,590571 |
| Microbioma sintético: PR-AUC / ROC-AUC | 0,095530 / 0,532613 |
| Combinado: PR-AUC / ROC-AUC | 0,074825 / 0,480397 |

O combinado ficou abaixo de 0,5 na ROC-AUC e abaixo da prevalência na PR-AUC. A implementação corretamente impede usar `1 − ROC-AUC` como desempenho “corrigido” após observar o resultado. Os números de 2.504 registros, 89 crianças e 997 transições iniciais, encontrados como constantes/contagens-alvo no código e no diagrama, **não foram reproduzidos nesta execução**; não devem figurar como resultados do OdontoCA.

### Forças metodológicas observadas

1. O alvo positivo é explicitamente a transição `H→C` entre visitas consecutivas, com variáveis de futuro separadas dos preditores.
2. O laço externo contém uma asserção de ausência de crianças compartilhadas entre treino e teste; a seleção de hiperparâmetros ocorre em folds internos.
3. O pré-processamento dos ASVs sintéticos está dentro das pipelines de validação cruzada, e a coluna de probabilidade positiva é localizada pela ordem real de classes do estimador.
4. O relatório diferencia módulos experimentais dos módulos clínicos não executados.

### Fragilidades que exigem correção

1. O teste TDD-005 pode capturar a própria falha de asserção e terminar como `PASS` mesmo se a duplicata for aceita.
2. O TDD-010 usa uma condição tautológica; a asserção operacional no laço externo é mais forte que esse teste.
3. Dois gates (`GATE-04` e `GATE-05`) são marcados diretamente como `True`; devem gerar evidência verificável própria.
4. Brier e log loss foram calculados, mas curva, intercepto e inclinação de calibração não aparecem; a linha interna `calibration = PASS` não comprova boa calibração.
5. Os 200 bootstraps solicitados não vieram acompanhados, no relatório salvo, de intervalos de confiança interpretáveis.
6. O pacote ZIP de resultados citado pelo notebook não integra os materiais recebidos, e a execução integral não foi repetida independentemente nesta avaliação.

## Relação entre v1.3.2 e arquitetura v1.9.1

A v1.9.1 especifica 46 requisitos SDD, 58 testes TDD, adaptadores de anotação, quatro domínios visuais, controle de qualidade, deduplicação entre partições, treino visual, odontograma e fusão por mesma coorte/paciente/visita/dente. Esses números e módulos representam **escopo projetado**, pois o anexo não apresenta relatórios de testes nem métricas. O próprio nó final condiciona “resultados para artigo” à execução real aprovada e distingue aprovação técnica de validação clínica.

Assim, o artigo entregue é um **rascunho metodológico com resultados sintéticos identificados**. Uma versão que alegue desempenho real no *Journal of Dentistry* depende, no mínimo, de:

1. executar e documentar a reprodução da tabela clínica real e o pareamento microbiológico;
2. corrigir os testes e gates frágeis, preservar dados/código/manifestos e informar incerteza e calibração;
3. testar a coorte externa e as imagens apenas nos conjuntos com referência e independência demonstráveis;
4. confirmar autorização de uso dos dados, aprovação ética ou dispensa aplicável, autoria, contribuições CRediT, financiamento e conflitos;
5. preparar página de título separada e versão anônima do manuscrito, conferir permissões do Colab e depositar materiais em repositório apropriado.

## Arquivos produzidos

- `Journal_of_Dentistry_Example_OdontoCA.docx`: manuscrito cego em inglês, estruturado a partir do exemplo, com figuras e números sintéticos corretamente rotulados. Esta versão local preserva a diagramação final conferida.
- `Journal_of_Dentistry_Example_OdontoCA.pdf`: prévia paginada da versão local, conferida visualmente.
- `Journal_of_Dentistry_Example_OdontoCA.md`: fonte editável do manuscrito.
- `manuscript_assets/Figure_1_pipeline.png`, `Figure_2A_synthetic_PR.png`, `Figure_2B_synthetic_ROC.png`: figuras em arquivos separados.
- `manuscript_assets/Supplementary_Architecture_v1_9_1.mmd`: arquitetura integral fornecida pelo usuário.

O documento vinculado no Google Drive foi atualizado no mesmo endereço, com texto, três tabelas e três figuras. Uma exportação `.docx` feita pelo Google Docs preservou o conteúdo e as imagens, mas a conversão desse arquivo exportado no LibreOffice cortou parte superior das figuras. Para leitura paginada e revisão de submissão, use o `.docx` local e sua prévia `.pdf`; a cópia online permanece disponível para edição colaborativa.

**Conclusão editorial:** o manuscrito pode circular para revisão dos autores como estudo técnico preliminar. Não há base para submetê-lo como validação clínica ou estudo de acurácia diagnóstica.
