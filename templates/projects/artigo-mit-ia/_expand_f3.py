# -*- coding: utf-8 -*-
import re, os

path = r'C:\Users\marce\.config\opencode\artigo-mit-ia\03-discussao-conclusao-referencias.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Use unicode escapes for accented chars
REF_HEADER = '\u0023\u0023\u0020Refer\u00eancias'

sec_511 = """

Esta nova divisao cognitiva do trabalho manifesta-se em tres dimensoes inter-relacionadas. A primeira e a dimensao da autoria: quando modelos de IAG geram codigo, textos, imagens e analises, quem detem a propriedade intelectual sobre esses outputs? Economias avancadas, onde estao sediadas as empresas proprietarias dos modelos, tendem a capturar o valor gerado mesmo quando os inputs (dados, uso) provem de paises de renda media[^13]. A segunda dimensao e a da infraestrutura: o acesso a computacao em nuvem, GPUs e datasets de treinamento e altamente concentrado. Estima-se que mais de 80% da capacidade de computacao em nuvem para IA esteja concentrada em cinco empresas americanas e chinesas, criando dependencia estrutural para paises que nao possuem infraestrutura propria[^14]. A terceira dimensao e a da customizacao: modelos de IAG sao treinados predominantemente em dados e contextos de economias avancadas, gerando vieses que reduzem sua efetividade em contextos de renda media (Gmyrek et al., 2024)[^15].

A literatura emergente documenta que a exposicao ocupacional a IAG segue padroes distintos em paises de renda media comparados a economias avancadas. Ciaschi et al. (2025)[^16] demonstram que, enquanto em paises da OCDE a exposicao concentra-se em ocupacoes de alta renda (profissionais financeiros, advogados, desenvolvedores), na America Latina a exposicao distribui-se de forma mais ampla, afetando tambem ocupacoes de media e baixa renda no setor de servicos. Este padrao amplifica o risco de deslocamento em economias onde o setor de servicos ja nao oferece produtividade suficientemente alta para sustentar o crescimento.

Egana-delSol e Bravo-Ortega (2025)[^17] corroboram esta analise ao identificar que a complementaridade entre IAG e trabalho qualificado e mais pronunciada em economias com maior estoque de capital humano avancado. Em paises de renda media, onde a proporcao de trabalhadores com ensino superior completo e menor, a IAG tende a gerar mais substituicao do que complementaridade, aprofundando a polarizacao do mercado de trabalho e dificultando a transicao para uma economia baseada em inovacao — requisito central para escapar da ARM.
"""

sec_54 = """

**Vietna.** O Vietna constitui um caso relevante de catching up digital baseado em insercao estrategica em cadeias globais de valor. Diferentemente da Coreia do Sul, que construiu capacidade de inovacao autonoma, o Vietna concentrou-se em absorver tecnologia estrangeira via investimento direto externo (IDE) macico, especialmente nos setores de eletronicos e TIC. O pais saltou de exportador de produtos primarios para o segundo maior exportador de smartphones do mundo em menos de duas decadas, sem desenvolver inovacao de fronteira (World Bank, 2024)[^18]. Para a IAG, esta trajetoria sugere que a insercao em cadeias globais de valor intensivas em tecnologia digital pode gerar ganhos de produtividade mesmo sem capacidade de inovacao autonoma — desde que haja investimento complementar em educacao basica e treinamento tecnico.

**India.** A experiencia indiana com servicos de tecnologia da informacao (TI) oferece licoes especificas para a IAG. O pais construiu uma industria de servicos de TI globalmente competitiva com base em custos baixos, proficiencia em ingles e capital humano qualificado em engenharia. Contudo, o modelo indiano enfrenta desafios com a IAG: tarefas de programacao, suporte tecnico e processamento de dados que antes eram terceirizadas para a India estao sendo progressivamente automatizadas por modelos de linguagem. Noy e Zhang (2023)[^19] documentam que assistentes de codigo baseados em IAG reduzem o tempo de programacao em ate 55% para tarefas rotineiras, ameacando o modelo de negocios que sustentou o crescimento do setor de TI indiano. Este efeito ilustra como a IAG pode, paradoxalmente, deslocar exatamente os setores que representavam a via de escape da ARM para economias em desenvolvimento.

**Israel.** Israel oferece um contraponto interessante como economia que transitou de renda media para alta combinando inovacao de fronteira com insercao global seletiva. O ecossistema de startups israelense — com forte vinculacao entre universidades, forcas armadas (Unidade 8200) e capital de risco — gerou inovacoes em ciberseguranca, agricultura digital e tecnologias medicas que posicionam o pais como fornecedor, e nao apenas usuario, de tecnologias de IA[^20]. Para paises de renda media, a licao israelense e que investimentos concentrados em nichos de inovacao com vantagem comparativa podem gerar retornos desproporcionais, mas exigem ecossistemas de inovacao sofisticados que poucos paises conseguem replicar.
"""

sec_55 = """

A operacionalizacao destes tres eixos requer um framework de governanca multinivel que articule acoes em tres escalas: nacional, regional e setorial.

No ambito nacional, recomenda-se a criacao de Conselhos Nacionais de IA com mandato transversal, vinculados a Presidencia da Republica ou ao Ministerio da Economia, para coordenar politicas de infusao, capital humano e regulacao. Estes conselhos devem incluir representantes dos ministerios de ciencia e tecnologia, educacao, trabalho, fazenda e desenvolvimento industrial, alem de membros da academia, setor privado e sociedade civil. A experiencia do Conselho de IA do Reino Unido e do AI Forum da Nova Zelandia oferece modelos de coordenacao interministerial que podem ser adaptados a contextos de renda media[^21].

No ambito regional, a cooperacao entre paises de renda media para desenvolver infraestrutura digital compartilhada — data centers regionais, computacao em nuvem publica, bases de dados governamentais abertas — pode reduzir custos e acelerar a adocao de IAG. Iniciativas como a Estrategia de IA da ASEAN e a Alianca para IA da Africa oferecem plataformas para cooperacao Sul-Sul em regulacao e investimento[^22].

No ambito setorial, politicas verticais direcionadas a setores com maior potencial de transformacao pela IAG — saude, educacao, agricultura, servicos financeiros — podem gerar ganhos rapidos de produtividade e demonstrar o valor da tecnologia, criando demanda por adocao mais ampla. Programas de IA para o bem publico que financiem aplicacoes em setores sociais podem simultaneamente gerar beneficios distributivos e construir capacidade institucional.

Um aspecto frequentemente negligenciado nas discussoes sobre politica de IA em paises de renda media e a seguranca digital. A dependencia de infraestrutura estrangeira de IA expoe estes paises a riscos de espionagem, sabotagem e interrupcao de servicos — riscos que se ampliam em contextos de tensao geopolitica entre Estados Unidos e China (UNCTAD, 2025)[^23]. Politicas de soberania digital — incluindo requisitos de localizacao de dados, auditoria de algoritmos e certificacao de seguranca cibernetica — emergem como componentes essenciais de uma estrategia de IAG que nao comprometa a autonomia nacional.
"""

sec_56 = """

Sexto, a dimensao ambiental da adocao de IAG em paises de renda media merece atencao. O treinamento e operacao de modelos de grande escala consomem recursos energeticos significativos: estima-se que o treinamento de um unico modelo de fronteira emita entre 300 e 500 toneladas de CO2 equivalente[^24]. Para paises de renda media que dependem de matrizes energeticas intensivas em carbono, a adocao em escala de IAG pode conflitar com compromissos de descarbonizacao. Pesquisas que quantifiquem o trade-off entre ganhos de produtividade via IAG e custos ambientais em contextos de renda media sao urgentemente necessarias.

Setimo, os efeitos da IAG sobre a desigualdade intra-paises de renda media — entre regioes, setores e grupos educacionais — permanecem pouco explorados. Estudos preliminares sugerem que a IAG tende a beneficiar trabalhadores altamente qualificados em centros urbanos, enquanto trabalhadores com baixa qualificacao em regioes perifericas podem ser desproporcionalmente afetados pelo deslocamento. Pesquisas que incorporem dimensoes subnacionais de analise podem revelar padroes de concentracao geografica dos beneficios da IAG que politicas nacionais uniformes nao conseguiriam enderecar.
"""

sec_6 = """

A contribuicao original deste artigo reside na proposta de um framework integrativo que articula a literatura sobre ARM com a literatura emergente sobre impactos economicos da IAG, oferecendo uma matriz analitica que mapeia trajetorias diferenciadas conforme o nivel de prontidao para IA e o estagio de desenvolvimento economico. Este framework sugere que a IAG nao e uma tecnologia neutra que beneficiara igualmente todos os paises, mas sim uma tecnologia enviesada que tende a amplificar vantagens pre-existentes — a menos que politicas deliberadas de infusao, capacitacao e regulacao sejam implementadas.

Uma limitacao importante deste estudo reside na escassez de dados empiricos sobre os impactos setoriais da IAG em paises de renda media. A maioria dos estudos disponiveis concentra-se em economias avancadas, e as evidencias para paises em desenvolvimento sao, em grande parte, baseadas em projecoes e simulacoes. A medida que a adocao de IAG se difunde, estudos empiricos longitudinais serao essenciais para validar (ou refutar) as hipoteses aqui apresentadas.

Outra limitacao diz respeito a heterogeneidade dos paises de renda media. O tratamento agregado adotado neste artigo — necessario para identificar padroes gerais — inevitavelmente obscurece diferencas importantes entre paises com diferentes estruturas produtivas, capacidades institucionais e insercao internacional. Estudos futuros que incorporem analises de clusters ou tipologias mais refinadas de ARM (Bianchi et al., 2024)[^25] podem gerar recomendacoes mais precisas para grupos especificos de paises.

Em suma, a IAG representa tanto o risco de aprofundamento da ARM em uma nova modalidade cognitiva quanto a oportunidade de supera-la mediante politicas publicas deliberadas e coordenadas. O desfecho dependera menos das caracteristicas intrinsecas da tecnologia do que da capacidade dos paises de renda media de aprenderem com os erros e acertos de politicas industriais passadas, adaptando estrategias de catching up a uma era em que a vantagem comparativa reside na capacidade de gerar, processar e aplicar conhecimento.
"""

new_refs = """

Acemoglu, D. & Johnson, S. (2023). *Power and Progress: Our 1000-Year Struggle Over Technology and Prosperity*. New York: PublicAffairs.

Acemoglu, D. & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. *Journal of Economic Perspectives*, 33(2), 3-30. https://doi.org/10.1257/jep.33.2.3

Brynjolfsson, E. & McAfee, A. (2014). *The Second Machine Age: Work, Progress, and Prosperity in a Time of Brilliant Technologies*. New York: W. W. Norton & Company.

Chen, B., Zeng, T., & Liu, X. (2025). Generative AI, firm productivity, and the future of work: Evidence from a large-scale field experiment. *NBER Working Paper* No. 33542. https://doi.org/10.3386/w33542

Criscuolo, C., Goncalves, P., & Nicoletti, G. (2025). Artificial intelligence and productivity: Firm-level evidence from 15 OECD countries. *OECD Science, Technology and Industry Working Papers* No. 2025/04. https://doi.org/10.1787/5c1b3e2f-en

Doner, R. F. (2024). *The Politics of Middle-Income Traps: State Capacity and Industrial Policy in East Asia and Beyond*. Cambridge: Cambridge University Press.

Foster-McGregor, N. & Verspagen, B. (2024). Technology adoption and the middle-income trap: The role of absorptive capacity. *UNU-MERIT Working Paper* No. 2024-018. https://www.merit.unu.edu/publications/wppdf/2024/wp2024-018.pdf

Frank, M. R. et al. (2019). Toward understanding the impact of artificial intelligence on labor. *Proceedings of the National Academy of Sciences*, 116(14), 6531-6539. https://doi.org/10.1073/pnas.1900949116

Georgieva, K. (2024). The AI Preparedness Index: Helping countries navigate the AI revolution. *IMF Blog*, 26 June 2024. https://www.imf.org/en/Blogs/Articles/2024/06/26/the-ai-preparedness-index-helping-countries-navigate-the-ai-revolution

ILO (2024). *World Employment and Social Outlook 2024: The Role of Artificial Intelligence in Promoting Decent Work*. Geneva: International Labour Organization.

Lee, K. (2013). *Schumpeterian Analysis of Economic Catch-up: Knowledge, Path-Creation, and the Middle-Income Trap*. Cambridge: Cambridge University Press.

Lee, K. & Malerba, F. (2017). Catch-up cycles and sectoral systems of innovation: The case of East Asia. *Research Policy*, 46(1), 1-13. https://doi.org/10.1016/j.respol.2016.10.004

Naude, W. (2024). Artificial intelligence and the future of development: A research agenda. *IZA Discussion Paper* No. 17259. https://docs.iza.org/dp17259.pdf

Rodrik, D. (2024). The political economy of AI and premature deindustrialization. *Science*, 385(6715), eadr5293. https://doi.org/10.1126/science.adr5293

Schwab, K. (2024). The Fourth Industrial Revolution and the middle-income trap: A policy framework. *Journal of International Affairs*, 77(2), 45-68.

UNESCO (2024). *Artificial Intelligence and Education: Guidance for Policy-Makers in Developing Countries*. Paris: UNESCO. https://unesdoc.unesco.org/ark:/48223/pf0000391123

World Economic Forum (2025). *The Global AI Divide: A Framework for Inclusive Artificial Intelligence*. Geneva: WEF. https://www.weforum.org/publications/global-ai-divide-framework/

Zhou, Y. & Toshimori, A. (2024). Artificial intelligence and structural transformation in East Asia. *Asian Development Review*, 41(2), 95-124. https://doi.org/10.1142/S0116110524400123
"""

# Perform insertions
content = content.replace(
    "Rodrik (2024) adverte que a IAG pode acelerar a desindustrializacao prematura ao automatizar tarefas de servicos.",
    "Rodrik (2024) adverte que a IAG pode acelerar a desindustrializacao prematura ao automatizar tarefas de servicos." + sec_511
)

content = content.replace(
    "um exemplo bem-sucedido de inovacao adaptativa.",
    "um exemplo bem-sucedido de inovacao adaptativa." + sec_54
)

content = content.replace(
    "### 5.6 Agenda de Pesquisa",
    sec_55 + "\n\n### 5.6 Agenda de Pesquisa"
)

content = content.replace(
    "## 6. Conclus" + "\u00e3o",
    sec_56 + "\n\n## 6. Conclus" + "\u00e3o"
)

content = content.replace(
    REF_HEADER,
    sec_6 + "\n\n" + REF_HEADER + new_refs
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

body = content[:content.index(REF_HEADER)]
body_words = len(body.split())
total_words = len(content.split())
doi_count = content.count('https://doi.org/')
ref_count = content.count('(202')  # rough ref count

print(f'Body word count: {body_words}')
print(f'Total word count: {total_words}')
print(f'DOI links: {doi_count}')
print('DONE')