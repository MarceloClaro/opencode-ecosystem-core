"""Apply the journal editorial revision without altering analytical results."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / 'Journal_of_Dentistry_Example_OdontoCA.md'
PT = ROOT / 'Journal_of_Dentistry_Example_OdontoCA_PT.md'

en_abstract = '''**Objectives:** To develop tooth-level early-childhood caries models from a public longitudinal cohort and assess internal performance with child-separated validation and training-only recalibration.

**Methods:** The outcome was progression from a healthy tooth to caries at the next consecutive visit, two to five months later. Penalised logistic models used minimal clinical or clinical-plus-spatial predictors. Five outer and three inner child-grouped folds separated tuning from evaluation. Recalibration used only outer-training children. Uncertainty was estimated with 1,000 paired child-cluster bootstrap samples of out-of-fold predictions.

**Results:** The analysis included 996 transitions, 83 events (8.33%), and 81 children. Uncalibrated average precision was 0.166 (95% interval 0.120–0.246) for the minimal model and 0.178 (0.138–0.239) for the spatial model; ROC areas were 0.686 (0.618–0.754) and 0.737 (0.660–0.804), respectively. Paired model differences included zero. Intercept-and-slope recalibration reduced the minimal model's held-out Brier score from 0.0806 to 0.0745 (difference −0.00610; 95% interval −0.01173 to −0.00067). The spatial model's change from 0.0754 to 0.0740 had an interval including zero.

**Conclusions:** Training-only recalibration improved one probability score in this exploratory internal evaluation. Spatial superiority and clinical utility remain unestablished. Limited sample size, uncertainty about derived predictors, and absence of external validation constrain clinical interpretation.'''

pt_abstract = '''**Objetivos:** Desenvolver modelos de cárie na primeira infância por dente em uma coorte longitudinal pública e avaliar seu desempenho interno com separação por criança e recalibração ajustada no treinamento.

**Métodos:** O desfecho foi a progressão de dente saudável para cárie na consulta consecutiva seguinte, dois a cinco meses depois. Modelos logísticos penalizados utilizaram preditores clínicos mínimos ou clínicos e espaciais. Cinco partições externas e três internas, agrupadas por criança, separaram ajuste e avaliação. A recalibração utilizou somente crianças do treinamento externo. A incerteza foi estimada por 1.000 reamostragens bootstrap pareadas por criança das predições fora da amostra.

**Resultados:** Foram analisadas 996 transições, 83 eventos (8,33%) e 81 crianças. A precisão média sem recalibração foi 0,166 (intervalo de 95%: 0,120–0,246) no modelo mínimo e 0,178 (0,138–0,239) no espacial; as áreas ROC foram, respectivamente, 0,686 (0,618–0,754) e 0,737 (0,660–0,804). Os intervalos das diferenças entre modelos incluíram zero. A recalibração do intercepto e da inclinação reduziu o Brier do modelo mínimo nas crianças de teste de 0,0806 para 0,0745 (diferença −0,00610; intervalo de 95%: −0,01173 a −0,00067). A mudança espacial de 0,0754 para 0,0740 apresentou intervalo incluindo zero.

**Conclusões:** A recalibração ajustada no treinamento melhorou um escore probabilístico nesta avaliação interna exploratória. A superioridade espacial e a utilidade clínica permanecem sem comprovação. A amostra limitada, as incertezas sobre preditores derivados e a ausência de validação externa restringem a interpretação clínica.'''

en = EN.read_text(encoding='utf-8')
pt = PT.read_text(encoding='utf-8')
en = re.sub(r'(?<=## Abstract\n\n).*?(?=\n\n\*\*Keywords:)', en_abstract, en, flags=re.S)
pt = re.sub(r'(?<=## Resumo\n\n).*?(?=\n\n\*\*Palavras-chave)', pt_abstract, pt, flags=re.S)
en = en.replace('calibration; oral microbiome.', 'calibration.')
pt = re.sub(r'\*\*Palavras-chave.*?\n', '**Palavras-chave (em inglês):** early-childhood caries; clinical prediction; primary teeth; spatial features; internal validation; calibration.\n', pt, count=1)

en = en.replace('This study is reported in accordance with the TRIPOD+AI statement [10] and was appraised with PROBAST+AI [11]. The completed checklists are provided as Supplementary Files S3 and S4.', 'Reporting was mapped to TRIPOD+AI [10], and methodological quality, risk of bias, and applicability were assessed using PROBAST+AI [11]. Supplementary Files S3 and S4 record item-level responses, evidence locations, and unresolved information. These AI-assisted internal assessments are not independent external reviews.')
old_pt = next((p for p in pt.split('\n\n') if 'TRIPOD+AI' in p and '[10]' in p and ('S3' in p or 'S4' in p)), None)
if old_pt:
    pt = pt.replace(old_pt, 'O relato foi mapeado ao TRIPOD+AI [10], e a qualidade metodológica, o risco de viés e a aplicabilidade foram avaliados com o PROBAST+AI [11]. Os Arquivos Suplementares S3 e S4 registram respostas por item, localização das evidências e informações pendentes. Essas avaliações internas assistidas por IA não constituem revisões externas independentes.')
else:
    anchor = '### 2.3.'
    pt = pt.replace(anchor, 'O relato foi mapeado ao TRIPOD+AI [10], e a qualidade metodológica, o risco de viés e a aplicabilidade foram avaliados com o PROBAST+AI [11]. Os Arquivos Suplementares S3 e S4 registram respostas por item, localização das evidências e informações pendentes. Essas avaliações internas assistidas por IA não constituem revisões externas independentes.\n\n'+anchor, 1)

en = en.replace('### 2.3. Prespecified candidate models', '### 2.3. Candidate models')
en = en.replace('Two penalised logistic-regression models were specified before examining their performance.', 'Two penalised logistic-regression feature sets were defined in the analysis code before fitting. No prospectively registered analysis protocol was available.')
pt = pt.replace('### 2.3. Modelos candidatos pré-especificados', '### 2.3. Modelos candidatos')
pt = re.sub(r'Dois modelos de regressão logística penalizada foram.*?desempenho\.', 'Dois conjuntos de preditores para regressão logística penalizada foram definidos no código antes do ajuste. Não havia protocolo de análise registrado prospectivamente.', pt, count=1)

extra_en = 'Sample size was determined by the available public cohort; no formal development or validation sample-size calculation was performed. Neither a final deployment model nor a clinical decision threshold was established.'
extra_pt = 'O tamanho amostral foi determinado pela coorte pública disponível; não foi realizado cálculo formal de tamanho amostral para desenvolvimento ou validação. Não foram definidos modelo final para implantação nem limiar de decisão clínica.'
en = en.replace('### 2.5. Technical audit and analysis boundary', extra_en+'\n\n### 2.5. Technical audit and analysis boundary')
pt = re.sub(r'(?=### 2.5\.)', extra_pt+'\n\n', pt, count=1)

ai_en = 'OpenAI Codex assisted with analysis-code review, execution, translation, and figure scripts; GPT-6 was used for this editorial revision. Earlier session model identifiers were not recorded. Figures were rendered by deterministic Python/Matplotlib scripts from the documented workflow or numerical outputs. No generative image model was used to fabricate observations or primary research images. This assistance does not replace author verification of code, results, or interpretations.'
ai_pt = 'O OpenAI Codex auxiliou a revisão do código analítico, a execução, a tradução e os programas de figuras; GPT-6 foi utilizado nesta revisão editorial. Os identificadores dos modelos de sessões anteriores não foram registrados. As figuras foram renderizadas por programas determinísticos em Python/Matplotlib a partir do fluxo documentado ou de resultados numéricos. Não foi utilizado modelo generativo de imagens para fabricar observações ou imagens primárias de pesquisa. Essa assistência não substitui a verificação dos autores sobre código, resultados e interpretações.'
en = en.replace('## 3. Results', ai_en+'\n\n## 3. Results')
pt = pt.replace('## 3. Resultados', ai_pt+'\n\n## 3. Resultados')
en = en.replace('its content and terminology were verified by the authors.', 'author verification of its content and terminology is required before submission.')
pt = pt.replace('seu conteúdo e sua terminologia foram verificados pelos autores.', 'a verificação de seu conteúdo e de sua terminologia pelos autores é necessária antes da submissão.')

en = en.replace('The real clinical OOF analysis is separate from the source investigators\' published models.', 'Supplementary File S3 maps reporting to TRIPOD+AI; Supplementary File S4 provides the formal PROBAST+AI internal appraisal. Reproducibility materials include analysis scripts and aggregate outputs. The real clinical OOF analysis is separate from the source investigators\' published models.')
pt = pt.replace('## Referências', '## Referências', 1)
for path, content in ((EN,en),(PT,pt)):
    path.write_text(content, encoding='utf-8')
for lang,a in [('EN',en_abstract),('PT',pt_abstract)]:
    n=len(re.findall(r'\S+',re.sub(r'[*]','',a)))
    assert n<=250,(lang,n)
    print(lang,'abstract words including headings',n)

# Translation fragments remain consistent with the canonical edited source.
(ROOT/'manuscript_assets/pt_resumo.md').write_text(pt.split('## 1.')[0],encoding='utf-8')
