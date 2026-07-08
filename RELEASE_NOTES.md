# Release Notes: OpenCode Ecosystem Core

## v2.3.0 — Legal Intelligence & Transversal MetaBus Expansion

Esta versão transforma o subsistema jurídico em uma camada estratégica do ecossistema e estabelece a **orquestração transversal** de todos os subsistemas via **MetaBus**. O OpenCode agora combina **raciocínio jurídico brasileiro**, **Datajud**, **AUXJURIS**, **scanner jurídico de impacto**, **especialização por 7 ramos do direito**, **bases de conhecimento segmentadas por domínio**, **benchmarks jurídicos conservadores por domínio**, **aba jurídica dedicada na webapp** e **sincronização universal de eventos entre OQS, VSEE, EGS, RAG, Superhuman Suite, MiroFish, Game Theory, Publishing, Research e SDD**.

### Destaques

1. **Core Jurídico (`legal/`)**
   - Subsunção, ponderação, precedentes, interpretação constitucional e scoring.
   - Integração com dados processuais reais da API pública Datajud do CNJ.
   - Knowledge base com RAG por keywords e sumarização jurídica.

2. **AUXJURIS integrado ao MCI**
   - 4 agentes jurídicos A2A.
   - Base de conhecimento jurídica integrada ao Blackboard/MetaBus.
   - Roteamento jurídico explicável e agente especialista sugerido por ramo.

3. **Legal Impact Scanner (`scanners/legal_impact_scanner.py`)**
   - Avalia LGPD, licenciamento, compliance, grounding jurisprudencial, responsabilidade contratual e defensibilidade de publicação.
   - Mede `compliance_awareness`, `normative_conflict_detection`, `risk_anticipation` e `epistemic_humility_legal`.

4. **Especialização por ramo + benchmarks (`SPEC-927/928`)**
   - 7 ramos: penal, trabalhista, tributário, empresarial, administrativo, ambiental e digital/LGPD.
   - Benchmarks por ramo com tiers conservadores:
     `base` → `specialist` → `specialist_advanced` → `phd_candidate` → `phd_validated`.
   - `phd_validated` exige validação externa explícita.

5. **Knowledge Bases Segmentadas por Ramo (`SPEC-931`)**
   - Base de conhecimento segmentada nos 7 ramos com estatutos, princípios, keywords, issues comuns e vetores de risco.
   - Roteamento automático por domínio e seleção manual na webapp.

6. **Webapp Jurídica com KB Integration (`SPEC-932`)**
   - Aba `⚖️ Jurídico` exibe base ativa, switch manual de ramo, preview de conteúdo e score de impacto.
   - Gatilho para refinamento via MetaBus.

7. **Refinamento Jurídico via MetaBus (`SPEC-933`)**
   - Ciclo contínuo: busca → recuperação → síntese → atualização de confiança.

8. **MetaBus — Orquestração Transversal (`SPEC-934`)**
   - OQS, VSEE, EGS, Scientific RAG, Superhuman Suite, MiroFish, Game Theory, Publishing, Research e SDD publicam eventos no MetaBus.
   - MetaBus com `publish_subsystem_event`, `search_memory`, `update_topic_confidence`, `upser_semantic_topic`.
   - Rastreabilidade completa de ciclos evolutivos (R56–R67).

### Validação

```bash
pytest tests -q
# 363 passed, 2 skipped
```

### Como usar

```bash
streamlit run webapp/app.py
```

Na aba `⚖️ Jurídico`, forneça o corpus e os campos de análise para obter:

- score jurídico
- ganho metacognitivo jurídico
- readiness
- flags de alto risco
- ramo jurídico provável
- base de conhecimento ativa
- agente especialista sugerido

## v2.2.0 — Metacognitive Superhuman Refinement

Esta versão adiciona a **Metacognitive Superhuman Refinement Suite (SPEC-920)**, uma régua conservadora para avaliar se o ecossistema está apenas executando tarefas ou melhorando sua própria forma de decidir.

### Destaques

1. **Metacognitive Evaluator (`mci/metacognitive_evaluator.py`)**
   - `MetacognitiveTrace` para representar ações, outcomes, confiança, estratégia, evidência e abstenção.
   - `MetacognitiveEvaluator` para calcular maturidade metacognitiva.
   - `MetacognitiveBenchmarkSuite` com casos determinísticos de benchmark.

2. **Dimensões avaliadas**
   - awareness;
   - reflection;
   - adaptation;
   - memory_quality;
   - error_causality;
   - epistemic_humility.

3. **Política anti-overclaim metacognitiva**
   - `metacognitive_superhuman_verified` só é retornado com `external_validation=True`.
   - Sem validação externa, o máximo permitido é `metacognitive_superhuman_candidate`.

### Validação

```bash
pytest tests/test_metacognitive_superhuman.py -q
# 8 passed

pytest tests -q
# 263 passed, 2 skipped, 1 warning
```

---

## v2.1.0 — Scientific RAG + SuperHuman Readiness

Esta versão eleva o núcleo científico do ecossistema com **RAG científico auditável** e uma régua conservadora de **readiness superhuman**. O objetivo é medir progresso rumo a raciocínio científico superhuman sem claims exagerados: `superhuman_verified` só é permitido com validação externa explícita.

### Destaques

1. **Scientific RAG (`rag/`)**
   - Indexação de documentos científicos com metadados.
   - Chunking citável e recuperação top-k.
   - Busca híbrida lexical + semantic-lite.
   - Reranking científico com bônus para método, evidência direta e metadados.
   - Citações auditáveis no formato `Autor (Ano), doc_id#chunk`.
   - Abstenção quando não há evidência suficiente.

2. **Grounding Evaluator**
   - Métricas `groundedness`, `citation_coverage`, `evidence_count` e `abstention`.
   - Política epistêmica: é melhor não responder do que inventar evidência.

3. **Scientific Superhuman Benchmark Suite**
   - Novo `readiness_score` (0–100).
   - Tiers: `base`, `research_grade`, `superhuman_candidate`, `superhuman_verified`.
   - `superhuman_verified` requer `external_validation=True`.
   - Integra benchmarks científicos, RAG, robustez, calibração e reprodutibilidade.

4. **Benchmarks mais rigorosos**
   - Os 5 benchmarks científicos existentes agora avaliam `pipeline_fn` quando fornecido.
   - Pipelines que respondem errado não passam automaticamente.

### Validação

```bash
pytest tests/test_scientific_rag_superhuman.py -q
# 8 passed

pytest tests -q
# 255 passed, 2 skipped, 1 warning
```

### Como usar

```python
from rag import ScientificDocument, ScientificRAG
from benchmarks.scientific_reasoning import run_superhuman_suite

rag = ScientificRAG(min_score=0.05)
rag.index([
    ScientificDocument(
        doc_id="pearl-2009",
        title="Causality",
        authors=["Pearl"],
        year=2009,
        source="book",
        text="Correlação não implica causalidade; inferência causal exige modelo estrutural.",
    )
])

print(rag.answer("como distinguir correlação de causalidade?"))
print(run_superhuman_suite(rag=rag, external_validation=False)["tier"])
```

---

## v1.0.0

É com imenso orgulho que anunciamos a versão **1.0.0** do **OpenCode Ecosystem Core**, o núcleo metacognitivo para orquestração de 134 agentes especializados com foco em produção científica de alto rigor (Qualis A1) e diagnóstico profundo de sistemas complexos.

## Destaques desta Versão

### 1. Interface Web Interativa (Streamlit)
O orquestrador `marceloclaro` agora possui um painel de controle visual completo. Com 6 abas funcionais, você pode monitorar o Global Workspace, delegar tarefas com roteamento explicável, executar o pipeline de pesquisa acadêmica, simular o enxame MiroFish, e rodar diagnósticos profundos ou experimentos quânticos com apenas alguns cliques.

### 2. Suporte Nativo a Modelos Locais (Ollama)
A privacidade na pesquisa acadêmica é fundamental. Agora, o enriquecimento de fichamentos e resenhas críticas pode ser feito de forma 100% local, utilizando o Ollama. Modelos como `llama3.2` ou `qwen2.5` processam os textos integralmente na sua máquina, garantindo custo zero e proteção de dados sensíveis. A integração detecta automaticamente a presença do servidor local e possui fallback gracioso.

### 3. Notebooks End-to-End
A curva de aprendizado foi drasticamente reduzida com a inclusão de 3 notebooks Jupyter interativos e documentados na pasta `notebooks/`. Eles cobrem desde os primeiros passos (roteamento, memória, Reflexion) até o pipeline Qualis A1 completo e algoritmos avançados (Teoria dos Jogos, Simulador Quântico).

### 4. Transparência e Maturidade
O `README.md` foi atualizado com uma tabela comparativa de maturidade exaustiva. O OpenCode Ecosystem Core foi contrastado em 7 dimensões arquiteturais contra frameworks de mercado como Microsoft AutoGen, MetaGPT, Superhuman, LangGraph, CrewAI e OpenDevin, demonstrando sua superioridade em metacognição, QA (SDD/TDD) e produção científica.

## Como Atualizar

```bash
git pull origin main
pip install -r requirements.txt
pip install streamlit jupyter
```

Para rodar a nova interface web:
```bash
streamlit run webapp/app.py
```

Agradecemos o apoio contínuo. Explore o código, teste os notebooks e continue elevando o padrão da pesquisa automatizada!
