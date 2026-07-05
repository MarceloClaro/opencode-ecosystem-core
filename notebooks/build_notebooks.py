# -*- coding: utf-8 -*-
"""
build_notebooks.py — Gerador dos notebooks de demonstração end-to-end
=====================================================================
Gera notebooks Jupyter (.ipynb) documentados para os principais fluxos
do OpenCode Ecosystem Core. Executar a partir da raiz do repositório:

    python3 notebooks/build_notebooks.py
"""
import nbformat as nbf
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


SETUP = """import sys, os, logging
# Garante que a raiz do repositório está no path (notebook roda em notebooks/)
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')))
logging.basicConfig(level=logging.WARNING)
from marceloclaro.orchestrator import MarceloClaroOrchestrator
orch = MarceloClaroOrchestrator()
print('Orquestrador inicializado com', len(orch.list_agents()), 'agentes')"""


def build_01_getting_started():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md("""# 01 — Primeiros Passos com o Orquestrador `marceloclaro`

Este notebook demonstra o ciclo de vida básico do **OpenCode Ecosystem Core**: inicialização do orquestrador central, percepção do Global Workspace, delegação de tarefas via roteamento por atenção (Transformer), execução do pipeline Gerar→Verificar→Revisar e consulta ao estado do ecossistema.

**Requisitos:** Python 3.10+, apenas biblioteca padrão (stdlib). Nenhuma chave de API é necessária para este fluxo.

**Arquitetura envolvida:** MCI (Metacognitive Interconnect Layer), AttentionRouter, HierarchicalMemory, Trust Engine e Token Economy."""),
        code(SETUP),
        md("""## 1. Status do Ecossistema

O método `status()` retorna um retrato do Global Workspace: agentes registrados, tarefas ativas, saúde do Trust Engine e saldo da Token Economy."""),
        code("""status = orch.status()
for k, v in status.items():
    print(f'{k}: {v}')"""),
        md("""## 2. Percepção (Global Workspace Theory)

O orquestrador **percebe** o quadro-negro (blackboard) compartilhado, coletando os eventos mais salientes do workspace — análogo ao *broadcast* consciente da GWT de Baars."""),
        code("""percept = orch.perceive(topic='general_execution', limit=5)
print(percept)"""),
        md("""## 3. Roteamento por Atenção (explicabilidade)

Antes de delegar, podemos **auditar** a decisão de roteamento. O `explain_routing` expõe os scores softmax de cada cabeça de atenção (semântica, capacidade, confiança, carga) — transparência total, como exige o padrão Qualis A1 de auditabilidade."""),
        code("""explanation = orch.explain_routing('Escrever revisão de literatura sobre aprendizado quântico de máquina')
import json
print(json.dumps(explanation, indent=2, ensure_ascii=False, default=str)[:2000])"""),
        md("""## 4. Delegação de Tarefa

A delegação emite um CFP (Call For Proposals) no blackboard A2A. O AttentionRouter seleciona o agente vencedor e o Trust Engine valida o gate comportamental."""),
        code("""task = orch.delegate('Analisar requisitos de um artigo científico sobre redes neurais', required_capabilities=['research'])
print(task)"""),
        md("""## 5. Pipeline Gerar → Verificar → Revisar (Reflexion)

O pipeline iterativo aplica o padrão **Reflexion** (Shinn et al., 2023): o executor produz um artefato, o verificador critica, e o revisor refina até convergência."""),
        code("""def executor(prompt, feedback=None):
    base = f'Rascunho para: {prompt}'
    if feedback:
        base += f' [revisado com feedback: {feedback}]'
    return base

result = orch.run_pipeline('Resumo executivo do ecossistema', executor)
print(result)"""),
        md("""## 6. Memória Hierárquica (Recall)

A `HierarchicalMemory` armazena episódios em camadas (curto prazo → episódica → semântica) com *episodic replay*. O `recall` recupera as entradas mais relevantes."""),
        code("""memories = orch.recall('artigo científico', top_entries=3)
for m in memories:
    print(m)"""),
        md("""## Conclusão

Neste notebook você viu o núcleo do ecossistema: percepção, roteamento explicável, delegação com confiança, pipeline Reflexion e memória hierárquica. Prossiga para o notebook **02** para o pipeline acadêmico Qualis A1 completo."""),
    ]
    return nb


def build_02_academic_pipeline():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md("""# 02 — Pipeline Acadêmico Qualis A1 de Ponta a Ponta

Este notebook percorre o fluxo completo de **produção científica**: busca acadêmica multiplataforma (arXiv, OpenAlex, Crossref, Semantic Scholar), fichamento ABNT/APA, pipeline MASWOS de manuscrito, produção LaTeX modular e design automático de capa.

**Nota:** As buscas reais exigem conexão com a internet. Quando offline, os buscadores retornam resultados vazios sem erro (degradação graciosa)."""),
        code(SETUP),
        md("""## 1. Busca Acadêmica Multiplataforma

O `research_search` consulta múltiplas APIs abertas em paralelo e normaliza os metadados (título, autores, ano, DOI, resumo)."""),
        code("""results = orch.research_search('quantum machine learning', platforms=['arxiv'], limit_per_platform=3)
for r in results[:3]:
    print('-', str(r)[:160])"""),
        md("""## 2. Pesquisa Completa com Fichamentos

O método `research` executa o funil completo: busca → download de PDFs → conversão PDF→Markdown → fichamento ABNT/APA — gravando tudo numa pasta de produção auditável."""),
        code("""import tempfile
prod = tempfile.mkdtemp(prefix='producao_')
research = orch.research('transformer attention mechanisms', production_folder=prod, max_papers=2)
print('Pasta de produção:', prod)
print(str(research)[:800])"""),
        md("""## 3. Pipeline MASWOS (Manuscrito Qualis A1)

O MASWOS orquestra agentes especializados (revisor de literatura, metodólogo, estatístico, auditor ABNT) num ciclo Delphi até o manuscrito atingir o gate de qualidade."""),
        code("""manuscript = orch.academic_pipeline(
    topic='Ruído quântico benéfico em classificadores variacionais',
    manuscript='Rascunho inicial: o ruído pode atuar como regularizador implícito em VQCs.'
)
print(str(manuscript)[:1200])"""),
        md("""## 4. Produção Científica LaTeX Modular

O `produce_scientific_work` gera a árvore LaTeX com um `.tex` por seção/capítulo, `main.tex` agregador, e metadados de compilação para PDF/DOCX/ODT (compatível com Amazon KDP)."""),
        code("""work = orch.produce_scientific_work(
    title='Beneficial Quantum Noise in Variational Classifiers',
    content='# Introducao\\nO ruido quantico pode ser benefico.\\n# Metodologia\\nSimulacao com statevector.\\n# Resultados\\nAcuracia media de 89%.',
    template='artigo',
)
print(str(work)[:800])"""),
        md("""## 5. Capa e Contracapa Automáticas

O `cover_designer` estuda paleta de cores e tipografia adequadas ao tema, e gera prompts de ilustração para capa, contracapa e lombada."""),
        code("""from publishing.cover_designer import CoverDesigner
designer = CoverDesigner(output_dir=prod)
design = designer.design_cover(
    title='Beneficial Quantum Noise',
    author='Prof. Marcelo Claro',
    content_sample='ruido quantico, classificadores variacionais, aprendizado de maquina quantico',
    subtitle='Variational Classifiers',
)
print(str(design)[:1000])"""),
        md("""## Conclusão

O fluxo demonstrado cobre da busca bibliográfica à arte de capa, com auditabilidade em cada etapa (pasta de produção, fichamentos, specs SDD). No notebook **03** exploramos o enxame MiroFish e a Teoria dos Jogos."""),
    ]
    return nb


def build_03_swarm_gametheory():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md("""# 03 — MiroFish Swarm, Teoria dos Jogos e Diagnóstico Profundo

Este notebook demonstra os subsistemas de **inteligência coletiva**: predição por enxame (MiroFish), validação por consenso Delphi com GraphMemory, análise estratégica via Teoria dos Jogos (Nash, Shapley) e o Deep Diagnose (M1–M5)."""),
        code(SETUP),
        md("""## 1. Predição por Enxame (MiroFish)

O enxame agrega sinais de múltiplos agentes-peixe com dinâmica de cardume, produzindo uma predição coletiva com intervalo de confiança."""),
        code("""prediction = orch.swarm_predict('A adoção de agentes autônomos crescerá em 2026?', signal=0.72)
print(prediction)"""),
        md("""## 2. Validação por Consenso (Delphi + GraphMemory)

O `swarm_validate` conduz um debate Delphi entre os agentes e registra os argumentos num grafo de conhecimento consultável."""),
        code("""validation = orch.swarm_validate('O TDD melhora a qualidade de sistemas multiagentes?', signal=0.8)
print(str(validation)[:900])"""),
        md("""## 3. Meta-Raciocínio (38 Tipos de Raciocínio)

O `meta_reason` seleciona e combina os tipos de raciocínio mais adequados ao tópico (dedutivo, abdutivo, contrafactual, bayesiano, etc.)."""),
        code("""meta = orch.meta_reason('Como garantir reprodutibilidade em pesquisa com LLMs?')
print(str(meta)[:900])"""),
        md("""## 4. Teoria dos Jogos — Equilíbrio de Nash

Análise estratégica de interações entre agentes: dilema do prisioneiro, valor de Shapley para atribuição de crédito, e Tit-for-Tat para cooperação iterada."""),
        code("""nash = orch.nash_analysis(game='prisoners_dilemma')
print(nash)"""),
        md("""## 5. Motores de Raciocínio Formal

O subsistema `reasoning` integra Z3 (SAT/SMT), SymPy (álgebra simbólica) e Kanren (lógica relacional), com fallback crítico em stdlib puro."""),
        code("""result = orch.reason('2*x + 4 = 10', engine='auto')
print(result)"""),
        md("""## 6. Experimento Quântico (Statevector Simulator)

Simulador de vetor de estado em stdlib puro — sem dependências pesadas — para experimentos didáticos com portas H, CNOT e medição."""),
        code("""quantum = orch.quantum_experiment(n_qubits=3)
print(str(quantum)[:700])"""),
        md("""## 7. Diagnóstico Profundo (Deep Diagnose M1–M5)

O pipeline de scanners executa engenharia reversa epistemológica sobre um corpus: varredura noológica, teleológica, priorização epistêmica e geração de sucessores."""),
        code("""corpus = 'Sistema multiagente com roteamento estatico apresenta gargalos de escalabilidade e ausencia de gates de qualidade.'
diagnosis = orch.diagnose(corpus, domain='software architecture', deep=True)
print(str(diagnosis)[:1200])"""),
        md("""## Conclusão

Você explorou os subsistemas de inteligência coletiva e diagnóstico do ecossistema. Combine estes fluxos com o pipeline acadêmico (notebook 02) para produção científica validada por enxame — o diferencial de maturidade ⭐⭐⭐⭐⭐ do Core."""),
    ]
    return nb


def main():
    builders = {
        '01_getting_started.ipynb': build_01_getting_started,
        '02_academic_pipeline.ipynb': build_02_academic_pipeline,
        '03_swarm_gametheory_diagnose.ipynb': build_03_swarm_gametheory,
    }
    for name, builder in builders.items():
        nb = builder()
        nb.metadata['kernelspec'] = {
            'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
        nb.metadata['language_info'] = {'name': 'python', 'version': '3.10'}
        path = os.path.join(HERE, name)
        with open(path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        print('Gerado:', path)


if __name__ == '__main__':
    main()
