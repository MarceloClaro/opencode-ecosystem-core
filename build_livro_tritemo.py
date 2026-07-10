#!/usr/bin/env python3
"""
Build Script: Livro "Tritemo: O Elixir e o Tempo"
==================================================
Produz o livro completo com ilustrações MIRA + template Victoria Regia.
"""

import os, sys, subprocess, shutil, json, time
from pathlib import Path

# ── Setup paths ──────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

HISTORIA_FILE = Path("/mnt/c/Users/marce/Downloads/historia/TRITEMO. PARA COLUNA CONURBAÇÃO.CERTO.md")
OUTPUT_DIR = ROOT / "producao_cientifica" / "tritemo"
LIVRO_DIR = OUTPUT_DIR / "livro"
LATEX_DIR = OUTPUT_DIR / "latex"
MIRA_DIR  = OUTPUT_DIR / "ilustracoes" / "mira"
MERMAID_DIR = OUTPUT_DIR / "ilustracoes" / "mermaid"

CHAPTER_NAMES = [
    "1_O_Alquimista_Moderno",
    "2_O_Elixir_da_Vida",
    "3_O_Despertar_em_Camelot",
    "4_Merlin_e_os_Druidas",
    "5_Jessica",
    "6_A_Invasao_Saxa",
    "7_O_Resgate_Heroico",
    "8_O_Adeus_e_o_Retorno",
]

CHAPTER_TITLES = [
    "O Alquimista Moderno",
    "O Elixir da Vida",
    "O Despertar em Camelot",
    "Merlin e os Druidas",
    "Jéssica",
    "A Invasão Saxã",
    "O Resgate Heróico",
    "O Adeus e o Retorno",
]

# ── Step 1: Generate MIRA illustrations ──────────────────────────────
def generate_mira_illustrations():
    """Cria cards MIRA animados para cada capítulo."""
    print("=" * 60)
    print("🎨 GERANDO ILUSTRAÇÕES MIRA...")
    print("=" * 60)
    
    from illustrations.mira_engine import MiraEngine
    
    engine = MiraEngine(output_dir=str(MIRA_DIR))
    cards = []
    
    chapter_themes = [
        ("Alquimia e Ciência", "Lucas Tritemo estudava os alquimistas da idade média em busca da pedra filosofal, ciência e magia se encontravam no laboratório moderno"),
        ("O Elixir da Imortalidade", "A preparação do Elixir da Vida exigia conhecimentos ancestrais e moderna química farmacêutica"),
        ("Despertar Místico", "Acordar em Camelot, no laboratório de Merlin, foi o choque entre razão e magia que Lucas jamais imaginou"),
        ("Senhor de Avalon", "Merlin, o druida senhor de Avalon, guardava os segredos ancestrais druidas"),
        ("Amor à Primeira Vista", "Jessica colhia clemátis na campina quando os olhos de Lucas encontraram os seus num instante eterno"),
        ("Invasão e Perigo", "Os saxões atacaram o castelo de Cadbury, flechas e catapultas contra a muralha de Camelot"),
        ("O Nevoeiro Mágico", "Merlin criou um nevoeiro mágico para encobrir o acampamento saxão e libertar Lucas"),
        ("O Beijo e o Adeus", "Lucas beijou Jessica uma última vez antes de tomar o elixir e prometer voltar"),
    ]
    
    for i, (title, concept) in enumerate(chapter_themes):
        card = engine.card(title, concept, subtitle=f"Capítulo {i+1}: {CHAPTER_TITLES[i]}")
        rendered = engine.render(card)
        cards.append(rendered)
        print(f"  ✓ Card MIRA: {title} → {rendered.html_path}")
    
    print(f"\n  ✅ {len(cards)} cards MIRA gerados em {MIRA_DIR}\n")
    return cards

# ── Step 2: Generate Mermaid diagram ─────────────────────────────────
def generate_mermaid_diagram():
    """Cria diagrama Mermaid da estrutura do livro."""
    print("=" * 60)
    print("📊 GERANDO DIAGRAMA MERMAID...")
    print("=" * 60)
    
    from illustrations.mermaid_engine import MermaidEngine
    
    engine = MermaidEngine(output_dir=str(MERMAID_DIR))
    
    # Flat outline for MermaidEngine
    outline_flat = [
        "Cap 1: O Alquimista Moderno",
        "Cap 2: O Elixir da Vida",
        "Cap 3: O Despertar em Camelot",
        "Cap 4: Merlin e os Druidas",
        "Cap 5: Jessica",
        "Cap 6: A Invasao Saxa",
        "Cap 7: O Resgate Heroico",
        "Cap 8: O Adeus e o Retorno",
    ]
    
    fig = engine.from_outline("Estrutura do Livro - Tritemo", outline_flat)
    engine.render(fig)
    
    # Create a storyline flowchart as well
    flowchart_mmd = """flowchart TD
    A["🔬 Lucas Tritemo<br>Estudante de Química"] --> B["⚗️ O Elixir da Vida"]
    B --> C["🌌 Viagem no Tempo"]
    C --> D["🏰 Camelot - Merlin"]
    D --> E["🌿 Druidismo e Avalon"]
    E --> F["💖 Encontro com Jéssica"]
    F --> G["⚔️ Invasão Saxã"]
    G --> H["🌫️ Nevoeiro Mágico"]
    H --> I["🏆 Resgate e Vitória"]
    I --> J["👑 Excalibur"]
    J --> K["💔 O Adeus"]
    K --> L["⏳ Promessa de Volta"]
    
    style A fill:#58a6ff,color:#fff
    style B fill:#d29922,color:#fff
    style C fill:#8957e5,color:#fff
    style D fill:#3fb950,color:#fff
    style E fill:#f778ba,color:#fff
    style F fill:#f85149,color:#fff
    style G fill:#e6edf3,color:#000
    style H fill:#58a6ff,color:#fff
    style I fill:#d29922,color:#fff
    style J fill:#8957e5,color:#fff
    style K fill:#3fb950,color:#fff
    style L fill:#f778ba,color:#fff
"""
    flowchart_path = MERMAID_DIR / "tritemo_flowchart.mmd"
    flowchart_path.write_text(flowchart_mmd, encoding="utf-8")
    
    print(f"  ✓ Mermaid outline: {fig.mmd_path or 'N/A'}")
    print(f"  ✓ Mermaid flowchart: {flowchart_path}")
    print(f"  ✅ Diagrama gerado em {MERMAID_DIR}\n")

# ── Step 3: Set up Victoria Regia LaTeX book ─────────────────────────
def setup_latex_book():
    """Configura o template Victoria Regia com o conteúdo do livro."""
    print("=" * 60)
    print("📖 MONTANDO LIVRO LaTeX (Victoria Regia)...")
    print("=" * 60)
    
    # Create directories
    LATEX_DIR.mkdir(parents=True, exist_ok=True)
    content_dir = LATEX_DIR / "content"
    frontmatter_dir = LATEX_DIR / "frontmatter"
    misc_dir = LATEX_DIR / "misc"
    cover_dir = LATEX_DIR / "cover"
    content_dir.mkdir(exist_ok=True)
    frontmatter_dir.mkdir(exist_ok=True)
    misc_dir.mkdir(exist_ok=True)
    cover_dir.mkdir(exist_ok=True)
    
    # Copy Victoria Regia template files
    template_dir = ROOT / "publishing" / "templates" / "livro" / "victoria_regia"
    for item in template_dir.rglob("*"):
        if item.is_file():
            rel = item.relative_to(template_dir)
            dest = LATEX_DIR / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    
    # Copy logo images for cover
    for logo in ["logo-black.png", "logo-white.png"]:
        src = template_dir / "frontmatter" / logo
        if src.exists():
            shutil.copy2(src, frontmatter_dir / logo)
    
    # Update main.tex with book metadata
    main_tex = r"""% =============================================================================
% Victoria-Regia book template by @jancarauma
% Adapted for: Tritemo - O Elixir e o Tempo
% =============================================================================

\documentclass[12pt,openany]{book}

\newcommand{\goldenratio}{1.618}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{brazil}

% --- Book metadata ---
\newcommand{\authorname}{Marcelo Dias de Carvalho Filho}
\newcommand{\translatorname}{}
\newcommand{\booktitle}{Tritemo}
\newcommand{\subtitle}{O Elixir e o Tempo}
\newcommand{\publisher}{OpenCode Publishing}
\newcommand{\editionyear}{2026}
\newcommand{\isbn}{978-65-00-00000-0}

\usepackage{misc/options}

\usepackage{graphicx}
\usepackage{wrapfig}
\usepackage{float}
\usepackage{hyperref}

\begin{document}

% ===== Front Matter =====
\frontmatter
\input{frontmatter/titlepage}
\input{frontmatter/copyrightpage}
\input{frontmatter/preface}
\input{frontmatter/tocpage}

% ===== Main Content =====
\mainmatter
\pagestyle{fancy}

\input{content/chapter1}
\input{content/chapter2}
\input{content/chapter3}
\input{content/chapter4}
\input{content/chapter5}
\input{content/chapter6}
\input{content/chapter7}
\input{content/chapter8}

% ===== Back Matter =====
\backmatter
\input{frontmatter/backpage}

\end{document}
"""
    (LATEX_DIR / "main.tex").write_text(main_tex, encoding="utf-8")
    
    # Generate chapter files
    chapters_content = [
        # Chapter 1
        r"""\chapter{O Alquimista Moderno}

\lettrine{L}{ucas Tritemo}, talentoso estudante de Química, com amplo interesse na alquimia da idade média, aspirante a cientista, buscava nos livros antigos respostas para existência da vida humana, convicto que o conhecimento do passado aliado a tecnologia da modernidade causaria descobertas extraordinárias.

O jovem tornou-se conhecido por suas contribuições na indústria farmacêutica, fato que alicerçava sua confiança em progredir nesse caminho, em suas pesquisas descobriu que a alquimia antiga possuía alguns objetivos que o atraíam de forma singular: a \textbf{Transmutação} --- transformar metais comuns (chumbo, cobre) em preciosos, como ouro ou prata; a \textbf{Medicina} --- criar um elixir, uma poção ou um metal capaz de curar todas as doenças; e a \textbf{Transcendência} --- descobrir um elixir que conduziria à imortalidade.

\begin{quote}
\small\textit{Consulte o card MIRA interativo ``Alquimia e Ciência'' em \textbf{ilustracoes/mira/alquimia-e-ciencia.html} para uma metáfora visual animada deste capítulo.}
\end{quote}

Lucas encontrou nos estudos da alquimia medieval semelhanças a seu desejo de ascensão científica e deparou-se com a obtenção da chave para a imortalidade (elixir da longa vida). Os alquimistas estavam empenhados na descoberta da pedra filosofal, a qual iria desencadear as demais buscas. Vestiu-se de responsabilidade e tornou a pedra filosofal seu projeto pessoal.

Junto ao desejo surgiu o medo de represálias, já que os amplos conhecimentos dos alquimistas e o perigo que geravam numa sociedade teocêntrica (Deus como centro do Universo) causaram no medievo desastrosos resultados, culminando em um período também conhecido como Idade das Trevas, levando a perseguição de muitos cientistas pela Santa Inquisição, sendo eles excomungados, presos e queimados na fogueira. Nessa época a alquimia era sinônimo de bruxaria e quem a praticava (chamados bruxos ou bruxas) estariam indo contra as leis de Deus.
""",
        # Chapter 2
        r"""\chapter{O Elixir da Vida}

A modernidade e mudança dos tempos trouxeram certo conforto, o que aliviava Lucas, porém a soberba da descoberta inflava seu Ego e vaidade a ponto de tornar sua pesquisa secreta e silenciosa. Seguindo os ensinamentos dos alquimistas medievos, associando os conhecimentos trazidos pela modernidade, Lucas pôs-se a criar o magnífico Elixir da vida, cheio de arrogância e soberba, características de mentes brilhantes como a sua. Essa confiança o fez tomar a decisão de ele mesmo ser a cobaia para provar o primeiro protótipo do Elixir.

\begin{quote}
\small\textit{Veja o card MIRA ``O Elixir da Imortalidade'' em \textbf{ilustracoes/mira/o-elixir-da-imortalidade.html} --- animação com metáfora visual do Elixir da Vida.}
\end{quote}

Confiante, bebe todo o conteúdo do frasco e em alguns minutos perde os sentidos, caindo desacordado. Após o decorrer de alguns minutos inerte, inicia lentamente a reaver os sentidos e tenta abrir os olhos, mas as pálpebras pesam como toneladas de ferro. Desiste temporariamente e perde-se em conflitantes pensamentos.

Consegue abrir os olhos e, ainda deitado, começa a se debater e gritar de forma desesperada, momento em que é tranquilizado por um velho senhor que o acalmava de forma amigável, o que o deixou ainda mais confuso por não saber onde estava. Teria morrido? Ou estaria no hospital? O senhor seria um médico?
""",
        # Chapter 3
        r"""\chapter{O Despertar em Camelot}

--- Onde estou? Quem é o senhor? --- perguntou Lucas, confuso.

O senhor respondeu de forma sóbria:

--- É Sir. Lucas, nossa fórmula ainda não está pronta, teremos que trabalhar um pouco mais. Sua perda de memória também é mau sinal, realmente não lembra nada?

--- Apenas que estava na garagem de minha casa trabalhando em meu Elixir e acordei aqui com o senhor.

--- Você é Sir. Lucas, meu aprendiz. Estávamos testando uma de minhas experiências e você desmaiou. Estamos no reino de Camelot, me chamo Merlin e este é meu laboratório. Recorda agora?

\begin{quote}
\small\textit{O card MIRA ``Despertar Místico'' em \textbf{ilustracoes/mira/despertar-mistico.html} ilustra o momento em que Lucas acorda no laboratório de Merlin.}
\end{quote}

--- Ainda estou confuso, isso não pode acontecer, eu não sou dessa Época!

--- Ora, ora! Ingênuo garoto, sua juventude me fascina. Ah! A beleza e luminosidade da juventude, com essa surpreendente alegria pela vida transparente em seu olhar me faz querer reacender sua memória com a fabulosa estória da Ilha de Avalon.
""",
        # Chapter 4
        r"""\chapter{Merlin e os Druidas}

--- Existem lindas lendas que encantam e fazem a imaginação voar. Conta-se que Avalon é uma ilha, famosa por suas belas maçãs. --- Ao falar desta estória, Merlin recorda Lucas até mesmo do Gaélico, seu idioma nativo.

--- Avalon é um lugar de conhecimento sobre os deuses pagãos antigos onde os druidas passavam o conhecimento antigo de geração em geração. É o lugar onde se aprende o conhecimento da religião antiga, o druidismo. Sendo eu, Merlin, o senhor de Avalon. Você, Sir. Lucas, é meu aprendiz. Ficou claro agora?

\begin{quote}
\small\textit{O card MIRA ``Senhor de Avalon'' em \textbf{ilustracoes/mira/senhor-de-avalon.html} representa Merlin e os druidas em metáfora visual animada.}
\end{quote}

--- Como meu aprendiz, eu passo a você o legado especial sobre o Druidismo.

--- Eu lembro de ter estudado na minha época sobre a presença dos druidas na literatura, o que exerce em mim fascínio e apresenta tons misteriosos. Eu ouvi também sobre o druidismo através das histórias que envolvem o Rei Arthur e os Cavaleiros da Távola Redonda, nas quais Merlin, o senhor, ocupa a posição de um druida.

--- Continuo confuso, Sir Merlin, pois eu venho de outra época, não era para estar aqui.

--- Que brincadeira ingênua essa sua, garoto. Tenho muita idade mas não sou um tolo e acredito que nossa experiência pode ter causado essa confusão, mas eu vou resolver o problema.

--- Vamos flanar um pouco pelo reino, sair desse laboratório, talvez você recupere a memória. Estamos no castelo de Cadbury, em Somerset, um isolado forte que é seguro para andarmos livremente.

--- Eu sempre li que Camelot é um esplendor, onde viviam nobres, cavaleiros e damas que se reuniam em numerosos banquetes e torneios. Nos dias de festa, flutuavam bandeiras nos seus pátios; pavilhões eram montados, espalhando-se pelas suas encostas e era intensa a movimentação de pessoas que entravam e saíam pelos seus portões.

--- Sim, meu jovem, mas não viviam, \textit{vivemos}. Eu, você, e logo verá todos reunidos.
""",
        # Chapter 5
        r"""\chapter{Jéssica}

Caminhando pelos arredores do castelo com Merlin, Lucas vê-se fascinado por toda aquela beleza campestre. Seus olhos cravam-se em uma figura curvilínea a alguns metros de distância e, de repente, pega-se desejando ver àquela pequena donzela mais de perto. Seus cabelos longos e castanhos acobreados reluzem com os raios do sol. Guiado pela brisa campestre que traz o cheiro da relva adocicado com o cândido perfume daquela linda aparição a andar pela paisagem do lugar, e sem perceber, seus pés o levam até ela.

--- Espere, meu jovem. Aonde você vai com tanta pressa? --- Merlin o detém segurando pelo ombro e acompanha o seu olhar.

--- Quem é ela? --- pergunta fascinado.

--- Jéssica, minha bisneta! --- o velho responde orgulhoso. --- Não lembra dela também?

\begin{quote}
\small\textit{``Amor à Primeira Vista'' é o card MIRA disponível em \textbf{ilustracoes/mira/amor-a-primeira-vista.html} para este capítulo.}
\end{quote}

Distraída em meio a tantas flores, Jéssica não ouviu os passos dos cavalheiros que se aproximavam. Abaixando-se, recolheu a última das flores para montar seu arranjo de clemátis. Quando se levantou, seus olhos cruzaram-se com os de Sir Lucas e a atração entre eles é imediata. Merlin percebe a atração e deixa os dois sozinhos conversando, voltando para o Castelo.
""",
        # Chapter 6
        r"""\chapter{A Invasão Saxã}

De volta ao laboratório, Merlin vê nas runas o prenúncio de grande perigo e imediatamente sai para avisar o exército do reino.

A descontraída conversa entre Jéssica e Lucas é interrompida por intensa movimentação vinda da floresta, deixando-os apavorados ao perceberem que tratava-se de uma invasão de saxões no reino. Atrevida, Jéssica corre de forma frenética para o castelo e é atingida por uma flecha de um arqueiro saxão que, felizmente, não tinha boa pontaria e apenas feriu o braço da jovem, o que não a impediu de comunicar a invasão aos cavaleiros reais, alertando a defesa do forte. Já Lucas não teve a mesma sorte e foi subjugado e aprisionado pelo numeroso exército saxão.

\begin{quote}
\small\textit{O card MIRA ``Invasão e Perigo'' (ver \textbf{ilustracoes/mira/invasao-e-perigo.html}) retrata o ataque saxão a Camelot em animação.}
\end{quote}

A coragem de Jéssica impediu que as tropas de saxões chegassem a usar as poderosas catapultas de pedras contra a muralha do forte e deixou os arqueiros e cavaleiros atentos para revidar e expulsar o exército inimigo. Os invasores também não tiveram tempo de usar o aríete para arrombar o grande portão de entrada do forte. As seteiras de arqueiros rapidamente foram ocupadas pelos arqueiros defensores, deixando a muralha protegida e perigosa para invasores.

Após a frustrada invasão, Jéssica é socorrida por Merlin e ambos se preocupam com Sir Lucas. A jovem, cheia de coragem, implora a Merlin ajuda para salvar Lucas, aprisionado no acampamento saxão.
""",
        # Chapter 7
        r"""\chapter{O Resgate Heróico}

Diante da angústia de Jéssica, Merlin busca conselhos nas Runas e decide reunir um grupo de cavaleiros nobres para libertar seu aprendiz do acampamento saxão. Confiantes na astúcia mística de Merlin, 15 cavaleiros fortemente preparados e armados apropriam-se de suas armaduras e espadas e partem para o resgate suicida.

A teimosia de Jéssica não a deixaria tranquila a esperar. Então, rebela-se contra Merlin querendo participar da missão. As justificativas do bisavô não a convencem e a atrevida jovem segue sorrateira o grupo, armada apenas com uma espada que encontrou no laboratório do bisavô. Nem mesmo saberia o que fazer com ela, e tamanho era o peso que nem mesmo conseguiria erguê-la. Mas, como o bisavô sempre dizia, ``a coragem é a visão dos tolos'', e a vontade de ver de novo os olhos inquietos de Lucas compensaria o esforço e perigo.

\begin{quote}
\small\textit{``O Nevoeiro Mágico'' card MIRA em \textbf{ilustracoes/mira/o-nevoeiro-magico.html} mostra o feitiço de Merlin que encobriu o acampamento saxão.}
\end{quote}

As runas aconselharam Merlin a melhor hora de atacar o acampamento: antes do amanhecer. Assim, o sagaz mago usou seus conhecimentos místicos e criou um denso nevoeiro noturno que encobriu todo o acampamento e que, além de prejudicar a visão dos inimigos, era tóxico à respiração, e não afetaria seus cavaleiros pois o elmo de suas armaduras os protegeriam.

No chegar da fria madrugada, era o momento exato para agirem. Merlin lançou seu feitiço e o nevoeiro engoliu a noite escura. Os corajosos cavaleiros seguem ao acampamento inimigo, sendo seguidos atentamente pela escolta apaixonada de Jéssica.

Atordoados com os efeitos do nevoeiro mágico de Merlin, os invasores saxões tornam-se presas fáceis para os aguerridos cavaleiros de Camelot, que os massacram sem piedade. Em meio à batalha, Jéssica encontra o cativeiro de Lucas e o liberta. Os dois juntam-se a Merlin e seus cavaleiros e retornam livres ao castelo, deixando o acampamento inimigo devastado e furioso por vingança.
""",
        # Chapter 8
        r"""\chapter{O Adeus e o Retorno}

De volta ao castelo, Merlin apavora-se com o desaparecimento da Excalibur, a espada poderosa que estava sob sua proteção desde o rei Arthur ter negado a bandeira do Pendragon e instituído em Camelot a bandeira com a cruz do Cristo e a Virgem Maria, instituindo uma religião única em toda a Bretanha: o Cristianismo.

Vendo o desespero do bisavô com o desaparecimento da Excalibur, Jéssica devolve a espada que estava em seu poder e é vigorosamente advertida por Merlin sobre a gravidade de seus atos. Lucas tenta defendê-la e também é bruscamente advertido por Merlin.

--- Sir Lucas, eu não posso te mandar de volta para seu mundo sem antes ter a certeza que você entendeu que nós, os druidas, cultuamos a arte, a música, a poesia, dominamos a medicina natural, a fitoterapia, a agricultura, os conhecimentos astronômicos. Consideramos as runas mágicas. Mesmo tendo posse desse conhecimento, não podemos interferir na vida. Tenha responsabilidade, pois conhecimento é ``Poder''. Diga adeus a Jéssica e beba o Elixir e volte para casa, meu jovem.

\begin{quote}
\small\textit{Veja o card MIRA ``O Beijo e o Adeus'' em \textbf{ilustracoes/mira/o-beijo-e-o-adeus.html} para a despedida entre Lucas e Jéssica.}
\end{quote}

Segurando o pequeno frasco com o elixir que o levaria de volta, Lucas acariciou a pele alva do rosto de Jéssica com as pontas dos dedos. Lágrimas cristalinas caíam dos olhos escuros da jovem, maculando sua pele macia. Lucas se aproximou mais, colando seus corpos e unindo seus lábios em um beijo casto. Quando se afastou, algo se partiu dentro dele.

--- Eu te amo --- ela murmurou, cerrando os olhos e deitando o rosto contra a palma da mão dele.

--- Eu também te amo.

--- Então fica --- ela o fitou dentro dos olhos.

--- Eu não posso --- disse, dando um passo para trás. --- Mas darei um jeito para voltar e ficar com você. Me espere!

Ela balançou a cabeça concordando e, ainda olhando no fundo dos olhos intensos, Sir Lucas tomou a fórmula e caiu desacordado...
""",
    ]
    
    for i, content in enumerate(chapters_content):
        chapter_file = content_dir / f"chapter{i+1}.tex"
        chapter_file.write_text(content, encoding="utf-8")
        print(f"  ✓ Chapter {i+1}: {CHAPTER_TITLES[i]}")
    
    # Generate preface
    preface_content = r"""\chapter{Nota do Autor}

\lettrine{E}{sta} obra é fruto de uma imaginação que busca conectar dois mundos aparentemente distantes: a ciência moderna e a magia ancestral. Lucas Tritemo, o protagonista, representa o espírito inquieto do cientista que não se contenta com as respostas fáceis e mergulha nos mistérios mais profundos da existência.

A alquimia medieval, com sua busca pela pedra filosofal e pelo elixir da longa vida, encontra eco na moderna indústria farmacêutica e na nossa eterna fascinação pela imortalidade. Já Camelot, Merlin e os druidas representam o conhecimento ancestral que a humanidade teima em esquecer.

Esta história é um convite para viajar no tempo, para questionar os limites do conhecimento e para acreditar que o amor pode transcender qualquer época.

\textit{Marcelo Dias de Carvalho Filho}
"""
    (frontmatter_dir / "preface.tex").write_text(preface_content, encoding="utf-8")
    
    # Generate copyright page
    copyright_content = r"""\newpage
\thispagestyle{empty}
~
\vfill

\begin{center}
\textbf{Tritemo: O Elixir e o Tempo}

Copyright \textcopyright{} 2026 Marcelo Dias de Carvalho Filho

Todos os direitos reservados. Nenhuma parte desta publicação pode ser reproduzida, distribuída ou transmitida sem a permissão prévia por escrito do autor, exceto no caso de citações breves em resenhas e outros usos não comerciais permitidos pela lei de direitos autorais.

\textit{Produzido com o OpenCode Ecosystem Core --- MarceloClaro Orchestrator}

\textbf{OpenCode Publishing}

1ª edição --- Julho de 2026

ISBN: 978-65-00-00000-0
\end{center}
"""
    (frontmatter_dir / "copyrightpage.tex").write_text(copyright_content, encoding="utf-8")
    
    # Generate back page
    backpage_content = r"""\newpage
\thispagestyle{empty}
~
\vfill

\begin{center}
\textit{``A coragem é a visão dos tolos.''}

--- Merlin
\end{center}
"""
    (frontmatter_dir / "backpage.tex").write_text(backpage_content, encoding="utf-8")
    
    # Generate TOC page
    toc_content = r"""\newpage
\tableofcontents
"""
    (frontmatter_dir / "tocpage.tex").write_text(toc_content, encoding="utf-8")
    
    print(f"  ✅ Livro LaTeX montado em {LATEX_DIR}\n")
    return True

# ── Step 4: Generate Cover Design ────────────────────────────────────
def generate_cover():
    """Gera o estudo de design e os prompts de ilustração da capa."""
    print("=" * 60)
    print("🎨 GERANDO DESIGN DA CAPA...")
    print("=" * 60)
    
    from publishing.cover_designer import CoverDesigner
    
    cover_dir = LATEX_DIR / "cover"
    designer = CoverDesigner(str(cover_dir))
    
    content_sample = (
        "Lucas Tritemo, talentoso estudante de Química, com amplo interesse "
        "na alquimia da idade média, buscava nos livros antigos respostas "
        "para existência da vida humana. Alquimia, magia, Camelot, Merlin, druidas."
    )
    
    design = designer.design_cover(
        title="Tritemo: O Elixir e o Tempo",
        author="Marcelo Dias de Carvalho Filho",
        content_sample=content_sample,
        subtitle="O Elixir e o Tempo",
        blurb="Um estudante de Química moderna encontra-se transportado ao reino de Camelot, onde Merlin e os druidas guardam segredos ancestrais. Entre o elixir da imortalidade e um amor que desafia os séculos, Lucas Tritemo precisa escolher seu destino."
    )
    
    print(f"  ✓ Estilo detectado: {design['style']}")
    print(f"  ✓ Estudo de design: {design['study_file']}")
    print(f"  ✓ Capa LaTeX: {design['capa_file']}")
    print(f"  ✅ Design da capa gerado em {cover_dir}\n")
    return design

# ── Step 5: Generate Graphify Knowledge Graph ────────────────────────
def generate_knowledge_graph():
    """Constrói o grafo de conhecimento da história."""
    print("=" * 60)
    print("🔗 GERANDO GRAFO DE CONHECIMENTO...")
    print("=" * 60)
    
    from illustrations.graphify_engine import GraphifyEngine
    
    # Read the story and split into sections
    historia_text = Path(HISTORIA_FILE).read_text(encoding="utf-8")
    
    sections = {
        "capitulo_1_alquimista": historia_text[:1500],
        "capitulo_2_elixir": historia_text[1500:3000],
        "capitulo_3_camelot": historia_text[3000:4500],
        "capitulo_4_merlin": historia_text[4500:6000],
        "capitulo_5_jessica": historia_text[6000:7000],
        "capitulo_6_invasao": historia_text[7000:8500],
        "capitulo_7_resgate": historia_text[8500:10000],
        "capitulo_8_adeus": historia_text[10000:],
    }
    
    graph_dir = OUTPUT_DIR / "ilustracoes" / "grafo"
    ge = GraphifyEngine(output_dir=str(graph_dir), max_nodes=30)
    graph = ge.build(sections)
    paths = ge.export(graph)
    
    print(f"  ✓ Nós: {len(graph.nodes)} | Arestas: {len(graph.edges)}")
    print(f"  ✓ JSON: {paths.get('json', 'N/A')}")
    print(f"  ✓ HTML interativo: {paths.get('html', 'N/A')}")
    print(f"  ✅ Grafo gerado em {graph_dir}\n")

# ── Step 6: Compile the book ─────────────────────────────────────────
def compile_book():
    """Tenta compilar o PDF via latexmk ou pdflatex."""
    print("=" * 60)
    print("📄 COMPILANDO LIVRO PDF...")
    print("=" * 60)
    
    main_tex = LATEX_DIR / "main.tex"
    pdf_path = OUTPUT_DIR / "Tritemo_O_Elixir_e_o_Tempo.pdf"
    
    engines = [
        ("lualatex", ["lualatex", "-interaction=nonstopmode", "-output-directory=" + str(LATEX_DIR), str(main_tex)]),
        ("pdflatex", ["pdflatex", "-interaction=nonstopmode", "-output-directory=" + str(LATEX_DIR), str(main_tex)]),
    ]
    
    for name, cmd in engines:
        engine_path = shutil.which(name)
        if not engine_path:
            print(f"  ⚠ {name} não disponível, tentando próximo...")
            continue
        
        print(f"  ▶ Compilando com {name} (2 passadas)...")
        try:
            # Run twice for TOC
            for run in range(2):
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300,
                    cwd=str(LATEX_DIR)
                )
            
            # Check for generated PDF
            candidate = LATEX_DIR / "main.pdf"
            if candidate.exists():
                shutil.copy2(str(candidate), str(pdf_path))
                print(f"  ✅ PDF gerado: {pdf_path}")
                return True
            else:
                print(f"  ⚠ PDF não encontrado após compilação com {name}")
                # Show last few lines of log for debugging
                log = LATEX_DIR / "main.log"
                if log.exists():
                    log_text = log.read_text(errors="replace")[-2000:]
                    # Print only critical errors
                    for line in log_text.split('\n'):
                        if 'Error' in line or 'error' in line:
                            print(f"     {line.strip()}")
        except Exception as e:
            print(f"  ⚠ Erro com {name}: {e}")
    
    # Fallback: use pandoc md -> pdf
    print("  ▶ Tentando pandoc para PDF...")
    pandoc = shutil.which("pandoc")
    if pandoc:
        md_path = OUTPUT_DIR / "manuscrito.md"
        try:
            result = subprocess.run(
                [pandoc, str(md_path), "-o", str(pdf_path), "--pdf-engine=lualatex"],
                capture_output=True, text=True, timeout=300
            )
            if pdf_path.exists():
                print(f"  ✅ PDF gerado via pandoc: {pdf_path}")
                return True
        except Exception as e:
            print(f"  ⚠ Erro pandoc: {e}")
    
    print("  ⚠ PDF não pôde ser gerado.\n")
    return False

# ── Step 7: Copy to Desktop / Output ─────────────────────────────────
def copy_to_desktop():
    """Copia artefatos para a Área de Trabalho do usuário (detectada
    dinamicamente — Windows, Linux, macOS ou WSL — sem hardcodar usuário)."""
    from publishing.production import _detect_desktop_path
    desktop = Path(_detect_desktop_path())
    if not desktop.exists():
        print("  ⚠ Área de Trabalho não encontrada")
        return
    
    livro_dest = desktop / "Tritemo - O Elixir e o Tempo"
    livro_dest.mkdir(exist_ok=True)
    
    # Copy PDF if exists
    pdf_src = OUTPUT_DIR / "Tritemo_O_Elixir_e_o_Tempo.pdf"
    if pdf_src.exists():
        shutil.copy2(str(pdf_src), str(livro_dest / "Tritemo_O_Elixir_e_o_Tempo.pdf"))
    
    # Copy MIRA cards
    mira_dest = livro_dest / "ilustracoes_mira"
    if MIRA_DIR.exists():
        shutil.copytree(str(MIRA_DIR), str(mira_dest), dirs_exist_ok=True)
    
    # Copy Markdown
    md_src = OUTPUT_DIR / "manuscrito.md"
    if md_src.exists():
        shutil.copy2(str(md_src), str(livro_dest / "Tritemo_manuscrito.md"))
    
    print(f"  ✅ Artefatos copiados para: {livro_dest}\n")

# ── Step 7b: Generate DOCX/ODT ────────────────────────────────────────
def generate_docx():
    """Gera DOCX e ODT via pandoc."""
    print("=" * 60)
    print("📄 GERANDO DOCX/ODT...")
    print("=" * 60)
    
    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("  ⚠ pandoc não disponível")
        return
    
    md_path = OUTPUT_DIR / "manuscrito.md"
    if not md_path.exists():
        print("  ⚠ manuscrito.md não encontrado")
        return
    
    for fmt, ext in [("docx", "docx"), ("odt", "odt")]:
        out_path = OUTPUT_DIR / f"Tritemo_O_Elixir_e_o_Tempo.{ext}"
        try:
            result = subprocess.run(
                [pandoc, str(md_path), "-o", str(out_path)],
                capture_output=True, text=True, timeout=180
            )
            if out_path.exists():
                print(f"  ✅ {ext.upper()} gerado: {out_path}")
            else:
                print(f"  ⚠ Falha ao gerar {ext.upper()}")
        except Exception as e:
            print(f"  ⚠ Erro ao gerar {ext.upper()}: {e}")

# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 60)
    print("📚 LIVRO: TRITEMO - O ELIXIR E O TEMPO")
    print("=" * 60)
    print(f"Autor: Marcelo Dias de Carvalho Filho")
    print(f"Output: {OUTPUT_DIR}\n")
    
    # Step 1
    cards = generate_mira_illustrations()
    
    # Step 2
    generate_mermaid_diagram()
    
    # Step 3
    setup_latex_book()
    
    # Step 4
    generate_cover()
    
    # Step 5
    generate_knowledge_graph()
    
    # Step 6 - try compile
    compile_book()
    
    # Step 7 - copy to desktop
    copy_to_desktop()
    
    # Step 8 - Generate DOCX and ODT via pandoc
    generate_docx()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ LIVRO PROCESSADO COM SUCESSO!")
    print("=" * 60)
    print(f"\n📁 Pasta de produção: {OUTPUT_DIR}")
    print(f"📄 Manuscrito: {OUTPUT_DIR / 'manuscrito.md'}")
    print(f"📄 DOCX: {OUTPUT_DIR / 'Tritemo_O_Elixir_e_o_Tempo.docx'}")
    print(f"📄 ODT: {OUTPUT_DIR / 'Tritemo_O_Elixir_e_o_Tempo.odt'}")
    print(f"🎨 Cards MIRA: {MIRA_DIR}")
    print(f"📊 Diagrama: {MERMAID_DIR}")
    print(f"🔗 Grafo: {OUTPUT_DIR / 'ilustracoes' / 'grafo'}")
    print(f"📖 LaTeX: {LATEX_DIR}")
    print(f"🎭 Capa: {LATEX_DIR / 'cover' / 'DESIGN_STUDY.md'}")
    
    # Open the cards in browser
    print("\n📂 Cards MIRA gerados:")
    for c in cards:
        print(f"   • {c.html_path}")

if __name__ == "__main__":
    main()
