import re

with open(r'C:\Users\marce\.config\opencode\criador-artigo\tese_mestrado_cnpq.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the YAML front matter
text = text.replace(
    '---',
    '---',
    1  # only first occurrence
)

# Read original YAML from the saved content and rebuild it properly
new_yaml = """---
title: "A Insustentavel Leveza da Deteccao: Regulacao da Inteligencia Artificial Generativa na Pesquisa Cientifica Brasileira entre a Norma, a Tecnica e o Mercado Global da Quarta Revolucao Industrial"
subtitle: "Analise critica da Portaria CNPq n. 2.664/2026"
author: "Dissertacao de Mestrado"
date: 2026
abstract: "Esta dissertacao analisa criticamente a Portaria CNPq n. 2.664, de 6 de marco de 2026, que institui a Politica de Integridade na Atividade Cientifica do CNPq, a luz da Quarta Revolucao Industrial. A pesquisa adota metodologia juridico-dogmatica de natureza qualitativa, combinando analise normativa, revisao sistematica da literatura tecnica sobre detectores de Inteligencia Artificial Generativa (IAG), regulacao comparada (Uniao Europeia, China, Estados Unidos) e analise de economia politica da inovacao. Os resultados revelam sete ambiguidades hermeneuticas no art. 9 da Portaria, inviabilidade tecnica da fiscalizacao baseada em detectores automaticos, assimetria competitiva no mercado global de P&D e conflitos normativos com a LGPD e a Constituicao Federal. Conclui-se que a Portaria, nao obstante suas boas intencoes, impoe custos regulatorios desproporcionais ao sistema brasileiro de CT&I e propoe-se modelo hibrido de regulacao que combine marcacao tecnica pelos provedores de IA, declaracao simplificada pelo pesquisador e gradacao de exigencias por nivel de risco."
abstract-en: "This thesis critically analyzes CNPq Ordinance No. 2.664, of March 6, 2026, which establishes the Integrity Policy for Scientific Activity, in light of the Fourth Industrial Revolution. The research adopts a qualitative legal-dogmatic methodology, combining normative analysis, systematic review of the technical literature on Generative AI detectors, comparative regulation (European Union, China, United States), and political economy analysis of innovation. The results reveal seven hermeneutic ambiguities in Article 9 of the Ordinance, technical infeasibility of enforcement based on automatic detectors, competitive asymmetry in the global RD market, and normative conflicts with the Brazilian Data Protection Law and the Federal Constitution. The conclusion is that the Ordinance, despite its good intentions, imposes disproportionate regulatory costs on the Brazilian STI system. A hybrid regulation model is proposed, combining technical watermarking by AI providers, simplified researcher declaration, and risk-based requirements."
keywords-en: "Generative Artificial Intelligence; Scientific Integrity; CNPq; Fourth Industrial Revolution; Comparative Regulation"
lang: "pt-BR"
---"""

# Check content before --- mark
idx = text.find('\n---\n')
if idx > 0:
    # Content after first ---
    content = text[idx+5:]  # skip past '---\n'
    
    # Remove the manual SUMARIO section (everything from # SUMARIO to ## 1 INTRODUCAO)
    content = re.sub(r'# SUM.RIO.*?(?=## 1 INTRODU)', '## 1 INTRODU', content, flags=re.DOTALL)
    
    final = new_yaml + '\n' + content
else:
    final = new_yaml + '\n' + text

with open(r'C:\Users\marce\.config\opencode\criador-artigo\tese_mestrado_cnpq.md', 'w', encoding='utf-8') as f:
    f.write(final)

print('Done')
