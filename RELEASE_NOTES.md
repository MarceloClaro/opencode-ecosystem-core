# Release Notes: OpenCode Ecosystem Core v1.0.0

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
