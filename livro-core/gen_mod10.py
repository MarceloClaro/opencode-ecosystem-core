#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do Módulo 10 — Catálogo Completo de Agentes e Subagentes.
Lê opencode.json + agents/catalog/*.md e produz mod-10-catalogo.tex
com uma ficha (elemento) por agente, agrupado por categoria.

Uso:  python3 gen_mod10.py   (a partir de livro-core/ ou de raiz do repo)
"""
import json, glob, os, re, sys

ROOT = os.environ.get("CORE_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
OUT = os.path.join(os.path.dirname(__file__), "mod-10-catalogo.tex")


def esc(t):
    if t is None:
        return ""
    t = str(t)
    t = t.replace("\\", r"\textbackslash{}")
    t = t.replace("{", r"\{").replace("}", r"\}")
    t = t.replace("#", r"\#").replace("&", r"\&")
    t = t.replace("$", r"\$").replace("%", r"\%").replace("_", r"\_")
    t = t.replace("^", r"\^{}").replace("~", r"\~{}")
    return t


def limpar_texto(t):
    """Remove sintaxe de Markdown e pictogramas que pdfLaTeX não compõe."""
    t = str(t or "")
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\*\*(.*?)\*\*|__(.*?)__", lambda m: m.group(1) or m.group(2), t)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"(?<!\w)\*(?!\s)|(?<!\w)_(?!\s)|(?<!\s)\*(?!\w)|(?<!\s)_(?!\w)", "", t)
    t = re.sub(r"[|]+", "; ", t)
    t = re.sub(r"[\u2500-\u27FF\U0001F000-\U0001FAFF]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    # Tolerante a cabecalho de comentario HTML antes da cerca de frontmatter
    # (padrao dos cards de agents/catalog/*.md). Sem re.M o ^ ancorava apenas
    # no inicio do arquivo e 40 cards eram silenciosamente descartados.
    block = re.search(r"^---[ \t]*\n(.*?)\n---[ \t]*$", txt, re.S | re.M)
    if not block:
        return {}
    data = {}
    for m in re.finditer(r"^([A-Za-z_][\w-]*):[ \t]*(.+)$", block.group(1), re.M):
        data[m.group(1)] = m.group(2).strip().strip("'\"")
    # Descrições YAML dobradas (description: >-) ocupam várias linhas. A
    # leitura linha a linha anterior imprimia somente o marcador `>` no livro.
    fm_lines = block.group(1).splitlines()
    for i, line in enumerate(fm_lines):
        match = re.match(r"^description:[ \t]*[>|][+-]?[ \t]*$", line)
        if not match:
            continue
        folded = []
        for continuation in fm_lines[i + 1:]:
            if continuation.strip() and not continuation[:1].isspace():
                break
            if continuation.strip():
                folded.append(continuation.strip())
        data["description"] = " ".join(folded)
        break
    return data


def detalhes_ficha(path):
    """Recupera descrição substantiva de todas as seções YAML e do corpo."""
    txt = open(path, encoding="utf-8").read()
    lines = txt.splitlines()
    blocks, start, inside = [], None, False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not inside:
                start, inside = i + 1, True
            else:
                blocks.append((start, i))
                inside = False

    descriptions = []
    skills = []
    for a, b in blocks:
        block = lines[a:b]
        for i, line in enumerate(block):
            stripped = line.lstrip()
            if stripped.startswith("description:"):
                value = stripped.split(":", 1)[1].strip().strip(chr(34)).strip(chr(39))
                if value in (">", ">-", "|", "|-"):
                    continuation = []
                    for follow in block[i + 1:]:
                        if follow.strip() and not follow[:1].isspace():
                            break
                        if follow.strip():
                            continuation.append(follow.strip())
                    value = " ".join(continuation)
                if value:
                    if line.startswith("description:"):
                        descriptions.append(value)
                    else:
                        skills.append(value)
            elif stripped.startswith("name:") and line.startswith(" "):
                skills.append(stripped.split(":", 1)[1].strip().strip(chr(34)).strip(chr(39)))

    body_start = blocks[-1][1] + 1 if blocks else 0
    body = []
    for line in lines[body_start:]:
        if line.strip().startswith("<!--") or line.strip().startswith("```"):
            continue
        if line.lstrip().startswith("#"):
            continue
        line = line.lstrip().removeprefix("> ").strip()
        if line:
            body.append(line)
        if sum(len(x) for x in body) >= 950:
            break
    body_text = " ".join(body)
    body_text = re.sub(r"\s+", " ", body_text).strip()

    boilerplate = re.compile(
        r"^(agente especializado|specialized agent|agent especializado|"
        r"executa tarefas especializadas|capacidade especializada em)\b", re.I
    )
    useful = [d for d in descriptions if not boilerplate.search(d.strip())]
    description = max(useful or descriptions, key=len, default="")
    if (not description or len(description.split()) < 9 or boilerplate.search(description)) and len(body_text.split()) >= 9:
        description = body_text
    elif description and len(description.split()) < 16 and skills:
        specific = [s for s in skills if len(s.split()) >= 6 and not boilerplate.search(s)]
        if specific:
            description = description.rstrip(". ") + ". Capacidades descritas: " + "; ".join(specific[:2])
    return limpar_texto(description)[:720]


PT_CATEGORY = {
    "orchestration": "Orquestração", "academic": "Produção acadêmica",
    "research": "Pesquisa e evidências", "audit": "Auditoria e qualidade",
    "legal": "Apoio jurídico", "data": "Dados e proveniência",
    "inference": "Inferência e modelagem", "engineering": "Engenharia",
    "testing": "Testes", "literary": "Escrita e tradução",
    "ferramental": "Ferramentas e apoio transversal",
    "curation-agent": "Curadoria", "integration": "Integrações",
    "mira-agent": "Apresentações MIRA", "maswos-agent": "Fluxos MASWOS",
}

PT_CATEGORY_INTRO = {
    "orchestration": "Agrupa perfis ligados à coordenação, divisão e acompanhamento de tarefas. No Core, suas contribuições se relacionam à orquestração e ao Blackboard (Módulo 2).",
    "academic": "Reúne etapas especializadas da escrita acadêmica. Os perfis podem apoiar partes do fluxo MASWOS, da delimitação do problema à revisão editorial; citações e resultados continuam sujeitos a conferência (Módulo 6).",
    "research": "Agrupa perfis de busca, recuperação e síntese de evidências. No Core, suas fontes alimentam a análise e a escrita científica e devem permanecer rastreáveis (Módulo 6).",
    "audit": "Reúne perfis de inspeção e revisão. Seus achados podem informar verificações de qualidade e rigor, mas a existência de um auditor não equivale a aprovação independente (Módulos 4 e 6).",
    "legal": "Agrupa perfis de apoio a documentos, pesquisa e organização jurídica. No Core, podem estruturar informações e apontar questões para revisão humana; não substituem julgamento profissional.",
    "data": "Reúne perfis voltados a dados. No Core, podem apoiar preparação, análise e registro de proveniência antes que os resultados alimentem pesquisa ou decisão (Módulo 6).",
    "inference": "Contém perfis de inferência e modelagem. Suas contribuições se relacionam aos métodos de raciocínio do Core e precisam expor premissas e limites (Módulo 5).",
    "engineering": "Agrupa perfis que apoiam análise, implementação e manutenção de software. No Core, o trabalho deve ser ligado a especificações e verificações quando aplicável (Módulos 1 e 4).",
    "testing": "Reúne perfis orientados a testes. No Core, podem converter critérios em verificações e produzir evidência para o fluxo de qualidade; aprovação depende dos critérios e resultados observados (Módulo 4).",
    "literary": "Agrupa perfis de escrita, edição e tradução. No Core, apoiam tarefas de produção textual; fontes, terminologia e decisões editoriais devem ser conferidas segundo o objetivo do trabalho.",
    "ferramental": "Categoria transversal com perfis variados de repositório, documentação, automação e suporte. Leia a descrição individual para saber a tarefa específica; não presuma que todos executem a mesma função.",
    "curation-agent": "Agrupa perfis de curadoria de catálogos e paisagens de agentes. No Core, ajudam a organizar e comparar registros, sem que isso implique instalar ou ativar os agentes listados.",
    "integration": "Reúne perfis de conexão com serviços e executores externos. No Core, suas tarefas pertencem à camada de integração; disponibilidade depende de configuração, serviço e credenciais (Módulo 7).",
    "mira-agent": "Agrupa perfis de apresentação e apoio visual MIRA. No Core, podem contribuir para estruturar conteúdo e elementos visuais; a saída ainda exige revisão editorial e visual.",
    "maswos-agent": "Reúne perfis associados a etapas do MASWOS. No Core, cada perfil pode apoiar uma fase definida da escrita científica, mantendo referências, critérios e revisão explícitos (Módulo 6).",
}

PT_APLICACAO = {
    "orchestration": "Trilha de orquestração: pode contribuir para decompor, encaminhar ou acompanhar uma tarefa; a decisão de rota e a chamada precisam ser confirmadas no fluxo usado.",
    "academic": "Trilha acadêmica/MASWOS: pode apoiar a etapa de escrita indicada na descrição; fontes e afirmações devem ser verificadas antes de compor a versão final.",
    "research": "Trilha de pesquisa: pode apoiar busca ou síntese de evidências; registre fontes e confira se cada uma sustenta a afirmação associada.",
    "audit": "Trilha de auditoria: pode localizar problemas segundo os critérios descritos; achados são subsídios à revisão, não certificação automática.",
    "legal": "Trilha de apoio jurídico: pode organizar documentos e questões para revisão humana, com atenção à jurisdição e à data das fontes.",
    "data": "Trilha de dados: pode apoiar preparação ou análise; registre origem, transformação, método e limitações dos dados usados.",
    "inference": "Trilha de raciocínio: pode apoiar análise ou modelagem; explicite premissas e verifique as saídas com método adequado.",
    "engineering": "Trilha de engenharia: pode apoiar a mudança de software descrita; conecte o trabalho aos requisitos, à implementação e às verificações pertinentes.",
    "testing": "Trilha de qualidade: pode apoiar a elaboração ou execução de testes; relacione cada resultado ao critério que ele realmente avalia.",
    "literary": "Trilha de escrita e tradução: pode apoiar a produção textual descrita; preserve o sentido, as fontes e a revisão editorial necessária.",
    "ferramental": "Trilha de apoio transversal: pode contribuir para a tarefa específica descrita; o operador confere permissões, saída e integração com o fluxo principal.",
    "curation-agent": "Trilha de curadoria: pode organizar metadados e comparações de perfis; alterações no catálogo e sua disponibilidade exigem validação própria.",
    "integration": "Trilha de integração: pode apoiar a operação externa descrita; confirme conexão, credenciais, permissões e resposta do serviço.",
    "mira-agent": "Trilha de apresentações MIRA: pode apoiar a organização visual descrita; confira conteúdo, legibilidade e consistência do material produzido.",
    "maswos-agent": "Trilha MASWOS: pode apoiar a fase especializada indicada; a entrega segue para integração editorial e conferência das fontes.",
}

PT_TITLES = {
    "scientific-capabilities-audit": "Auditor de capacidades científicas",
    "simulation-game-audit": "Auditor de simulações e teoria dos jogos",
    "book-mcp": "Consulta de livros por MCP",
    "book-finetuning": "Preparação de livros para ajuste fino",
    "library-architecture": "Arquitetura da biblioteca",
    "hooks-integration": "Integração de hooks",
    "mcp-cli-integration": "Integração de MCP e CLI",
    "live-mirofish-hermes": "Execução externa de MiroFish e Hermes",
    "gemini-notebook-audit": "Auditor de evidências do Gemini Notebook",
    "gemini-notebook-upstream": "Auditor das fontes e contratos do Gemini Notebook",
    "gemini-notebook-transport": "Especialista em transporte do Gemini Notebook",
    "architect": "Arquiteto de software",
    "reversa-architect": "Arquiteto de software Reversa",
    "literary-narratology-architect-phd": "Arquiteto de narratologia literária",
    "adr-manager": "Gestor de decisões arquiteturais",
    "architecture-analyzer": "Analisador de arquitetura de software",
    "batch-executor": "Executor de tarefas em lote",
    "build-agent": "Agente de compilação e validação",
    "codebase-analyzer": "Analisador de código-fonte",
    "codebase-locator": "Localizador de arquivos e componentes",
    "codebase-pattern-finder": "Localizador de padrões no código",
    "context-manager": "Gestor de contexto do projeto",
    "context-retriever": "Recuperador de contexto do repositório",
    "contextscout": "Explorador de arquivos de contexto",
    "contract-manager": "Gestor de contratos de API",
    "copywriter": "Redator publicitário",
    "devops-specialist": "Especialista em DevOps",
    "eval-runner": "Executor do ambiente de avaliação",
    "externalscout": "Pesquisador de documentação externa",
    "frontend-specialist": "Especialista em interfaces front-end",
    "image-specialist": "Especialista em imagens",
    "landscape-curator": "Curador da paisagem de agentes",
    "openagent": "Agente geral OpenAgent",
    "opencoder": "Agente de programação OpenCoder",
    "prioritization-engine": "Mecanismo de priorização",
    "reviewer": "Revisor de código e segurança",
    "simple-responder": "Agente de resposta simples para avaliação",
    "stage-orchestrator": "Orquestrador de etapas",
    "story-mapper": "Mapeador de jornadas e histórias",
    "task-manager": "Gestor de tarefas de desenvolvimento",
    "technical-writer": "Redator técnico",
    "thoughts-analyzer": "Analista de documentos de pesquisa",
    "thoughts-locator": "Localizador de documentos de pesquisa",
    "web-search-researcher": "Pesquisador por busca na web",
    "ws-coder": "Agente de implementação de código",
    "ws-researcher": "Arquiteto de pesquisa e documentação",
    "ws-reviewer": "Revisor técnico de código",
    "ws-scribe": "Redator de documentação",
    "documentation": "Especialista em documentação",
    "test-engineer": "Engenheiro de testes",
    "web-developer": "Desenvolvedor de aplicações web",
    "llm-reduction": "Especialista em redução de chamadas a modelos",
    "32_agente_etica_open_science": "Agente de ética e ciência aberta",
    "litert-lm-agent": "Agente de inferência local LiteRT-LM",
    "reversa-agent-forum": "Moderador de fórum e debates multiagente",
    "reversa-document-ir": "Pipeline de extração e análise de documentos",
    "reversa-report-agent": "Agente de elaboração de relatórios Reversa",
    "ws-academic-pipeline": "Fluxo de produção acadêmica WS",
    "auxjuris_document_summarizer": "Especialista em síntese de documentos jurídicos",
}

PT_DESCRIPTIONS = {
    "scientific-capabilities-audit": "Audita capacidades científicas e lacunas pelo orquestrador central. Verifica fontes, métodos, reprodução e revisão computacional, preservando o escopo da evidência e a necessidade de avaliação externa.",
    "simulation-game-audit": "Audita simulações e teoria dos jogos pelo orquestrador central. Confere matrizes, equilíbrios e cenários, distinguindo execução de um cenário sintético de observação social ou previsão validada.",
    "book-mcp": "Consulta livros locais pela biblioteca do Core e sua interface MCP. Preserva origem e hashes das passagens e mantém a leitura dos documentos separada da execução de instruções neles contidas.",
    "book-finetuning": "Prepara dados de livros para ajuste fino, com verificação de licença, origem, grupos e separação de conjuntos. A preparação dos dados não executa treinamento de modelo.",
    "library-architecture": "Verifica estrutura, índice, cobertura e recuperação da biblioteca. Encaminha alterações e tarefas ao orquestrador central e registra ausências sem tratá-las como capacidades já executadas.",
    "hooks-integration": "Verifica integração de hooks e contratos do SDK, com casos de falha e sucesso. A ativação de um evento não demonstra a conclusão da tarefa; a entrega exige resultado e evidência correspondente.",
    "mcp-cli-integration": "Verifica esquemas, argumentos, inicializadores e ferramentas de MCP e CLI. Diferencia descoberta, instalação, autenticação, processo iniciado e operação concluída, preservando os erros observados.",
    "live-mirofish-hermes": "Executa Hermes e MiroFish/OASIS externos pelo método central scientific_runtime_run. Exige processo externo, resposta do modelo com tokens e artefato do runtime. Registra commits, hashes e limites; a população simulada permanece sintética.",
    "gemini-notebook-audit": "Audita estados, evidências e proveniência do Gemini Notebook pelo orquestrador central. Confere autenticação, transporte, resultado da operação e arquivos, preservando pendências, resultados parciais e falhas sem promover confiança científica.",
    "gemini-notebook-upstream": "Compara o fork solicitado, a versão instalada, os esquemas e as definições oficiais dos pipelines. Registra divergências e hashes das fontes públicas sem trocar perfis, atualizar pacotes ou executar operações da conta durante a descoberta.",
    "gemini-notebook-transport": "Verifica os executores oficiais CLI e MCP, as sessões persistentes e a associação de tarefas à sessão original. Examina limites, encerramento e downloads com arquivos reais; operações da conta seguem pelas entradas centrais e exigem autorização correspondente.",
    "adr-manager": "Registra decisões arquiteturais em formato ADR, incluindo contexto, alternativas consideradas e consequências.",
    "architecture-analyzer": "Analisa arquitetura orientada a domínio e identifica contextos delimitados, fronteiras entre módulos e relações de domínio para fluxos em várias etapas.",
    "batch-executor": "Executa tarefas em lotes paralelos, coordena delegações simultâneas ao CoderAgent e acompanha a conclusão do lote.",
    "build-agent": "Confere os tipos e valida a compilação do projeto.",
    "codebase-analyzer": "Analisa detalhes da implementação e ajuda a localizar e explicar componentes específicos do código-fonte.",
    "codebase-locator": "Localiza arquivos, diretórios e componentes pertinentes a uma funcionalidade ou tarefa no repositório.",
    "codebase-pattern-finder": "Localiza implementações semelhantes, exemplos de uso e padrões existentes que possam orientar uma mudança.",
    "context-manager": "Descobre, cataloga, valida e mantém a estrutura de contexto do projeto, acompanhando suas dependências.",
    "context-retriever": "Localiza arquivos de contexto, padrões e guias relevantes em um repositório.",
    "contextscout": "Localiza e prioriza arquivos de contexto do projeto e aponta quando a documentação externa de uma biblioteca pode ser necessária.",
    "contract-manager": "Gerencia contratos de API para apoiar desenvolvimento paralelo com desenho contract-first e suporte a OpenAPI/Swagger.",
    "copywriter": "Redige textos persuasivos, conteúdo de marketing e mensagens alinhadas à marca.",
    "devops-specialist": "Apoia CI/CD, infraestrutura como código e automação de implantação.",
    "eval-runner": "Executa o harness de avaliação; a ficha orienta que este perfil não seja chamado diretamente.",
    "externalscout": "Busca documentação atual e específica por versão de bibliotecas e frameworks usando Context7 e outras fontes; filtra e retorna material pertinente.",
    "frontend-specialist": "Apoia o desenho de interfaces, sistemas de design, temas e animações.",
    "image-specialist": "Apoia edição e análise de imagens com ferramentas Gemini AI.",
    "openagent": "Agente de uso geral para responder consultas, executar tarefas e coordenar fluxos em diferentes domínios, conforme a ficha.",
    "opencoder": "Orquestra tarefas complexas de programação, arquitetura e refatoração de vários arquivos.",
    "prioritization-engine": "Pontua e prioriza itens de backlog com os métodos RICE e WSJF e organiza entregas entre MVP e etapas posteriores.",
    "reviewer": "Revisa código, segurança e qualidade segundo o escopo configurado.",
    "simple-responder": "Perfil de teste que retorna a expressão `AWESOME TESTING`; destina-se à avaliação do framework, não a tarefas produtivas.",
    "stage-orchestrator": "Orquestra etapas de fluxos complexos, aplicando transições, regras de passagem, validação e reversão.",
    "story-mapper": "Converte necessidades de usuários em jornadas, épicos, histórias e entregas verticais relacionadas a contextos delimitados.",
    "task-manager": "Decompõe funcionalidades em subtarefas verificáveis, acompanha dependências em JSON e integra o fluxo à CLI.",
    "technical-writer": "Redige documentação, documentação de APIs e comunicação técnica.",
    "thoughts-analyzer": "Aprofunda temas de pesquisa por meio da análise de documentos e materiais disponíveis no repositório.",
    "thoughts-locator": "Localiza documentos relevantes no diretório `thoughts`, usado pelo projeto para armazenar metadados e notas.",
    "web-search-researcher": "Pesquisa conteúdo na web a partir de uma URL e o analisa conforme a pergunta recebida.",
    "ws-coder": "Apoia a implementação técnica e a modificação de código no escopo da tarefa.",
    "ws-researcher": "Organiza pesquisa e documentação para estruturar conhecimento e fontes pertinentes.",
    "ws-reviewer": "Revisa código quanto a segurança, desempenho e qualidade técnica.",
    "ws-scribe": "Produz documentação e prosa voltadas à comunicação com pessoas.",
    "documentation": "Aplica as convenções documentais do repositório: consulta o contexto do projeto, propõe alterações antes de editar e prioriza textos que possam ser lidos rapidamente.",
    "test-engineer": "Planeja e escreve testes conforme as convenções do projeto, considerando a testabilidade antes da implementação e buscando resultados determinísticos.",
    "web-developer": "Desenvolve componentes de interface em SolidJS, observando práticas atuais de desenvolvimento web, experiência de uso e integração eficiente de dados.",
    "32_agente_etica_open_science": "Protege os interesses legais e éticos da pesquisa e orienta a coleta e a guarda de dados pelos princípios FAIR — localizáveis, acessíveis, interoperáveis e reutilizáveis — e pela anonimização adequada.",
    "litert-lm-agent": "Opera modelos de linguagem no próprio dispositivo por meio do LiteRT-LM: lista e importa modelos, executa prompts, mantém conversas interativas, consulta metadados e pode iniciar um servidor compatível com a API da OpenAI.",
    "llm-reduction": "Camada de apoio que substitui chamadas a modelos de linguagem por busca textual, roteamento baseado em regras, classificação local e estratégias de teoria dos jogos; o objetivo declarado é reduzir custo, latência e dependência de rede.",
    "reversa-agent-forum": "Modera debates entre agentes especializados em quatro etapas — abertura, discussão, síntese e conclusão — com controle das falas e consolidação do resultado.",
    "reversa-document-ir": "Coordena um fluxo de extração de informação de documentos, da análise do material à produção de um relatório estruturado.",
    "reversa-report-agent": "Produz relatórios a partir de informações reunidas por outras etapas do fluxo Reversa, preservando a organização e a rastreabilidade do conteúdo.",
    "ws-academic-pipeline": "Coordena um fluxo de produção acadêmica, encaminhando as etapas de pesquisa, redação e revisão conforme as instruções documentadas.",
    "auxjuris_document_summarizer": "Resume documentos jurídicos, destacando informações relevantes para facilitar a leitura e a análise posterior.",
}


def aplicar_titulo_pt(nome, arquivo):
    slug = os.path.basename(arquivo).removesuffix(".md")
    if slug in PT_TITLES:
        return PT_TITLES[slug]
    # Nomes em português permanecem como foram escritos; slugs ingleses comuns
    # recebem rótulo legível e traduzido, mantendo o caminho técnico na ficha.
    if re.search(r"[A-Z]", nome) and not re.search(r"[_-]", nome):
        tokens = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", nome).split()
    else:
        tokens = re.sub(r"[_-]+", " ", nome).split()
    words = {
        "agent": "agente", "specialist": "especialista", "manager": "gestor",
        "orchestrator": "orquestrador", "reviewer": "revisor", "writer": "redator",
        "engineer": "engenheiro", "analyst": "analista", "analyzer": "analisador",
        "researcher": "pesquisador", "research": "pesquisa", "expert": "especialista",
        "auditor": "auditor", "auditor": "auditor", "builder": "construtor",
        "creator": "criador", "curator": "curador", "curator": "curador",
        "finder": "localizador", "locator": "localizador", "retriever": "recuperador",
        "scout": "explorador", "engine": "mecanismo", "runner": "executor",
        "executor": "executor", "task": "tarefa", "tasks": "tarefas",
        "code": "código", "coder": "programador", "coding": "programação",
        "software": "software", "development": "desenvolvimento", "devops": "DevOps",
        "data": "dados", "science": "ciência", "academic": "acadêmico",
        "literary": "literário", "legal": "jurídico", "inference": "inferência",
        "integration": "integração", "image": "imagem", "images": "imagens",
        "context": "contexto", "memory": "memória", "graph": "grafo",
        "web": "web", "search": "busca", "documentation": "documentação",
        "technical": "técnico", "frontend": "front-end", "backend": "back-end",
        "cloud": "nuvem", "security": "segurança", "test": "teste",
        "testing": "testes", "story": "história", "stories": "histórias",
        "mapping": "mapeamento", "mapper": "mapeador", "batch": "lote",
        "external": "externo", "prioritization": "priorização", "stage": "etapa",
        "simple": "simples", "responder": "respondente", "manager": "gestor",
        "open": "Open", "mira": "MIRA", "maswos": "MASWOS",
    }
    translated = [words.get(token.lower(), token) for token in tokens]
    if not translated:
        return nome
    # Coloca a função em primeiro plano, que é mais natural em português.
    role = translated[-1].lower()
    if role == "especialista":
        translated = ["Especialista em"] + translated[:-1]
    elif role in ("gestor", "orquestrador", "revisor", "redator", "engenheiro", "analisador", "analista", "pesquisador", "curador", "localizador", "recuperador", "explorador", "mapeador", "programador"):
        translated = [translated[-1].capitalize(), "de"] + translated[:-1]
    else:
        translated[0] = translated[0].capitalize()
    return " ".join(translated)


def tipo_pt(tipo):
    return {"subagent": "subagente", "agent": "agente", "primary": "principal",
            "specialist": "especialista", "assistant": "assistente"}.get(str(tipo).lower(), str(tipo))


# --- R618: reconciliacao catalogo <-> runtime -------------------------------
# O frontmatter dos cards usa o NOME HUMANO ("Medico Cardiologista"), enquanto o
# opencode.json registra o SLUG kebab-case ("medico-cardiologista"). Comparar os
# dois textos literalmente produzia 39 falsos "nao registrados" (SPEC-935-R618).
import difflib
import unicodedata

# Casos em que nem o slug nem a similaridade resolvem: declarados, nunca adivinhados.
ALIASES = {
    "Synthetic University — Orquestrador Acadêmico Transversal": "university_synthetic",
    "Agente Reversa: Agent Forum / Debate Moderator": "reversa-agent-forum",
    "Agente Reversa: Document IR Report Pipeline": "reversa-document-ir",
    "Agente Reversa: Process Lifecycle Manager": "reversa-process-lifecycle",
    "Catálogo de Skills Cloud (Antigravity Backup)": "skills-cloud-antigravity",
    "Cloud SQL PostgreSQL Specialist": "cloud-sql-postgres-specialist",
    "Cloud SQL SQL Server Specialist": "cloud-sql-sqlserver-specialist",
    "Haystack RAG Specialist": "haystack-rag",
    "OpenCopywriter": "copywriter",
    "OpenTechnicalWriter": "technical-writer",
    "PyPISearcher": "pypi-searcher",
    "MasterOrchestrator": "master-orchestrator",
    "StageOrchestrator": "stage-orchestrator",
    "AntigravityOrchestrator": "antigravity-orchestrator",
    "ContextScout": "contextscout",
    "Eval Runner": "eval-runner",
    "Image Specialist": "image-specialist",
    "Nano Orchestrator": "nano-orchestrator",
}

# Agentes registrados no runtime por definicao propria (sem card), declarados
# explicitamente: sao os unicos que podem ficar fora de agents/catalog/.
INLINE_DECLARADOS = frozenset()

SIMILARIDADE_MINIMA = 0.55


def _slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower())


def _tokens(s):
    return set(t for t in _slug(s).split("-") if len(t) > 2)


def carregar_cards(root):
    """Nome do frontmatter -> frontmatter, de todos os agents/catalog/*.md."""
    out = {}
    for f in sorted(glob.glob(os.path.join(str(root), "agents", "catalog", "*.md"))):
        fm = frontmatter(f)
        fm["_file"] = f
        if fm.get("name"):
            out[fm["name"]] = fm
    return out


def reconciliar(cards, runtime):
    """Mapeia nome-humano da ficha -> chave de agente no runtime.

    Ordem: nome exato -> alias declarado -> slug exato -> similaridade. A
    similaridade e apenas um ultimo recurso; os casos que dependem dela estao
    cobertos por ALIASES para que o resultado nao dependa de heuristica.
    """
    pares = {}
    for nome in sorted(cards):
        if nome in runtime:
            pares[nome] = nome
            continue
        if nome in ALIASES and ALIASES[nome] in runtime:
            pares[nome] = ALIASES[nome]
            continue
        s = _slug(nome)
        exato = [r for r in runtime if _slug(r) == s]
        if exato:
            pares[nome] = exato[0]
            continue
        melhor, score = None, 0.0
        for r in runtime:
            q = difflib.SequenceMatcher(None, s, _slug(r)).ratio()
            inter = len(_tokens(nome) & _tokens(r))
            uni = len(_tokens(nome) | _tokens(r))
            j = inter / uni if uni else 0.0
            if max(q, j) > score:
                melhor, score = r, max(q, j)
        if melhor and score >= SIMILARIDADE_MINIMA:
            pares[nome] = melhor
    return pares


def nao_registrados(cards, runtime):
    return sorted(n for n in cards if n not in reconciliar(cards, runtime))


def main():
    cfg = json.load(open(os.path.join(ROOT, "opencode.json"), encoding="utf-8"))
    agents = cfg.get("agent", {})
    catalog = carregar_cards(ROOT)
    # R618: reconciliacao por convencao de nome (slug) em vez de igualdade textual
    pares = reconciliar(catalog, agents)
    nao_reg = [n for n in sorted(catalog) if n not in pares]
    runtime_sem_ficha = sorted(set(agents) - set(pares.values()) - set(INLINE_DECLARADOS))

    # metadados por agente (fonte + descricao)
    meta = {}
    for name, f in catalog.items():
        route = f["_file"].split("agents/catalog/")[-1]
        slug = os.path.basename(route).removesuffix(".md")
        source_detail = detalhes_ficha(f["_file"])
        source_desc = source_detail or f.get("description", "")
        desc_pt = limpar_texto(PT_DESCRIPTIONS.get(slug, source_desc))
        # Descrições residuais em inglês sem tradução editorial explícita não
        # devem ser publicadas como se estivessem localizadas.
        if re.search(r"\b(the|and|with|when|from|using|through|for|across)\b", desc_pt, re.I) and slug not in PT_DESCRIPTIONS:
            desc_pt = "Perfil especializado cuja ficha de origem deve ser consultada para confirmar escopo, entradas e saída esperada."
        category = f.get("category", "ferramental")
        # Aplicação explícita em nível de perfil: mostra ao leitor quando
        # encaminhar essa tarefa ao agente e como integrar a resposta ao Core.
        tarefa = re.split(r"(?<=[.!?])\s+|;", desc_pt, maxsplit=1)[0]
        palavras = tarefa.split()
        if len(palavras) > 24:
            tarefa = " ".join(palavras[:24]).rstrip(",;:") + "…"
        app = (f"No Core, este perfil apoia tarefas relacionadas a {tarefa[0].lower() + tarefa[1:] if tarefa else 'a atividade indicada na ficha'}. "
               "O orquestrador pode encaminhar-lhe o trabalho na etapa correspondente; a resposta retorna ao fluxo principal para integração e conferência de fontes, critérios e permissões. A ficha documenta a função, mas não comprova que o perfil tenha sido chamado ou executado a tarefa.")
        meta[name] = {
            "file": route,
            "slug": slug,
            "title_pt": PT_TITLES.get(slug, aplicar_titulo_pt(name, route)),
            "desc": desc_pt,
            "category": category,
            "category_pt": PT_CATEGORY.get(category, category.replace("-", " ").title()),
            "app": app,
            "atype": f.get("type", "specialist"),
            "ver": f.get("version", ""),
        }

    inline = 0
    for name, v in agents.items():
        if name in INLINE_DECLARADOS:
            prompt = v.get("prompt", "")
            meta[name] = {
                "file": "inline (opencode.json)" if prompt else "inline",
                "desc": v.get("description", ""),
                "category": "orquestracao",
                "category_pt": "Orquestração",
                "app": PT_APLICACAO["orchestration"],
                "slug": name,
                "title_pt": aplicar_titulo_pt(name, name),
                "atype": v.get("mode", "agent"),
                "ver": "",
            }
            inline += 1

    order = ["orchestration", "academic", "research", "audit", "legal", "data",
             "inference", "engineering", "testing", "literary", "curation-agent",
             "integration", "mira-agent", "maswos-agent", "utility"]
    cats = {}
    for name, m in meta.items():
        cats.setdefault(m["category"], []).append(name)
    for k in list(cats):
        cats[k].sort(key=lambda n: n.lower())

    # Nenhuma ficha pode ser descartada: categorias fora da ordem canonica
    # entram ao final, em vez de sumirem silenciosamente do corpo do capitulo.
    emit_order = [c for c in order if c in cats]
    emit_order += sorted(c for c in cats if c not in order)

    # Numeros derivados por contagem literal (nunca fixos no gerador).
    # R618: n_fichas e o numero de AGENTES (1:1 com o runtime), e nao a soma
    # bruta de nomes — antes, alias de slug contavam duas vezes e inflavam o
    # total para 255 com apenas 216 agentes reais.
    n_agents = len(agents)
    n_cards = len(catalog)
    n_prim = sum(1 for v in agents.values() if v.get("mode") == "primary")
    n_sub = n_agents - n_prim
    n_fichas = n_agents
    n_nao_registrados = len(nao_reg)
    n_runtime_sem_ficha = len(runtime_sem_ficha)

    fd = []
    fd.append("% ============================================================")
    fd.append("%  MÓDULO 10 — Catálogo Completo de Agentes e Subagentes")
    fd.append("%  ARQUIVO GERADO — não editar à mão. Rode: python3 gen_mod10.py")
    fd.append("% ============================================================")
    fd.append(f"\\chapter{{Catálogo Completo — {n_fichas} Fichas de Agente "
              f"({n_fichas} registradas no runtime)}}")
    fd.append("")
    fd.append("\\roteirodidatico")
    fd.append("{Este catálogo é um inventário de perfis descritos no projeto. Para encontrar um agente, comece pela categoria e leia a ficha como uma declaração de escopo e instruções.}")
    fd.append("{\\emph{Ficha} é documentação; \\emph{slug} é o identificador usado na configuração; \\emph{runtime} é a sessão do aplicativo; \\emph{ativação} é uma chamada efetiva do perfil. Nas permissões, \\cod{allow} autoriza uma ação e \\cod{deny} a bloqueia, conforme a política carregada.}")
    fd.append("{Escolha um perfil, compare seu nome humano ao identificador, leia as instruções e confira permissões e requisitos. Depois localize um registro que demonstre se houve chamada.}")
    fd.append("{A reconciliação entre fichas e configuração mede consistência declarativa. Não mede desempenho, adequação da resposta nem taxa de sucesso.}")
    fd.append("{O que a ficha permite concluir sobre o perfil e que observação adicional seria necessária para afirmar que ele executou bem uma tarefa?}")
    fd.append("")
    fd.append("\\begin{resultado}")
    fd.append(f"O \\pth{{opencode.json}} registra \\textbf{{{n_agents}}} agentes "
              f"({n_prim} orquestrador, {n_sub} subagentes), e o acervo "
              f"\\pth{{agents/catalog/}} traz \\textbf{{{n_cards}}} fichas. "
              f"Cada agente tem exatamente uma ficha e cada ficha um agente: "
              f"a cobertura documental é \\textbf{{1:1}} "
              f"({n_nao_registrados} fichas sem registro, "
              f"{n_runtime_sem_ficha} agentes sem ficha). As {n_fichas} fichas "
              f"abaixo são geradas deterministicamente por \\pth{{gen\\_mod10.py}} "
              f"e agrupam-se por categoria.")
    fd.append("\\end{resultado}")
    fd.append("")
    fd.append("\\begin{aviso}")
    fd.append(f"\\textbf{{Convenção de nomes (verificada em 29/09/2026, "
              f"SPEC-935-R618).}} O \\pth{{frontmatter}} de cada card usa o "
              f"\\emph{{nome humano}} (ex.: \\emph{{Cloud SQL PostgreSQL "
              f"Specialist}}), enquanto \\pth{{opencode.json}} registra o "
              f"\\emph{{slug}} em kebab-case (ex.: \\cod{{cloud-sql-postgres-"
              f"specialist}}). Uma versão anterior deste capítulo comparava os dois "
              f"textos literalmente e reportava trinta e nove fichas como não registradas — "
              f"falso positivo de convenção, não lacuna de runtime: reconciliadas "
              f"pelo slug e por alias declarado, todas as {n_cards} fichas estão "
              f"registradas. Ficha documentada ainda $\\neq$ agente testado: "
              f"registrar não prova que o agente funcione.")
    fd.append("\\end{aviso}")
    fd.append("")
    # ---- N-10 (R618): todos os numeros sao DERIVADOS, nunca fixos ----
    cats_sorted = sorted(cats.items(), key=lambda kv: -len(kv[1]))
    l1, l2 = len(cats_sorted[0][1]), len(cats_sorted[1][1])
    n_cat = len(cats)
    top2 = l1 + l2
    pct_top2 = (f"{100.0 * top2 / n_agents:.1f}").replace(".", ",")
    media_cat = (f"{n_agents / n_cat:.1f}").replace(".", ",")
    exatos = sum(1 for n in catalog if n in agents)
    naive_falta = n_cards - exatos
    alias_hits = sum(1 for n in catalog
                      if n not in agents and n in ALIASES and ALIASES[n] in agents)
    slug_hits = naive_falta - alias_hits
    cob_ingenua_pct = round(100.0 * exatos / n_agents)

    fd.append("\\begin{processo}")
    fd.append("GATILHO. o leitor quer saber se o runtime entrega o que o acervo "
              "promete, ou se documentacao e disponibilidade sao coisas distintas.")
    fd.append("ROTA. reconciliar ficha contra registro antes de contar inventario.")
    fd.append("FUNCAO. transformar o catalogo enumerativo em um teste de "
              "consistencia executavel, e nao em uma lista de nomes.")
    fd.append("\\end{processo}")
    fd.append("")
    fd.append("\\section[Leitura guiada]{Leitura guiada — Módulo 10: "
              "o catálogo como teste de consistência}")
    fd.append("")
    fd.append("\\begin{descricao}")
    fd.append(f"\\textbf{{O fenômeno.}} Um capítulo que enumera {n_agents} agentes "
              "produz a impressão de catálogo fiel. Mas a enumeração é a forma mais "
              "fácil de mascarar um erro de reconciliação: se o procedimento de "
              "contagem compara o nome humano do card com o slug do runtime, a lista "
              "parece cheia de agentes faltantes que não faltam. Foi exatamente o que "
              "aconteceu: o capítulo afirmava não estarem registradas fichas que "
              "estavam todas registradas, apenas sob outra convenção de nome.")
    fd.append("\\end{descricao}")
    fd.append("")
    fd.append("\\begin{definicao}")
    fd.append("\\textbf{Grandezas e definições.}\\par")
    fd.append("(1) \\emph{Ficha}: registro documental em \\pth{agents/catalog/}, "
              "identificado pelo \\emph{nome humano} no frontmatter.\\par")
    fd.append("(2) \\emph{Agente registrado}: entrada na chave \\pth{agent} do "
              "\\pth{opencode.json}, identificada pelo \\emph{slug} em "
              "kebab-case.\\par")
    fd.append("(3) \\emph{Reconciliação}: correspondência bijetiva entre ficha e "
              "agente, resolvida por nome exato, alias declarado ou slug.\\par")
    fd.append("(4) \\emph{Cobertura documental}: a razão entre o número de agentes "
              "com ficha e o número de agentes registrados.\\par")
    fd.append("(5) \\emph{Falso positivo de convenção}: contagem que reporta "
              "ausência onde há apenas diferença de grafia entre as duas colunas.")
    fd.append("\\end{definicao}")
    fd.append("")
    fd.append("\\begin{metodo}")
    fd.append("\\textbf{Dedução passo a passo.} Por que o erro numérico é "
              "inofensivo e o erro de reconciliação não?\\par")
    fd.append("(1) Uma lista de nomes não tem invariante: qualquer contagem produz "
              "um inteiro, e um inteiro plausível é indistinguível de um inteiro "
              "errado.\\par")
    fd.append("(2) Uma reconciliação tem invariante: o conjunto de fichas e o "
              "conjunto de agentes devem ter a mesma cardinalidade, e cada elemento "
              "de um deve ter exatamente um parceiro no outro.\\par")
    fd.append("(3) Sem a convenção de nomes explicitada, a comparação literal entre "
              "duas colunas de nomes mede \\emph{grafia}, não presença.\\par")
    fd.append("(4) A soma bruta de dois conjuntos que se correspondem por alias "
              "conta cada agente duas vezes: o total fica inflado e a discrepância "
              "aparente, quando na verdade inexiste.\\par")
    fd.append("(5) Logo, a contagem correta exige reconciliar antes de somar, e o "
              "resíduo da reconciliação é o número que merece atenção.")
    fd.append("\\end{metodo}")
    fd.append("")
    fd.append("\\begin{resultado}")
    fd.append(f"\\textbf{{Exemplo resolvido.}} Estado da configuração consultada nesta geração, com "
              f"$N = {n_agents}$ agentes no \\pth{{opencode.json}} e $F = {n_cards}$ "
              f"fichas em \\pth{{agents/catalog/}}.\\par")
    fd.append(f"(1) Contagem ingênua por igualdade textual: ${naive_falta}$ fichas "
              f"sem correspondência exata, o que sugeriria cobertura de "
              f"$\\frac{{{exatos}}}{{{n_agents}}} \\approx {cob_ingenua_pct}\\%$ "
              f"— número plausível, e por isso mesmo perigoso.\\par")
    fd.append(f"(2) Reconciliação por slug: os ${naive_falta}$ casos se resolvem em "
              f"${slug_hits}$ por equivalência direta de slug e em ${alias_hits}$ por "
              f"alias declarado (ex.: \\emph{{Synthetic University — Orquestrador "
              f"Acadêmico Transversal}} $\\to$ \\cod{{university_synthetic}}).\\par")
    fd.append(f"(3) Resíduo: ${naive_falta} - {slug_hits} - {alias_hits} = 0$ fichas "
              f"sem agente; e ${n_runtime_sem_ficha}$ agentes sem ficha.\\par")
    fd.append(f"(4) Cobertura documental correta: "
              f"$\\frac{{{n_agents}}}{{{n_agents}}} = 1 = 100\\%$.\\par")
    fd.append("(5) Leitura correta do número verdadeiro: uma versão anterior somava "
              "os dois acervos como se fossem disjuntos e obtinha um total maior que "
              "o número real de agentes — supercontagem devida a aliases contados em "
              "duplicidade.")
    fd.append("\\end{resultado}")
    fd.append("")
    fd.append("\\begin{resultado}")
    fd.append(f"\\textbf{{Ordem de grandeza e verificação.}} A cobertura de "
              f"$100\\%$ é exata e, ainda assim, diz pouco: as duas maiores "
              f"categorias (${l1}$ e ${l2}$ fichas, de {n_cat} no total) somam "
              f"$\\frac{{{top2}}}{{{n_agents}}} \\approx {pct_top2}\\%$, de modo que "
              f"a média por categoria (${n_agents}/{n_cat} \\approx {media_cat}$) "
              f"descreve mal a distribuição — o mesmo mecanismo de concentração que "
              f"oculta o desequilíbrio no Módulo 8. \\emph{{Verifique você mesmo:}} "
              f"rode \\cod{{python3 gen_mod10.py}} e confira quantos elementos são "
              f"emitidos; alterar o \\pth{{opencode.json}} e reexecutar deve mover "
              f"esse número na mesma medida.")
    fd.append("\\end{resultado}")
    fd.append("")
    fd.append("\\begin{aviso}")
    fd.append("\\textbf{Limite de validade.} Reconciliação é consistência "
              "declarativa, não evidência funcional: um agente registrado e "
              "documentado pode ainda estar quebrado, jamais invocado ou sem "
              "permissão adequada. O resultado $100\\%$ atesta que nome e documento "
              "batem, não que o agente funcione: atestar comportamento é o gate de "
              "teste, descrito no Módulo 4.")
    fd.append("\\end{aviso}")
    fd.append("")
    fd.append("\\begin{resultado}")
    fd.append("\\textbf{Exercícios.} (1) Acrescente um agente fictício ao "
              "\\pth{opencode.json} sem card correspondente e calcule a cobertura "
              "resultante. (2) Remova o alias de \\emph{Synthetic University} no "
              "gerador e observe o teste de reconciliação falhar. (3) Explique, em "
              "uma frase, por que \\emph{inventário completo} e "
              "\\emph{inventário correto} são propriedades diferentes.")
    fd.append("\\end{resultado}")
    fd.append("")
    fd.append("\\section{Panorama por categoria}")
    fd.append("")
    fd.append("\\begin{resultado}")
    fd.append("Contagem por categoria (ordem decrescente de fichas):\\par")
    fd.append("\\smallskip")
    fd.append("{\\footnotesize")
    fd.append("\\begin{tabularx}{\\textwidth}{lrX}")
    fd.append("\\toprule")
    fd.append("Categoria & Fichas & Exemplo de agentes \\\\")
    fd.append("\\midrule")
    for cat in sorted(cats, key=lambda c: -len(cats[c])):
        ex = ", ".join(meta[name]["title_pt"] for name in cats[cat][:3])
        fd.append(f"{esc(PT_CATEGORY.get(cat, cat.title()))} & {len(cats[cat])} & {esc(ex)} \\\\")
    fd.append("\\bottomrule")
    fd.append("\\end{tabularx}\\par}")
    fd.append("\\end{resultado}")
    fd.append("")

    for cat in emit_order:
        if cat not in cats:
            continue
        fd.append(r"\clearpage")
        fd.append(r"\section{Categoria: " + esc(PT_CATEGORY.get(cat, cat.title())) + f" ({len(cats[cat])} perfis)" + "}")
        fd.append("")
        fd.append("\\begin{descricao}")
        fd.append(esc(PT_CATEGORY_INTRO.get(cat, "Categoria complementar do catálogo. Consulte as fichas individuais para identificar o escopo documentado e sua relação com os fluxos do Core.")))
        fd.append("\\end{descricao}")
        fd.append("")
        for name in cats[cat]:
            m = meta[name]
            # Ficha inline (sem card no catalogo) nao tem versao: evita "(v)".
            ver = f" (v{m['ver']})" if m["ver"] else ""
            src = m["file"]
            fd.append(
                f"\\elemento{{{esc(m['title_pt'])}{ver}}}"
                f"{{\\metainfo{{Categoria}}{{{esc(m['category_pt'])}}} \\hfill "
                f"\\metainfo{{Tipo}}{{{esc(tipo_pt(m['atype']))}}} \\hfill "
                f"\\metainfo{{Identificador}}{{{esc(name)}}} \\hfill "
                f"\\metainfo{{Ficha}}{{{esc(src)}}}}}"
            )
            fd.append("")
            fd.append("\\begin{descricao}")
            fd.append(esc(m["desc"]) or "A ficha de origem não traz uma descrição resumida; consulte o arquivo indicado nesta ficha.")
            fd.append("\\end{descricao}")
            fd.append("")
            fd.append("\\begin{funcao}")
            fd.append(esc(m["app"]))
            fd.append("\\end{funcao}")
            fd.append("")
            if name in agents:
                perm = agents[name].get("permission", {})
                mode = agents[name].get("mode", "")
            else:
                perm, mode = {}, ""
            perm_txt = "; ".join(f"{k}: {v}" for k, v in perm.items())
            fd.append("\\begin{arquitetura}")
            fd.append("\\textbf{Modo de execução declarado:} " + esc(tipo_pt(mode or "subagent"))
                      + (" · \\textbf{Permissões:} " + esc(perm_txt) if perm_txt else ""))
            fd.append("\\end{arquitetura}")
            fd.append("")
    fd.append("% fim do módulo 10 (gerado)")

    open(OUT, "w", encoding="utf-8").write("\n".join(fd) + "\n")
    n_emit = sum(1 for l in fd if l.startswith("\\elemento{"))
    assert n_emit == n_fichas, f"fichas emitidas {n_emit} != {n_fichas}"
    print(f"OK: {n_agents} agentes -> {OUT} "
          f"({n_fichas} fichas em {len(emit_order)} categorias)")


if __name__ == "__main__":
    main()
