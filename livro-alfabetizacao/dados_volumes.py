# -*- coding: utf-8 -*-
"""dados_volumes.py — Dados pedagógicos dos Volumes 2–5 (SPEC-935-R220)."""


def U(n, titulo, foco, bncc, regra, boquinha, geradora, geradora_expl,
      entradas, palavras, frases, grafia, sila1, sila2, producao, dica,
      nivel="Silábico-Alfabético Avançado", palavras_misturadas=None,
      proxima=None, dominio="Leitura e Escrita", auto=None, indicadores=None,
      encaminhamento=None, curto=None):
    return {
        "n": n, "titulo": titulo, "foco": foco, "bncc": bncc, "regra": regra,
        "boquinha": boquinha, "geradora": geradora, "geradora_expl": geradora_expl,
        "entradas": entradas, "palavras": palavras, "frases": frases,
        "grafia": grafia, "sila1": sila1, "sila2": sila2,
        "producao": producao, "dica": dica, "nivel": nivel,
        "palavras_misturadas": palavras_misturadas or palavras + ["gato", "sapo", "rato", "bola", "menino"],
        "proxima": proxima, "dominio": dominio, "auto": auto, "indicadores": indicadores,
        "encaminhamento": encaminhamento, "curto": curto or titulo,
    }


def _auto(n):
    return [
        f"Reconheço as palavras com {n}",
        f"Leio as sílabas com {n} sem apoio",
        f"Escrevo palavras com {n}",
        "Separo corretamente as sílabas",
    ]


def _ind():
    return [
        "Lê com precisão as palavras-alvo da unidade",
        "Escreve com ortografia estável a grafia-alvo",
        "Generaliza a regra em escrita espontânea",
        "Mantém atenção e ritmo na folha",
        "Articula o som-alvo com clareza",
    ]


def _enc(fichas, extra=""):
    return ("Se 2 ou mais respostas NÃO no Passo 1 OU 2+ marcações R/N no Passo 2, "
            "registrar no Registro de Progresso e comunicar à família; o profissional "
            f"habilitado avalia com {fichas}. " + extra)


PERFIS = {}


# ===========================================================================
# VOLUME 2 — 2º ANO
# ===========================================================================
VOLUME2 = {
    "ano": 2,
    "titulo_ano": "2º Ano do Ensino Fundamental",
    "bncc": "EF02LP01--EF02LP10",
    "sobre": "Consonantes do Bloco 2 e Sílabas Simples",
    "fonemas": [
        ("/tʃ/", "ch", "chave, chuva"),
        ("/ʎ/", "lh", "ilha, coelho"),
        ("/ɲ/", "nh", "ninho, banho"),
        ("/kʷ/", "qu", "queijo, quilo"),
        ("/gʷ/", "gu", "guerra, água"),
        ("/bɾ/", "br", "braço, livro"),
        ("/kɾ/", "cr", "cravo, preto"),
        ("/dɾ/", "dr", "dragão, madre"),
        ("/fɾ/", "fr", "fruta, frio"),
        ("/gɾ/", "gr", "grade, grande"),
        ("/pɾ/", "pr", "prato, primo"),
        ("/tɾ/", "tr", "trem, corte"),
        ("/vɾ/", "vr", "livro, palavra"),
        ("/ʁ/ (forte)", "rr", "carro, terra"),
        ("/s/ (forte)", "ss", "passar, osso"),
        ("/s/, /z/", "s/z", "casa, zero"),
        ("/s/ (ç)", "ç", "coração, açúcar"),
    ],
    "triagem": {
        "Leitura e Fluência": ["Lê frases com precisão", "Lê com ritmo adequado", "Usa entonação ao ler"],
        "Escrita e Ortografia": ["Escreve com ortografia estável", "Usa as grafias-alvo do ano", "Traçado legível e homogêneo"],
        "Consciência Fonológica": ["Segmenta palavras em sílabas", "Percebe rimas e aliterações", "Manipula fonemas (troca/omite)"],
        "Linguagem Oral": ["Narra fatos com sequência lógica", "Usa vocabulário variado", "Articula sem trocas persistentes"],
        "Atenção e Funções Executivas": ["Mantém foco por 10–15 minutos", "Planeja a tarefa antes de executar", "Inibe respostas impulsivas"],
        "Motricidade Fina e Traçado": ["Preensão funcional do lápis", "Pressão adequada no papel", "Direção correta do traçado"],
        "Comportamento e Interação": ["Regula emoções com apoio", "Coopera em duplas", "Lida com a frustração"],
    },
    "unidades": [
        U(0, "Prontidão para o 2º Ano", "Revisão de vogais e sílabas simples",
          "EF02LP01", "Revisar as vogais, as consoantes simples e a leitura de sílabas diretas.",
          "Na revisão, a boca produz cada vogal com a boca aberta e o ar saindo sem obstáculo. Use o espelho para comparar A, E, I, O, U.",
          "MÃE", "a palavra mais afetiva da alfabetização, revisita a nasalidade com carinho.",
          [("M", "A"), ("S", "A"), ("T", "A"), ("L", "E"), ("P", "I"), ("B", "O"), ("F", "U"), ("N", "A")],
          ["mãe", "sapo", "tatu", "leite", "pipa", "bola", "foca", "navio"],
          ["A mãe lê para mim.", "O sapo pula na lagoa.", "A pipa voa no céu.", "A foca nada no mar."],
          "ÃE", "MÃ", "MA",
          "Escrever um bilhete curto para a família usando palavras das vogais.",
          "Antes de avançar, garanta que a leitura de sílabas diretas esteja automática; use o espelho da Boquinha sempre que houver dúvida.",
          proxima=1),
        U(1, "Dígrafo CH", "O som /tʃ/ e as grafias CH",
          "EF02LP03", "CH representa o som /tʃ/: chave, chuva, chapéu. Em palavras como chiclete, o CH aparece no meio e no início.",
          "Para dizer CH, os lábios se projetam, a língua toca o céu da boca e o ar escapa com atrito. Compare CHA com CA.",
          "CHUVA", "a chuva é cotidiana e permite sentir o som das gotas, perfeita para ancorar o dígrafo.",
          [("CH", "A"), ("CH", "E"), ("CH", "I"), ("CH", "O"), ("CH", "U")],
          ["chave", "chapéu", "chuva", "chão", "cheiro", "choro", "fecho", "chá"],
          ["A chave abriu a porta.", "A chuva molhou o chão.", "O chapéu protege do sol.", "Sinto o cheiro do bolo."],
          "CH", "CHA", "CHE",
          "Escrever três frases sobre o que você faz em um dia de chuva, usando palavras com CH.",
          "Faça o aluno comparar CHA (africado) com CA (oclusivo) no espelho; a diferença articulatória é o coração da lição.",
          proxima=2,
          dominio="Consciência Fonológica e Leitura",
          auto=_auto("CH"),
          indicadores=_ind(),
          encaminhamento=_enc("Ficha 18 (TDL) e Ficha 19 (Desvio Fonológico)")),
        U(2, "Dígrafo LH", "O som /ʎ/ e a grafia LH",
          "EF02LP03", "LH representa o som /ʎ/: ilha, coelho, orelha. A língua encosta no céu da boca e o som sai lateralmente.",
          "Para LH, a ponta da língua sobe ao céu da boca e o ar sai pelas laterais, como um 'L molhado'. Observe o sorriso dos lábios.",
          "COELHO", "o coelho é afetivo e conhecido; ajuda a fixar o som lateral do LH.",
          [("LH", "A"), ("LH", "E"), ("LH", "I"), ("LH", "O"), ("LH", "U")],
          ["ilha", "coelho", "orelha", "milho", "filho", "folha", "velho", "telhado"],
          ["O coelho comeu a folha.", "O filho mora na ilha.", "A orelha do elefante é grande.", "O velho consertou o telhado."],
          "LH", "LHA", "LHE",
          "Listar os integrantes da família e escrever uma frase para cada um, usando LH quando possível.",
          "LH exige apoio prolongado da língua no palato; volte ao espelho sempre que o aluno produzir um L comum.",
          proxima=3),
        U(3, "Dígrafo NH", "O som /ɲ/ e a grafia NH",
          "EF02LP03", "NH representa o som /ɲ/: ninho, banho, sonho. A língua inteira toca o céu da boca e o ar sai pelo nariz.",
          "Para NH, a boca fica quase fechada, a língua toca o palato e o ar sai pelo nariz, como um sorriso nasal.",
          "NINHO", "o ninho une o afeto (aves) e a forma nasal do som; é a palavra geradora perfeita.",
          [("NH", "A"), ("NH", "E"), ("NH", "I"), ("NH", "O"), ("NH", "U")],
          ["ninho", "banho", "sonho", "pinho", "galinha", "minhoca", "caminho", "vinho"],
          ["O ninho tem três ovos.", "Tomo banho de manhã.", "A galinha cisca no caminho.", "Eu sonho com o mar."],
          "NH", "NHA", "NHE",
          "Contar e escrever uma história curta usando pelo menos 5 palavras com NH.",
          "NH e LH são parecidos no gesto; compare no espelho a saída do ar (nariz para NH, laterais para LH).",
          proxima=4,
          dominio="Consciência Fonológica",
          auto=_auto("NH"),
          indicadores=_ind(),
          encaminhamento=_enc("Ficha 18 (TDL)")),
        U(4, "QU e GU", "Os digrafos QU e GU nas sílabas QUE e QUI",
          "EF02LP07", "QU representa o som /k/ em que e qui (queijo, quilo). GU representa /g/ em que e gui (guerra, guia). O U não é pronunciado.",
          "Em QUE e QUI, a boca faz o som de K com os lábios arredondados; em GUE e GUI, o som de G com a mesma postura.",
          "QUEIJO", "o queijo é familiar e permite explorar QUE/QUI com um alimento do cotidiano.",
          [("QU", "E"), ("QU", "I"), ("GU", "E"), ("GU", "I")],
          ["queijo", "quilo", "quente", "guerra", "guia", "guitarra", "quero", "água"],
          ["O queijo está na mesa.", "Eu quero um quilo de pão.", "A água está quente.", "A guitarra toca na festa."],
          "QU", "QUE", "QUI",
          "Escrever um convite de aniversário usando QUE e QUI e palavras com GU.",
          "Não confunda QUER com KER: explore a correspondência na leitura e na escrita; o treino Kumon fixa.",
          proxima=5),
        U(5, "Encontros Consonantais (1): BR, CR, DR, FR, GR, PR, TR, VR",
          "Os encontros consonantais do bloco 1",
          "EF02LP04", "Nos encontros consonantais, duas consoantes aparecem juntas e cada uma mantém seu som: braço, cravo, prato.",
          "Ao dizer BR, os lábios começam juntos (B) e a língua vibra (R). Cada consoante do encontro é articulada, sem vogal no meio.",
          "PRATO", "o prato está em todas as casas; o encontro PR é estável e fácil de ancorar.",
          [("BR", "A"), ("BR", "O"), ("CR", "A"), ("CR", "O"), ("DR", "A"), ("FR", "A"), ("FR", "O"), ("GR", "A"), ("PR", "A"), ("PR", "O"), ("TR", "A"), ("VR", "A")],
          ["braço", "prato", "trem", "fruta", "grade", "cravo", "dragão", "livro"],
          ["O braço dói hoje.", "O prato tem fruta.", "O trem chega cedo.", "O dragão cuspiu fogo."],
          "BR", "BRA", "BRO",
          "Escrever uma receita simples usando palavras com encontros consonantais (ex.: brigadeiro com BR).",
          "Peça leitura lenta dos encontros (B-R-A) e depois rápida (BRA); o automatismo vem do treino diário Kumon.",
          proxima=6,
          dominio="Leitura e Fluência",
          auto=_auto("BR/CR/DR/FR/GR/PR/TR"),
          indicadores=_ind(),
          encaminhamento=_enc("Ficha 1 (Dislexia)")),
        U(6, "Encontros Consonantais (2): BL, CL, FL, GL, PL, TL",
          "Os encontros consonantais com L",
          "EF02LP04", "BL, CL, FL, GL, PL e TL são encontros com L: blusa, claro, flor, globo, placa, atlas. As duas consoantes se pronunciam juntas.",
          "Em BL, os lábios fecham (B) e a língua sobe no L: o som desliza. Compare BLA com BA: o L é a segunda consoante.",
          "FLOR", "a flor é visual e afetiva; o encontro FL aparece em um dos primeiros desenhos de toda criança.",
          [("BL", "A"), ("BL", "O"), ("CL", "A"), ("CL", "O"), ("FL", "A"), ("FL", "O"), ("GL", "O"), ("PL", "A"), ("PL", "O"), ("TL", "A")],
          ["blusa", "claro", "flor", "globo", "placa", "atlas", "planta", "flauta"],
          ["A blusa é azul.", "O céu está claro.", "A flor abriu no jardim.", "A placa indica o caminho."],
          "BL", "BLA", "BLO",
          "Descrever um jardim usando palavras com FL e PL.",
          "BL é o mais frequente; alunos que trocam BL por B precisam de repetição com espelho e do apoio do Registro.",
          proxima=7),
        U(7, "RR e SS", "Os digrafos RR e SS entre vogais",
          "EF02LP07", "RR e SS aparecem ENTRE vogais: carro, terra, pasar, osso. Entre vogais, R simples tem som fraco e RR tem som forte.",
          "O R forte (RR) faz a língua vibrar atrás dos dentes; o S forte (SS) produz o som de cobra, com o ar passando com atrito.",
          "CARRO", "o carro é brinquedo universal; a dupla RR fixa a regra de que entre vogais o R forte se escreve RR.",
          [("RR", "A"), ("RR", "O"), ("RR", "E"), ("SS", "A"), ("SS", "O"), ("SS", "E")],
          ["carro", "terra", "barro", "sorriso", "passar", "osso", "assado", "morro"],
          ["O carro andou na terra.", "O sorriso da menina é bonito.", "O osso é do cachorro.", "O frango assado está quente."],
          "RR", "RRA", "RRO",
          "Escrever uma lista de lugares e objetos que tenham RR ou SS.",
          "Mostre o contraste R (muro) × RR (morro) no espelho; o som forte de RR usa mais vibração da língua.",
          proxima=8,
          dominio="Escrita e Ortografia",
          auto=_auto("RR/SS"),
          indicadores=_ind(),
          encaminhamento=_enc("Ficha 2 (Disortografia)")),
        U(8, "S, SS e Z", "O som de S, o som de Z e as grafias entre vogais",
          "EF02LP07", "Entre vogais, S tem som de Z: casa, mesa, asa. Z representa o som de Z: zero, zebra. SS, entre vogais, tem som de S forte.",
          "O Z faz vibrar a voz com o ar passando; o S entre vogais vira Z; o SS mantém o som de cobra. Compare ZA, SA e SSA.",
          "CASA", "a casa é a primeira palavra com S entre vogais que a criança reconhece; o som de Z nela surpreende e fixa a regra.",
          [("Z", "A"), ("Z", "E"), ("Z", "I"), ("Z", "O"), ("Z", "U"),
           ("S", "A"), ("S", "E"), ("S", "I")],
          ["casa", "mesa", "asa", "razão", "zero", "zebra", "poesia", "visita"],
          ["A casa é na rua da escola.", "A mesa tem quatro cadeiras.", "A zebra corre na savana.", "A poesia é bonita."],
          "S/Z", "SA", "ZA",
          "Escrever uma poesia curta usando palavras com S entre vogais.",
          "A regra 'S entre vogais soa como Z' é a mais frutífera do 2º ano; trabalhe em duplas de palavras (casa/caça).",
          proxima=9),
        U(9, "A Letra Ç", "O som de Ç e os usos da cedilha",
          "EF02LP07", "Ç representa o som de S e aparece antes de A, O, U: coração, cabeça, açúcar. Nunca antes de E ou I.",
          "O cê-cedilha tem uma perninha que muda o som de K para S. Compare CA (K) com ÇA (S): a boca muda o gesto? O som muda.",
          "CORAÇÃO", "o coração é a palavra mais afetiva do mundo infantil; fixa ÇA, ÇO e ÇU com til.",
          ["ÇA", "ÇO", "ÇU"],
          ["coração", "caçarola", "açúcar", "poço", "peça", "laço", "cabeça", "maçã"],
          ["O coração bate forte.", "O açúcar adoça o café.", "A cabeça dói um pouco.", "A menina ganhou um laço."],
          "Ç", "ÇA", "ÇO",
          "Escrever três objetos de cozinha que tenham Ç (panelas, caçarola...) e usá-los em frases.",
          "Ç é um excelente porta de entrada para a ortografia: a regra (A, O, U) é simples e o som é previsível.",
          proxima=10,
          dominio="Escrita e Ortografia",
          auto=_auto("Ç"),
          indicadores=_ind(),
          encaminhamento=_enc("Ficha 2 (Disortografia)")),
        U(10, "Ortografia AM e AN", "As grafias AM e AN no final e no meio de palavras",
          "EF02LP04", "AM e AN representam sílabas nasais: sambar, também, campo, dança. No final de verbos, escreve-se AM: eles cantam.",
          "Ao dizer AM, os lábios fecham no M e o ar sai pelo nariz; ao dizer AN, a língua toca atrás dos dentes e o ar sai pelo nariz.",
          "TAMBÉM", "também é uma palavra comum e funcional; a sílaba final BÉM mostra o AM nasal de forma clara.",
          ["MA", "MB", "BA", "AM", "AN", "CAN", "SAN", "TAM"],
          ["também", "sambar", "canto", "sangue", "banco", "campo", "dança", "lanche"],
          ["Eu também quero lanche.", "O canto da sala é azul.", "O banco está na praça.", "A dança começa já."],
          "AM/AN", "AM", "AN",
          "Escrever verbos no presente que terminam em AM (cantam, brincam) e usá-los em frases.",
          "AM/AN é a porta para a morfologia: 'eles cantam' com AM ensina que a escrita do verbo não depende do som apenas.",
          proxima=11),
        U(11, "Palavras com X", "Os sons do X: CH, Z, KS e SS",
          "EF02LP04", "X tem quatro sons possíveis: CH (xadrez), Z (exame), KS (táxi) e S (texto). O contexto decide; a leitura oral ajuda.",
          "O X não tem boca própria: ele 'empresta' o som. Ao ler, experimente os quatro sons até a palavra fazer sentido.",
          "XADREZ", "o xadrez é lúdico e permite explorar o X com som de CH em uma palavra de jogo.",
          ["XE", "XI", "XA", "XO", "XU"],
          ["xadrez", "peixe", "caixa", "exame", "táxi", "xícara", "enxada", "luxo"],
          ["O peixe nada no aquário.", "A caixa tem brinquedos.", "O táxi parou na esquina.", "A xícara está cheia."],
          "X", "XA", "XE",
          "Escrever uma lista de palavras com X e marcar com qual som cada uma se pronuncia.",
          "Não force a regra antes do tempo: a leitura por tentativa (e erro corrigido) é o caminho; o X é polissêmico.",
          proxima=12),
        U(12, "Revisão Geral e Fluência", "Leitura de texto curto com todas as grafias do ano",
          "EF02LP10", "Nesta unidade, o aluno lê um texto curto com fluência, localiza informações e produz uma resposta escrita.",
          "A leitura fluente usa todas as Boquinhas do ano: o aluno percebe que já conhece os sons e lê com ritmo.",
          "BIBLIOTECA", "a biblioteca reúne os aprendizados: ler com prazer é o objetivo final do 2º ano.",
          ["LEI", "TEX", "TO", "FLU"],
          ["biblioteca", "leitura", "estante", "revista", "história", "capítulo", "autor", "página"],
          ["A biblioteca da escola é grande.", "Eu leio um capítulo por dia.", "A história é de um coelho.", "O autor assinou o livro."],
          "LEITURA", "LEI", "TEX",
          "Produzir um pequeno texto de opinião: qual foi o livro favorito do ano e por quê?",
          "Use a fluência como meta: rum, não velocidade. A entonação correta indica compreensão; registre no Registro de Progresso.",
          proxima=None,
          dominio="Leitura, Fluência e Aprendizagem Geral",
          auto=["Leio o texto com fluência", "Localizo informações no texto", "Produzo respostas por escrito", "Gosto de ler em voz alta"],
          indicadores=["Lê texto curto com fluência e entonação", "Compreende o que leu em perguntas orais", "Generaliza as grafias do ano em escrita espontânea", "Progresso sustentado nas folhas Kumon", "Curva de aprendizagem consistente"],
          encaminhamento=_enc("Ficha 1 (Dislexia) e Ficha 25 (sinais escolares de DI leve)")),
    ],
    "kumon": [],
    "sons": [],
    "avaliacoes": [],
}

# Folhas Kumon E-01..E-28
_K = []
def _k(id, titulo, alvo, grafia, nivel, bncc, palavras, frases):
    d = {"id": id, "titulo": titulo, "alvo": alvo, "grafia": grafia,
         "nivel": nivel, "bncc": bncc, "palavras": palavras, "frases": frases}
    _K.append(d)
    return d

_k("E-01", "Dígrafo CH", "CH", "CH", "Silábico-Alfabético", "EF02LP03",
  ["chave", "chapéu", "chuva", "chão", "cheiro", "choro", "fecho", "chá"],
  ["A chave abriu a porta.", "A chuva molhou o chão.", "O chapéu é azul.", "Sinto o cheiro do bolo."])
_k("E-02", "Dígrafo LH", "LH", "LH", "Silábico-Alfabético", "EF02LP03",
  ["ilha", "coelho", "orelha", "milho", "filho", "folha", "velho", "telhado"],
  ["O coelho comeu a folha.", "O filho mora na ilha.", "A orelha é grande.", "O velho subiu no telhado."])
_k("E-03", "Dígrafo NH", "NH", "NH", "Silábico-Alfabético", "EF02LP03",
  ["ninho", "banho", "sonho", "pinho", "galinha", "minhoca", "caminho", "vinho"],
  ["O ninho tem três ovos.", "Tomo banho de manhã.", "A galinha cisca no caminho.", "Eu sonho com o mar."])
_k("E-04", "QUE e QUI", "QU", "QUE", "Silábico-Alfabético", "EF02LP07",
  ["queijo", "quilo", "quente", "quero", "periquito", "aquilo", "máquina", "queixo"],
  ["O queijo está na mesa.", "Eu quero um quilo de pão.", "O periquito canta.", "A máquina lavou a roupa."])
_k("E-05", "GUE e GUI", "GU", "GUE", "Silábico-Alfabético", "EF02LP07",
  ["guerra", "guia", "guitarra", "água", "guelra", "guitarra", "seguir", "figueira"],
  ["A água está quente.", "A guitarra toca na festa.", "O guia mostrou o caminho.", "Seguir o mapa é fácil."])
_k("E-06", "Encontro BR", "BR", "BRA", "Silábico-Alfabético", "EF02LP04",
  ["braço", "briga", "brilho", "brincar", "livro", "abrir", "cabra", "sobrancelha"],
  ["O braço dói hoje.", "O livro está aberto.", "A cabra comeu a folha.", "Vamos brincar no parque."])
_k("E-07", "Encontro CR", "CR", "CRA", "Silábico-Alfabético", "EF02LP04",
  ["cravo", "crédito", "criar", "criança", "macaco", "cruzeiro", "escrever", "cruz"],
  ["O cravo é uma flor.", "A criança gosta de criar.", "Escrever é aprender.", "A cruz fica na praça."])
_k("E-08", "Encontro DR", "DR", "DRA", "Silábico-Alfabético", "EF02LP04",
  ["dragão", "madre", "padrão", "drama", "pedra", "quadro", "comprar", "drible"],
  ["O dragão cuspiu fogo.", "A pedra é pesada.", "O quadro está na parede.", "O jogador fez o drible."])
_k("E-09", "Encontro FR", "FR", "FRA", "Silábico-Alfabético", "EF02LP04",
  ["fruta", "frio", "frente", "fritar", "café", "freio", "franja", "frango"],
  ["A fruta está madura.", "Hoje está frio.", "O frango assado cheira bem.", "A franja cobre os olhos."])
_k("E-10", "Encontro GR", "GR", "GRA", "Silábico-Alfabético", "EF02LP04",
  ["grade", "grande", "grama", "grato", "grilo", "grupo", "igual", "engraçado"],
  ["A grade protege o jardim.", "O elefante é grande.", "O grilo canta à noite.", "A grama ficou verde."])
_k("E-11", "Encontro PR", "PR", "PRA", "Silábico-Alfabético", "EF02LP04",
  ["prato", "primo", "praça", "prêmio", "sempre", "príncipe", "preto", "prova"],
  ["O prato tem fruta.", "O primo mora longe.", "A praça é bonita.", "O príncipe sorriu."])
_k("E-12", "Encontro TR", "TR", "TRA", "Silábico-Alfabético", "EF02LP04",
  ["trem", "trator", "triste", "troca", "letra", "outro", "trança", "três"],
  ["O trem chega cedo.", "O trator arou a terra.", "A letra é bonita.", "O outro menino chegou."])
_k("E-13", "Encontro VR", "VR", "VRA", "Silábico-Alfabético", "EF02LP04",
  ["livro", "palavra", "lavrar", "livre", "cobrir", "descobrir", "nevralgia", "vréu"],
  ["O livro é meu.", "A palavra é longa.", "Descobrir é divertido.", "O pássaro está livre."])
_k("E-14", "Encontro BL", "BL", "BLA", "Silábico-Alfabético", "EF02LP04",
  ["blusa", "bloco", "branco", "branco", "biblioteca", "obrigado", "bloqueio", "blasfêmia"],
  ["A blusa é azul.", "O bloco caiu no chão.", "A biblioteca é grande.", "Muito obrigado pela ajuda."])
_k("E-15", "Encontro CL", "CL", "CLA", "Silábico-Alfabético", "EF02LP04",
  ["claro", "clube", "clima", "classe", "chave", "cloche", "concluir", "clínica"],
  ["O céu está claro.", "O clube fica perto.", "A classe é quieta.", "O clima mudou hoje."])
_k("E-16", "Encontro FL", "FL", "FLA", "Silábico-Alfabético", "EF02LP04",
  ["flor", "flauta", "floco", "floresta", "flamingo", "flecha", "inflar", "flexão"],
  ["A flor abriu no jardim.", "A flauta toca doce.", "A floresta é verde.", "O floco caiu devagar."])
_k("E-17", "Encontro GL", "GL", "GLA", "Silábico-Alfabético", "EF02LP04",
  ["globo", "glória", "glicose", "inglês", "gladíolo", "regra", "clique", "inglês"],
  ["O globo mostra o mapa.", "A glória do time é grande.", "Glicose é açúcar no sangue.", "Ele estuda inglês."])
_k("E-18", "Encontro PL", "PL", "PLA", "Silábico-Alfabético", "EF02LP04",
  ["placa", "planta", "plano", "plástico", "soplar", "pluma", "completo", "aplicar"],
  ["A placa indica o caminho.", "A planta cresceu.", "O plano é simples.", "A pluma é leve."])
_k("E-19", "Dígrafo RR", "RR", "RRA", "Silábico-Alfabético", "EF02LP07",
  ["carro", "terra", "barro", "sorriso", "morro", "serra", "guerra", "arroz"],
  ["O carro andou na terra.", "O barro sujou o sapato.", "O sorriso é bonito.", "O arroz está quente."])
_k("E-20", "Dígrafo SS", "SS", "SSA", "Silábico-Alfabético", "EF02LP07",
  ["passar", "osso", "assado", "pássaro", "massa", "sossego", "professora", "excursão"],
  ["O pássaro cantou cedo.", "O osso é do cachorro.", "A massa do bolo ficou pronta.", "A professora explicou."])
_k("E-21", "S entre vogais e Z", "S/Z", "SA", "Silábico-Alfabético", "EF02LP07",
  ["casa", "mesa", "asa", "poesia", "zero", "zebra", "razão", "visitante"],
  ["A casa é na rua da escola.", "A mesa tem quatro cadeiras.", "A zebra corre na savana.", "A poesia é bonita."])
_k("E-22", "Letra Ç", "Ç", "ÇA", "Silábico-Alfabético", "EF02LP07",
  ["coração", "caçarola", "açúcar", "poço", "peça", "laço", "cabeça", "maçã"],
  ["O coração bate forte.", "O açúcar adoça o café.", "A cabeça dói um pouco.", "A menina ganhou um laço."])
_k("E-23", "Sílabas AM", "AM", "AM", "Silábico-Alfabético", "EF02LP04",
  ["também", "sambar", "cama", "chamar", "cantam", "brincam", "falam", "lamber"],
  ["Eu também quero lanche.", "As crianças brincam no pátio.", "Os meninos cantam na festa.", "O gato gosta de lamber."])
_k("E-24", "Sílabas AN", "AN", "AN", "Silábico-Alfabético", "EF02LP04",
  ["canto", "sangue", "banco", "campo", "dança", "lanche", "banana", "tangerina"],
  ["O canto da sala é azul.", "O banco está na praça.", "A dança começa já.", "A banana é madura."])
_k("E-25", "X com som de CH", "X", "XA", "Silábico-Alfabético", "EF02LP04",
  ["xadrez", "peixe", "caixa", "xícara", "enxada", "abacaxi", "lixeira", "xarope"],
  ["O peixe nada no aquário.", "A caixa tem brinquedos.", "O abacaxi é doce.", "A xícara está cheia."])
_k("E-26", "X com som de Z", "X", "XE", "Silábico-Alfabético", "EF02LP04",
  ["exame", "exemplo", "exato", "executar", "exército", "exílio", "excluir", "extrato"],
  ["O exame foi fácil.", "O exemplo ajudou a turma.", "O exército desfilou.", "Executar a tarefa é simples."])
_k("E-27", "X com som de KS", "X", "XA", "Silábico-Alfabético", "EF02LP04",
  ["táxi", "fixo", "saxofone", "oxigênio", "tóxico", "ônix", "reflexo", "clímax"],
  ["O táxi parou na esquina.", "O saxofone toca jazz.", "O oxigênio é essencial.", "O reflexo está no espelho."])
_k("E-28", "Revisão das Grafias do Ano", "TODAS", "GRAFIA", "Silábico-Alfabético", "EF02LP10",
  ["chave", "coelho", "ninho", "queijo", "carro", "casa", "coração", "biblioteca"],
  ["A chave abriu o cofre.", "O coelho correu no jardim.", "O carro parou na rua.", "A biblioteca tem muitos livros."])
_k("E-29", "Revisão CH, LH e NH", "CH/LH/NH", "CHA", "Silábico-Alfabético", "EF02LP03",
  ["chuva", "coelho", "ninho", "chave", "galinha", "folha", "sonho", "chapéu"],
  ["A chuva molhou o ninho.", "O coelho escondeu-se na folha.", "A galinha sonha com o milho.", "O chapéu do velho é preto."])
_k("E-30", "Revisão QUE, QUI, GUE, GUI", "QU/GU", "QUE", "Silábico-Alfabético", "EF02LP07",
  ["queijo", "quilo", "quente", "guerra", "guia", "guitarra", "água", "periquito"],
  ["O queijo está com o periquito.", "Eu quero um quilo de água.", "A guerra acabou no vale.", "O guia toca guitarra."])
_k("E-31", "Revisão Encontros 1 (B–G)", "BR/CR/DR/FR/GR", "BRA", "Silábico-Alfabético", "EF02LP04",
  ["braço", "cravo", "dragão", "fruta", "grade", "prato", "trem", "livro"],
  ["O braço segura o cravo.", "O dragão comeu a fruta.", "A grade protege o prato.", "O trem leva o livro."])
_k("E-32", "Revisão Encontros 2 (L)", "BL/CL/FL/GL/PL/TL", "BLA", "Silábico-Alfabético", "EF02LP04",
  ["blusa", "claro", "flor", "globo", "placa", "atlas", "planta", "flauta"],
  ["A blusa clara tem flor.", "O globo está sobre o atlas.", "A placa mostra a planta.", "A flauta toca no vento."])
_k("E-33", "Revisão RR e SS", "RR/SS", "RRA", "Silábico-Alfabético", "EF02LP07",
  ["carro", "terra", "barro", "sorriso", "passar", "osso", "assado", "morro"],
  ["O carro andou na terra barrenta.", "O sorriso dela é bonito.", "O osso passou do ponto.", "O assado está no morro."])
_k("E-34", "Revisão S, Z e Ç", "S/Z/Ç", "SA", "Silábico-Alfabético", "EF02LP07",
  ["casa", "mesa", "zero", "zebra", "coração", "açúcar", "laço", "maçã"],
  ["A casa da zebra é perto da mesa.", "O zero é redondo como o laço.", "O açúcar adoça a maçã.", "O coração está no poço."])
_k("E-35", "Revisão AM e AN", "AM/AN", "AM", "Silábico-Alfabético", "EF02LP04",
  ["também", "sambar", "canto", "sangue", "banco", "campo", "dança", "banana"],
  ["Eu também quero sambar no canto.", "O banco fica no campo.", "A dança da banana é alegre.", "O sangue circula no corpo."])
_k("E-36", "Revisão X", "X", "XA", "Silábico-Alfabético", "EF02LP04",
  ["xadrez", "peixe", "caixa", "exame", "táxi", "xícara", "enxada", "texto"],
  ["O peixe está na caixa do táxi.", "O xadrez é um jogo de atenção.", "A xícara suja o texto.", "O exame foi na enxada."])
_k("E-37", "Leitura de Frases 1", "FLUÊNCIA", "LEI", "Silábico-Alfabético", "EF02LP10",
  ["chuva", "coelho", "trem", "flor", "casa", "carro", "ninho", "poema"],
  ["A chuva cai no telhado do coelho.", "O trem passa pela casa de flor.", "O carro para no ninho da rua.", "O poema fala da chuva."])
_k("E-38", "Leitura de Frases 2", "FLUÊNCIA", "LEI", "Silábico-Alfabético", "EF02LP10",
  ["biblioteca", "história", "capítulo", "autor", "página", "revista", "estante", "leitura"],
  ["A biblioteca guarda a história.", "O capítulo novo começa na página 10.", "O autor assinou a revista.", "A estante tem leitura para todos."])
_k("E-39", "Ditado das Grafias do Ano", "DITADO", "GRAFIA", "Silábico-Alfabético", "EF02LP07",
  ["chave", "coelho", "ninho", "queijo", "carro", "casa", "coração", "biblioteca"],
  ["A chave abre o cofre do coelho.", "O ninho do queijo é de palha.", "O carro leva a casa do coração.", "A biblioteca guarda a chave do saber."])
_k("E-40", "Prova de Fluência Leitora", "FLUÊNCIA", "LEI", "Silábico-Alfabético", "EF02LP10",
  ["leitura", "fluência", "entonação", "precisão", "ritmo", "expressividade", "compreensão", "prazer"],
  ["A leitura com fluência tem ritmo e entonação.", "A precisão vem do treino diário.", "A expressividade dá vida ao texto.", "A compreensão transforma a leitura em prazer."])
VOLUME2["kumon"] = _K

# Sons — 36 atividades
VOLUME2["sons"] = [
    {"id": i + 1, "titulo": t, "texto": tex}
    for i, (t, tex) in enumerate([
        ("Fonema CH em posição inicial", "Peça que o aluno fale devagar: CHA, CHE, CHI, CHO, CHU. Circule todas as figuras que começam com o som de CH."),
        ("Fonema CH em posição medial", "Diga a palavra CHUVEIRO e peça que o aluno bata palmas a cada sílaba: CHU-VEI-RO. Agora encontre outras palavras com CH no meio."),
        ("Fonema LH em posição medial", "Diga COELHO e peça que o aluno sinta a língua no céu da boca. Escreva palavras com LH que tenham o som lateral."),
        ("Fonema NH em posição medial", "Diga NINHO e peça que o aluno feche a boca ao final (som nasal). Liste palavras com NH que tenham este gesto."),
        ("Contraste NH × LH", "Compare NINHO (ar sai pelo nariz) com MILHO (ar sai lateral). Diga as duas palavras e peça que o aluno diga qual é qual."),
        ("QUE e QUI: o U mudo", "Diga QUEIJO sem dizer o U: QUE. Compare com QUERO (QUE) e QUILO (QUI). A criança deve perceber que o U não é pronunciado."),
        ("GUE e GUI: o U mudo", "Diga GUERRA sem dizer o U: GUE. Compare com GUITARRA (GUI). Marque as palavras em que o U não é pronunciado."),
        ("Encontro BR em sílabas", "Diga BRA devagar: B-R-A. Repita mais rápido até virar BRA. Faça o mesmo com BRE, BRI, BRO, BRU."),
        ("Encontro CR em sílabas", "Diga CRA devagar: C-R-A. Repita mais rápido até virar CRA. O que mudou entre CA e CRA? O R entrou no meio."),
        ("Encontro DR em sílabas", "Diga DRA devagar: D-R-A. Repita mais rápido. Compare DAMA com DRAMA: o que o R fez?"),
        ("Encontro FR em sílabas", "Diga FRA devagar: F-R-A. Repita mais rápido. Encontre palavras que começam com FRA, FRE, FRI, FRO, FRU."),
        ("Encontro GR em sílabas", "Diga GRA devagar: G-R-A. Repita mais rápido. O que mudou entre GA e GRA?"),
        ("Encontro PR em sílabas", "Diga PRA devagar: P-R-A. Repita mais rápido. Compare PATO com PRATO: o que o R fez?"),
        ("Encontro TR em sílabas", "Diga TRA devagar: T-R-A. Repita mais rápido. Compare TAPA com TRAPA: existe TRAPA?"),
        ("Encontro VR em sílabas", "Diga VRA devagar: V-R-A. Repita mais rápido. Encontre LIVRO e PALAVRA: onde está o VR?"),
        ("Encontro BL em sílabas", "Diga BLA devagar: B-L-A. Repita mais rápido. O L vem logo depois do B, sem vogal no meio."),
        ("Encontro CL em sílabas", "Diga CLA devagar: C-L-A. Repita mais rápido. Compare CASA com CLASSE: o L mudou o som?"),
        ("Encontro FL em sílabas", "Diga FLA devagar: F-L-A. Repita mais rápido. FLOR e FLAUTA: onde está o FL?"),
        ("Encontro GL em sílabas", "Diga GLA devagar: G-L-A. Repita mais rápido. GLOBO e GLÓRIA: onde está o GL?"),
        ("Encontro PL em sílabas", "Diga PLA devagar: P-L-A. Repita mais rápido. PLACA e PLANTA: onde está o PL?"),
        ("R forte e R fraco", "Compare CARA (R fraco) com CARRO (R forte). Diga as palavras e circule onde o R vibra mais."),
        ("SS entre vogais", "Compare CASA (S com som de Z) com PASSA (SS com som de S). O SS sempre mantém o som de cobra."),
        ("S entre vogais com som de Z", "Diga CASA, MESA, ASA. Perceba: o S ficou com som de Z. Esta é uma das regras mais importantes do ano."),
        ("Z em posição inicial", "Diga ZERO, ZEBRA, ZÍPER. O Z é uma letra que 'liga' a voz. Escreva outras palavras com Z."),
        ("Ç em palavras", "Diga CORAÇÃO, AÇÚCAR, LAÇO. O Ç tem som de S. Escreva palavras com ÇA, ÇO, ÇU."),
        ("AM nasal no final", "Diga CANTAM, FALAM, BRINCAM. O AM final é a desinência de 'eles'. Sinta o nariz vibrar."),
        ("AN nasal no meio", "Diga BANCO, CAMPO, DANÇA. O AN é uma sílaba nasal no meio da palavra."),
        ("X com som de CH", "Diga XADREZ, PEIXE, CAIXA. O X 'veste' o som de CH. Leia e desenhe uma caixa."),
        ("X com som de Z", "Diga EXAME, EXEMPLO. O X 'veste' o som de Z em palavras com EXA, EXE."),
        ("X com som de KS", "Diga TÁXI, SAXOFONE. O X 'veste' os sons de K e S juntos. Como pronunciar FIXO?"),
        ("X com som de SS", "Diga TEXTO, EXTRA. O X 'veste' o som de S. Leia em voz alta e marque a pronúncia."),
        ("Rima e aliteração", "Ouça: CHAVE, CHUVA, CHÃO. Todas começam com o mesmo som. Crie outra série com LH."),
        ("Segmentação silábica avançada", "Diga BIBLIOTECA: BI-BLIO-TE-CA. Quantas sílabas? Agora escreva a palavra e sublinhe o encontro consonantal."),
        ("Posição do som na palavra", "Diga GUITARRA: onde está o som de GUE? No início (GUI), no meio (TA) ou no fim (RRA)?"),
        ("Completar com a grafia certa", "Complete: _AVE (CHAVE), _APÉU (CHAPÉU), _UVA (CHUVA). Agora invente você mais três."),
        ("Ditado de grafias do ano", "Faça o ditado: queijo, coelho, ninho, carro, casa, coração. Corrija com o aluno e registre os acertos."),
        ("Subtração de fonema em encontros", "Diga PRATO e retire o R: PATO. Diga FRIO e retire o R: FIO. Diga BLUSA e retire o L: BUSA? Teste e perceba: nem sempre a palavra continua existindo."),
        ("Rimas avançadas", "Encontre rimas: CHUVA (LUVA), PRATO (GATO), TRILHO (MILHO), FLOR (AMOR), CAIXA (FAIXA). Crie uma quadrinha com uma das rimas."),
        ("Aliteração em cadeia", "Crie uma frase em que todas as palavras comecem com o mesmo som: 'O coelho comeu cenoura no campo' (c). Depois com CH: 'A chuva chovera chão'."),
        ("Contagem de fonemas", "Conte os fonemas (sons) de: CHAVE (4), PRATO (5), FLOR (4), CASA (4), QUEIJO (5). Compare com o número de letras."),
        ("Ordem dos sons", "Diga PRATO e responda: qual é o 1º som? (P) E o 2º? (R) E o 3º? (A). Faça o mesmo com TREM e FLOR."),
        ("Associação som-grafia final", "Ouça o som e escolha a grafia: /tʃ/ pode ser CH ou X (chave, xícara). /s/ pode ser S, Ç, SS ou X (sapo, coração, passar, texto). Registre por escrito suas escolhas."),
    ])
]

# Avaliações — 3
VOLUME2["avaliacoes"] = [
    {
        "titulo": "Avaliação Diagnóstica — Início do 2º Ano",
        "criterios": "Objetivo: verificar a consolidação da base alfabética (sílabas simples, vogais) e a prontidão para os dígrafos. Aplicação individual ou em pequenos grupos, 30 minutos.",
        "questoes": [
            "Leia em voz alta as sílabas e escreva ao lado o que você leu: MA  SA  TA  LA  PA.",
            "Complete as palavras com a vogal que falta: m_te (maté), s_p_ (sapo), f_ra (fada).",
            "Separe em sílabas e escreva o número de sílabas: BOLA, CASACA, MONTANHA.",
            "Circule as palavras que terminam com o mesmo som: CHAVE e CAVE? CHUVA e BUVA? LHE e LE?",
            "Escreva uma frase usando a palavra NINHO.",
            "Leia o texto curto: 'O pato nada no lago.' e desenhe o que você entendeu.",
        ],
        "gabarito": [
            ("Q1", "MA, SA, TA, LA, PA", "Decodificação de sílabas diretas consolidadas"),
            ("Q2", "maté/sapo/fada", "Identificação de vogais em palavras"),
            ("Q3", "2, 3, 3 sílabas", "Segmentação silábica"),
            ("Q4", "CHAVE (som /tʃ/)", "Consciência do som-alvo"),
            ("Q5", "Frase com NINHO", "Produção escrita com palavras do ano"),
            ("Q6", "Desenho coerente", "Compreensão leitora inicial"),
        ],
    },
    {
        "titulo": "Avaliação Formativa — Meio do 2º Ano",
        "criterios": "Objetivo: verificar os dígrafos CH, LH, NH e os encontros consonantais. 40 minutos, aplicação coletiva com leitura oral individual.",
        "questoes": [
            "Forme sílabas com CH e escreva 3 palavras: CH+_, CH+_, CH+_.",
            "Complete com LH ou NH: coel_o, ni_ho, ora_ha, gali_a.",
            "Circule os encontros consonantais e leia: BRA, CRA, DRA, FRA, GRA, PRA, TRA.",
            "Escreva 3 palavras com BR e 3 palavras com TR.",
            "Leia a frase e sublinhe as palavras com encontro consonantal: 'O prato tem fruta e o trem chega cedo.'",
            "Separe em sílabas: PRATO, DRAGÃO, FLORESTA, GLOBO.",
        ],
        "gabarito": [
            ("Q1", "CHA CHE CHI CHO CHU + palavras", "Produção com dígrafo CH"),
            ("Q2", "coelho, ninho, orelha, galinha", "Ortografia LH/NH"),
            ("Q3", "Encontros identificados", "Reconhecimento de encontros"),
            ("Q4", "Palavras com BR e TR", "Produção de palavras com encontros"),
            ("Q5", "PRATO, FRUTA, TREM", "Leitura e identificação em contexto"),
            ("Q6", "PRA-TO, DRA-GÃO, FLO-RES-TA, GLO-BO", "Segmentação de encontros"),
        ],
    },
    {
        "titulo": "Avaliação Somativa — Fim do 2º Ano",
        "criterios": "Objetivo: verificar as grafias RR, SS, S/Z, Ç, AM/AN e X, além da fluência em texto curto. 50 minutos.",
        "questoes": [
            "Complete com RR ou R: ca_o, te_a, mo_o, co_o (corro).",
            "Complete com S, SS ou Z: ca_a (casa), ca_a (caça), pa_ar (passar), me_a (mesa).",
            "Complete com Ç, C ou S: cora_ão, _apéu, _alinha, _açarola.",
            "Complete com AM ou AN: cant__, brinc__, s__gue, c__po.",
            "Leia o texto: 'O carro passou na estrada. A professora sorriu. O pássaro cantou.' e responda: o que passou na estrada?",
            "Escreva uma história curta (4 frases) usando pelo menos uma palavra com CH, uma com NH e uma com RR.",
        ],
        "gabarito": [
            ("Q1", "carro, terra, morro, corro", "Ortografia RR"),
            ("Q2", "casa, caça, passar, mesa", "S entre vogais, SS e Z"),
            ("Q3", "coração, chapéu, galinha, caçarola", "Ç e dígrafos"),
            ("Q4", "cantam, brincam, sangue, campo", "AM/AN"),
            ("Q5", "O carro", "Compreensão leitora"),
            ("Q6", "Produção com grafias do ano", "Escrita espontânea"),
        ],
    },
]

VOLUME2["avaliacoes"] += [
    {
        "titulo": "Avaliação de Consciência Fonológica — 2º Trimestre",
        "criterios": "Objetivo: verificar a consciência silábica e fonêmica avançada (subtração, rima, aliteração e contagem de sons). Aplicação individual, 25 minutos, com apoio oral.",
        "questoes": [
            "Suba as sílabas e escreva: BOLACHA, CHUVEIRO, COELHO.",
            "Retire o R de PRATO e escreva a palavra que sobra (PATO). Agora retire o L de BLOCO e escreva o que sobra (BOCA).",
            "Encontre a rima: CHUVA rima com? ( ) CAVE ( ) LUVA ( ) FOCA",
            "Diga o 1º som de PRATO e o 1º som de FLOR.",
            "Quantos sons tem CASA? ( ) 3 ( ) 4 ( ) 5",
            "Fale uma frase em que todas as palavras começam com CH.",
            "Separe os fonemas de CHAVE e de TREM, batendo palmas para cada som.",
            "Qual palavra começa com o mesmo som de QUEIJO? ( ) GATO ( ) QUILO ( ) CASA",
        ],
        "gabarito": [
            ("Q1", "BO-LA-CHA, CHU-VEI-RO, CO-E-LHO", "Segmentação silábica"),
            ("Q2", "PATO, BOCA", "Subtração de fonema em encontro consonantal"),
            ("Q3", "LUVA", "Consciência de rima"),
            ("Q4", "/p/ e /f/", "Identificação do som inicial"),
            ("Q5", "4 (c-a-s-a)", "Contagem de fonemas"),
            ("Q6", "Frase com aliteração em CH", "Aliteração"),
            ("Q7", "4 e 4 fonemas", "Segmentação em fonemas"),
            ("Q8", "QUILO", "Identificação de som inicial"),
        ],
    },
    {
        "titulo": "Avaliação de Leitura e Compreensão — 3º Trimestre",
        "criterios": "Objetivo: verificar fluência leitora (precisão, ritmo, expressividade) e compreensão de texto curto. Aplicação individual da leitura em voz alta; as questões são respondidas por escrito.",
        "questoes": [
            "Leia em voz alta o texto: 'O carro do vizinho parou na chuva. A professora abriu a porta e sorriu. O menino tirou o chapéu e entrou na escola.'",
            "Quem chegou à escola?",
            "Onde o carro parou?",
            "O que a professora fez ao abrir a porta?",
            "Retire do texto uma palavra com CH.",
            "Retire do texto uma palavra com RR.",
            "Quantas palavras tem a primeira frase do texto?",
            "Qual é a melhor nova frase para continuar a história? Escreva uma.",
        ],
        "gabarito": [
            ("Q1", "Leitura oral com precisão e ritmo", "Fluência"),
            ("Q2", "O menino", "Localização de informação"),
            ("Q3", "Na chuva", "Localização de informação"),
            ("Q4", "Sorriu", "Compreensão"),
            ("Q5", "chapéu ou chuva", "Identificação de grafia em texto"),
            ("Q6", "carro", "Identificação de grafia em texto"),
            ("Q7", "7 palavras", "Análise linguística"),
            ("Q8", "Resposta coerente com o texto", "Produção de continuação"),
        ],
    },
    {
        "titulo": "Avaliação de Produção Escrita — Final do Ano",
        "criterios": "Objetivo: verificar a produção de texto com estrutura (início, meio, fim), ortografia das grafias do ano e legibilidade. 45 minutos; o rascunho é corrigido antes da versão final.",
        "questoes": [
            "Planeje: escolha o tema do seu texto (um dia de chuva, a visita à biblioteca, o passeio com o coelho) e escreva 3 palavras que vai usar.",
            "Escreva o rascunho do texto com, no mínimo, 4 frases. Use uma palavra com CH, uma com NH e uma com RR.",
            "Releia o rascunho: circule as palavras com CH, LH, NH, RR, SS, S entre vogais, Ç, AM/AN e X que você usou.",
            "Corrija a ortografia: troque as grafias erradas usando a regra que aprendeu no ano.",
            "Escreva a versão final em letra cursiva, com margem e parágrafo.",
            "Verifique: comecei com letra maiúscula? Terminei com ponto final? Todo parágrafo tem seu espaço?",
            "Ilustre o seu texto com um desenho.",
            "Apresente o texto para a turma em voz alta, com fluência e expressividade.",
        ],
        "gabarito": [
            ("Q1", "Planejamento com 3 palavras", "Planejamento de escrita"),
            ("Q2", "Texto com 4+ frases e grafias solicitadas", "Produção textual"),
            ("Q3", "Identificação das grafias no próprio texto", "Metacognição ortográfica"),
            ("Q4", "Correção ortográfica com justificativa", "Autorregulação"),
            ("Q5", "Versão final em cursiva legível", "Caligrafia e estrutura"),
            ("Q6", "Autoavaliação respondida", "Autorrevisão"),
            ("Q7", "Ilustração coerente", "Integração multimodal"),
            ("Q8", "Apresentação oral expressiva", "Fluência e expressividade"),
        ],
    },
]

VOLUME2["checkpoints"] = [
    (VOLUME2["unidades"][1], "Ficha 18 (TDL) e Ficha 19 (Desvio Fonológico)"),
    (VOLUME2["unidades"][3], "Ficha 18 (TDL)"),
    (VOLUME2["unidades"][5], "Ficha 1 (Dislexia)"),
    (VOLUME2["unidades"][7], "Ficha 2 (Disortografia)"),
    (VOLUME2["unidades"][9], "Ficha 2 (Disortografia)"),
    (VOLUME2["unidades"][12], "Ficha 1 (Dislexia) e Ficha 25 (sinais escolares de DI leve)"),
]

# Unidades de consolidação e leitura (13–16)
VOLUME2["unidades"] += [
    U(13, "Revisão dos Dígrafos CH, LH e NH", "Consolidar CH, LH e NH em leitura e escrita",
      "EF02LP03", "CH, LH e NH são dígrafos: duas letras, um som. A revisão lembra a boca de cada um e fortalece a leitura e a escrita.",
      "Na revisão, compare as três Boquinhas: CH tem atrito de ar, LH tem língua lateral, NH tem ar pelo nariz. Diga as três palavras-chave: CHUVA, COELHO, NINHO.",
      "COELHO", "o coelho junta LH e o afeto; revisitá-lo amarra a revisão dos três dígrafos.",
      [("CH", "A"), ("CH", "O"), ("LH", "A"), ("LH", "O"), ("NH", "A"), ("NH", "O"), ("CH", "E"), ("NH", "E")],
      ["chuva", "coelho", "ninho", "chave", "galinha", "folha", "sonho", "chapéu"],
      ["A chuva molhou o ninho.", "O coelho escondeu-se na folha.", "A galinha sonha com o milho.", "O chapéu do velho é preto."],
      "CH/LH/NH", "CHA", "LHA",
      "Escrever um pequeno conto de 4 frases usando pelo menos um CH, um LH e um NH.",
      "Use o quadro de contraste das três Boquinhas: a revisão é o momento de separar definitivamente os três sons.",
      proxima=14,
      dominio="Consolidação de Dígrafos"),
    U(14, "Revisão dos Encontros Consonantais", "Consolidar os encontros BR–VR e BL–TL",
      "EF02LP04", "Os encontros consonantais mantêm os dois sons juntos: BRA, CRA, DRA... e BLA, CLA, FLA. A revisão automatiza a leitura.",
      "Na revisão, leia os encontros em cadeia: BRA BRE BRI BRO BRU. Depois os de L: BLA BLE BLI BLO BLU. Sinta a diferença entre o R e o L.",
      "TREM", "o trem junta TR e movimento; é o encontro preferido das crianças.",
      [("BR", "A"), ("PR", "A"), ("TR", "A"), ("GR", "A"), ("FR", "A"), ("CR", "A"), ("DR", "A"), ("VR", "A"), ("BL", "A"), ("CL", "A"), ("FL", "A"), ("GL", "A"), ("PL", "A")],
      ["trem", "prato", "braço", "grade", "fruta", "cravo", "dragão", "flor", "placa", "livro"],
      ["O trem passou pela grade.", "O prato tem fruta e flor.", "O dragão voou sobre a placa.", "O livro tem um cravo na capa."],
      "ENCONTROS", "TRA", "PLA",
      "Escrever uma lista de 6 palavras com encontros consonantais e usá-las em um bilhete.",
      "A revisão dos encontros é o momento do automatismo: leitura em cadeia e jogos de carrinho (BRA-BRE-BRI) fixam o padrão.",
      proxima=15,
      dominio="Leitura e Fluência"),
    U(15, "Revisão Ortográfica: RR, SS, S/Z e Ç", "Consolidar as regras ortográficas do ano",
      "EF02LP07", "Entre vogais: R forte vira RR, S forte vira SS, S vira Z, e Ç aparece antes de A, O, U. A revisão transforma regra em hábito.",
      "Na revisão, compare duplas: CARA/CARRO, CASA/CAÇA, PASSA/PAÇA. A boca mantém o mesmo gesto; a escrita decide pela regra.",
      "CARROÇA", "carroça junta RR e Ç em uma palavra só: a revisão ortográfica completa.",
      [("RR", "A"), ("RR", "O"), ("SS", "A"), ("SS", "O"), "ZA", "CA", "ÇA", "ÇO"],
          ["carroça", "serra", "passa", "assado", "casa", "caça", "laço", "poço"],
          ["A carroça sobe a serra.", "O assado passa do ponto.", "A casa está perto do poço.", "O laço é da festa."],
      "RR/SS/SZ/Ç", "RRA", "CASA",
      "Reescrever 4 frases corrigindo os erros de ortografia (ditado de revisão).",
      "Na revisão, o aluno consulta a regra e justifica a escolha: 'R entre vogais, som forte, escrevo RR'. O hábito vem da justificativa.",
      proxima=16,
      dominio="Escrita e Ortografia"),
    U(16, "Leitura de Gêneros: Poema e Cantiga", "Ler poema e cantiga com fluência e expressividade",
      "EF02LP12", "Poemas e cantigas têm ritmo, rima e repetição. Ler com expressividade mostra que o aluno compreende o texto.",
      "Na leitura de poema, a boca acompanha a música do verso: subir e descer a voz, pausar nas rimas. Ler como quem canta.",
      "CANTIGA", "a cantiga é a memória oral do povo; une leitura, ritmo e alegria.",
      ["CAN", "TIGA", "RIMA", "POE"],
          ["cantiga", "poema", "rima", "estrofe", "verso", "cantor", "melodia", "refrão"],
          ["A cantiga tem uma rima.", "O poema fala do vento.", "O refrão repete a melodia.", "O cantor sorri no verso."],
      "POEMA", "CAN", "RIMA",
      "Recitar um poema curto para a turma e escrever o próprio poema com 2 versos e rima.",
      "A leitura expressiva é a ponte para a fluência: grave a recitação da criança e deixe que ela se ouça; o progresso fica evidente.",
      proxima=None,
      dominio="Fluência Leitora e Compreensão"),
]

# Unidades de leitura de gêneros e consolidação (17–22)
VOLUME2["unidades"] += [
    U(17, "Leitura de Gêneros: Conto", "Ler conto curto, localizar informações e recontar",
      "EF02LP12, EF02LP14", "O conto tem começo, meio e fim; personagens, lugar e um problema. O leitor localiza informações explícitas e recontra a história.",
      "Na leitura de conto, a voz acompanha a emoção: mais rápida no susto, mais lenta na calma. Ler conto é contar com a boca.",
      "FADA", "a fada abre o conto clássico e permite explorar 3 letras já conhecidas com encantamento.",
      ["FA", "DA", "CON", "TO"],
      ["fada", "castelo", "príncipe", "floresta", "tesouro", "magia", "coragem", "aventura"],
      ["A fada mora no castelo.", "O príncipe atravessou a floresta.", "O tesouro está escondido.", "A coragem vence a magia."],
      "CONTO", "FA", "CON",
      "Recontar o conto favorito em 4 frases, com começo, meio e fim.",
      "Leia o conto duas vezes em voz alta: a primeira para compreender, a segunda para recontar; a recontação é a evidência da compreensão.",
      proxima=18),
    U(18, "Leitura de Gêneros: Fábula", "Ler fábula, identificar a moral e relacionar com a vida",
      "EF02LP12", "A fábula é uma história curta com animais que agem como pessoas e termina com uma moral, um ensinamento.",
      "Ao ler a fábula, a boca dá voz aos animais: voz grossa para o leão, leve para o rato. A moral pede leitura pausada.",
      "LEÃO", "o leão é rei das fábulas; ajuda a trabalhar o encontro final e a moral.",
      ["LE", "ÃO", "RA", "TO"],
      ["leão", "rato", "formiga", "cigarra", "moral", "fábula", "corrida", "sabedoria"],
      ["O leão poupou o rato.", "A formiga trabalhou no verão.", "A cigarra cantou no frio.", "A moral ensina a lição."],
      "FÁBULA", "LE", "ÃO",
      "Explicar com suas palavras o que a moral da fábula significa na vida real.",
      "Após a leitura, converse com a turma: 'Já aconteceu algo parecido com você?' A relação com a vida garante a compreensão profunda.",
      proxima=19),
    U(19, "Trava-línguas e Rimas", "Articular claramente com trava-línguas e perceber rimas",
      "EF02LP06", "O trava-língua repete sons parecidos para desafiar a boca: 'O rato roeu a roupa do rei de Roma'. A articulação clara é o objetivo.",
      "No trava-língua, a boca precisa ser rápida e precisa; comece devagar e aumente a velocidade. O espelho ajuda a ver os lábios trabalhando.",
      "RATO", "o rato aparece no trava-língua clássico; a repetição de R treina a vibração.",
      ["RA", "RO", "RUI", "ROM", "RIM"],
      ["rato", "roupa", "rei", "Roma", "roeu", "rápido", "roda", "risada"],
      ["O rato roeu a roupa do rei.", "A roda gira rápido na rua.", "O rei de Roma riu da risada.", "Três pratos de trigo para três tigres."],
      "TRAVA-LÍNGUA", "RA", "RO",
      "Criar o próprio trava-língua com 3 palavras que comecem com o mesmo som.",
      "Grave a criança no trava-língua e reproduza: a autocorreção auditiva é mais eficaz que a correção do professor.",
      proxima=20),
    U(20, "Adivinhas", "Ler adivinhas, deduzir a resposta e justificá-la",
      "EF02LP12", "A adivinha é uma charada em versos: a resposta está escondida nas pistas do texto. Ler as pistas é parte do jogo.",
      "Na adivinha, leia as pistas devagar; a boca destaca as palavras-chave. Depois, responda e justifique: 'por que você acha isso?'",
      "OVO", "o ovo está em adivinhas clássicas ('branco por fora, amarelo por dentro') e a palavra é curta e familiar.",
      ["OVO", "PISTA", "CHAR", "ADA"],
      ["ovo", "pista", "charada", "resposta", "segredo", "palma", "escuro", "claro"],
      ["O ovo tem duas cores.", "A pista esconde a resposta.", "A charada fala do escuro.", "O segredo ficou claro no fim."],
      "ADIVINHA", "OVO", "PIS",
      "Escrever uma adivinha para a turma, usando pelo menos duas pistas.",
      "A adivinha exercita leitura inferencial: o aluno aprende que nem toda resposta está escrita; às vezes está escondida nas pistas.",
      proxima=21),
    U(21, "Gêneros do Cotidiano: Bilhete e Notícia Curta", "Ler e escrever bilhete e notícia curta",
      "EF02LP14, EF02LP15", "O bilhete comunica um recado rápido (para quem, o quê, de quem). A notícia curta informa o que aconteceu, onde e quando.",
      "O bilhete usa frases curtas e claras; a notícia começa com o fato principal. Leia um bilhete de exemplo em voz alta e perceba o tom.",
      "BILLETE", "o bilhete é o primeiro gênero escrito da vida escolar: recados para a família.",
      ["BI", "LHE", "TE", "NO", "TI"],
      ["bilhete", "recado", "notícia", "jornal", "data", "assunto", "destinatário", "remetente"],
      ["O bilhete avisa sobre a reunião.", "A notícia conta o fato de hoje.", "O destinatário lê o recado.", "O remetente assina no fim."],
      "BILHETE", "BI", "NO",
      "Escrever um bilhete para a família avisando sobre o sarau de leitura.",
      "Gêneros do cotidiano conectam a escola à vida: o bilhete escrito pelo aluno e entregue em casa vira evidência autêntica de aprendizagem.",
      proxima=22),
    U(22, "Revisão Final e Sarau de Leitura", "Revisar todas as grafias do ano e apresentar leitura no sarau",
      "EF02LP10", "A revisão final organiza as grafias do ano em um mapa; o sarau celebra a fluência conquistada com leitura expressiva para a turma.",
      "No sarau, a boca é o instrumento da festa: leitura clara, ritmo e emoção. Cada aluno apresenta um texto que escolheu.",
      "SARAU", "o sarau transforma a leitura em celebração: a meta do ano inteiro é ler com prazer em público.",
      ["SA", "RAU", "FESTA", "VOZ"],
      ["sarau", "festa", "poema", "leitura", "palco", "plateia", "aplauso", "memória"],
      ["O sarau tem poema e festa.", "A plateia escuta em silêncio.", "O palco recebe o leitor.", "O aplauso premia a leitura."],
      "SARAU", "SA", "RAU",
      "Apresentar no sarau um texto escolhido, lido com fluência e expressividade.",
      "O sarau é a culminância: celebre cada criança publicamente; a autoestima leitora construída hoje sustenta os anos seguintes.",
      proxima=None,
      dominio="Fluência Leitora, Compreensão e Aprendizagem Geral"),
]

# Folhas Kumon 41–50 (caderno complementar de leitura, escrita e caligrafia)
VOLUME2["kumon"] += [
    _k("E-41", "Caligrafia Cursiva 1", "CURSIVA", "A", "Silábico-Alfabético", "EF02LP10",
       ["chave", "coelho", "ninho", "queijo", "guerra", "carro", "casa", "coração"],
       ["A chave do coelho abriu o ninho.", "A guerra do carro passou na casa.", "O coração do queijo é de gelo.", "A casa do ninho tem telhado."]),
    _k("E-42", "Caligrafia Cursiva 2", "CURSIVA", "B", "Silábico-Alfabético", "EF02LP10",
       ["biblioteca", "estante", "revista", "história", "capítulo", "autor", "página", "leitura"],
       ["A biblioteca da escola tem estante nova.", "A história do capítulo é de um autor famoso.", "A revista abre na página da leitura.", "O autor autografou o livro na estante."]),
    _k("E-43", "Autoditado", "AUTODITADO", "GRAFIA", "Silábico-Alfabético", "EF02LP07",
       ["chave", "coelho", "ninho", "queijo", "guitarra", "carro", "casa", "coração"],
       ["A chave do coelho é dourada.", "O ninho do queijo é de palha.", "A guitarra do carro toca na casa.", "O coração da praça é de concreto."]),
    _k("E-44", "Banco de Palavras", "BANCO", "GRAFIA", "Silábico-Alfabético", "EF02LP03",
       ["chuva", "chapéu", "ilha", "orelha", "banho", "caminho", "queijo", "água"],
       ["A chuva molhou o chapéu.", "A ilha tem a orelha do mapa.", "O banho lava o caminho.", "O queijo bebe a água do rio."]),
    _k("E-45", "Listas e Completar Frases", "LISTA", "GRAFIA", "Silábico-Alfabético", "EF02LP04",
       ["braço", "trem", "fruta", "flor", "placa", "livro", "prato", "claro"],
       ["O braço aponta para o trem.", "A fruta e a flor enfeitam o prato.", "A placa clara mostra o livro.", "O trem carrega a placa da estação."]),
    _k("E-46", "Completar Frases", "FRASES", "GRAFIA", "Silábico-Alfabético", "EF02LP10",
       ["professora", "escola", "amigo", "pátio", "lanche", "quadro", "cadeira", "mochila"],
       ["A professora escreve no quadro da escola.", "O amigo lancha no pátio.", "A mochila fica perto da cadeira.", "O lanche é no recreio da escola."]),
    _k("E-47", "Leitura de Texto Curto 1", "TEXTO", "LEI", "Silábico-Alfabético", "EF02LP10",
       ["chuva", "telhado", "gato", "janela", "café", "mãe", "frio", "casa"],
       ["A chuva cai no telhado.", "O gato olha pela janela.", "A mãe toma café quente.", "A casa fica fria no inverno."]),
    _k("E-48", "Leitura de Texto Curto 2", "TEXTO", "LEI", "Silábico-Alfabético", "EF02LP10",
       ["menino", "pipas", "vento", "campo", "nuvem", "céu", "risada", "tarde"],
       ["O menino solta pipas no campo.", "O vento leva a nuvem pelo céu.", "A risada ecoa na tarde.", "A pipa dança no vento."]),
    _k("E-49", "Produção Guiada", "PRODUÇÃO", "GRAFIA", "Silábico-Alfabético", "EF02LP15",
       ["conto", "fábula", "bilhete", "notícia", "adivinha", "poema", "trava", "sarau"],
       ["O conto virou fábula com moral.", "O bilhete virou notícia no jornal.", "A adivinha virou poema no sarau.", "O trava-língua animou a festa."]),
    _k("E-50", "Revisão Geral Final", "REVISÃO", "GRAFIA", "Silábico-Alfabético", "EF02LP10",
       ["chave", "coelho", "carro", "casa", "coração", "biblioteca", "sarau", "leitura"],
       ["A chave abriu o cofre do coelho.", "O carro levou a casa ao sarau.", "O coração da biblioteca é a leitura.", "A leitura celebra a festa do ano."]),
]

# Sons 43–52 (consciência fonológica avançada)
VOLUME2["sons"] += [
    {"id": 43, "titulo": "Foco articulatório em encontros consonantais", "texto": "Diga BRA, CRA, DRA, FRA, GRA, PRA, TRA, VRA e desenhe a boca de cada um. Depois diga BLA, CLA, FLA, GLA, PLA e sinta a língua tocar o céu da boca no L. Produza as duas séries e registre a diferença: o R vibra, o L encosta."},
    {"id": 44, "titulo": "Vogais nasais em AM e AN", "texto": "Diga CANTAM, FALAM, BRINCAM e feche os lábios no M final. Depois diga BANCO, CAMPO, DANÇA e sinta o ar sair pelo nariz no AN. Liste palavras com AM (final de verbo) e AN (no meio) e marque onde o nariz vibra."},
    {"id": 45, "titulo": "Ditongo nasal ÃO", "texto": "Diga PÃO, MÃO, CÃO e perceba: o som começa no A e termina no U, tudo pelo nariz. Escreva 5 palavras com ÃO e faça um desenho para uma delas."},
    {"id": 46, "titulo": "Ditongo nasal ÃE e ÕE", "texto": "Diga MÃE, PÃES, LIÇÕES, CANÇÕES e perceba o ditongo nasal com E. Compare com 'mamão' (ÃE no início? não) e perceba a diferença entre ÃO e ÃE/ÕE. Escreva 4 palavras com ÃE ou ÕE."},
    {"id": 47, "titulo": "Percepção do R forte e do R fraco", "texto": "Compare CARA (R fraco: a língua toca uma vez) com CARRO (R forte: a língua vibra várias vezes). Diga 5 pares (cara/carro, muro/morro, para/parra) e circule onde o R é forte."},
    {"id": 48, "titulo": "Percepção do S e do Z", "texto": "Compare CASA (S com som de Z), PASSA (SS com som de S), ZERO (Z inicial). Diga as três palavras e escreva a regra com suas palavras: 'entre vogais, o S vira Z'."},
    {"id": 49, "titulo": "Neutralização de E/I e O/U no final", "texto": "No português falado, o E no final pode soar como I (LEITE, POTE) e o O como U (BOLO, GATO). Leia as palavras sentindo a pronúncia e escreva a grafia correta: leit_, pot_, bol_, gat_."},
    {"id": 50, "titulo": "Monossílabos e tonicidade", "texto": "Leia os monossílabos: PÁ, PÉ, PÓ, PÃO, MÃE, CÃO, CHÁ. Acentue quando necessário e explique por que alguns têm acento (abertos) e outros não (fechados: PAU, MÊS, SOL)."},
    {"id": 51, "titulo": "Segmentação de frases em palavras", "texto": "Ouça a frase 'O coelho fugiu do jardim' e bata palmas a cada palavra: 5 palavras. Faça com 3 frases do seu livro e escreva quantas palavras cada uma tem."},
    {"id": 52, "titulo": "Ditado de frases do ano", "texto": "O professor dita 5 frases com as grafias do ano: 1) A chave abriu o portão. 2) O coelho comeu a cenoura. 3) O carro parou na chuva. 4) A casa fica perto da praça. 5) O coração bate forte. Escreva e corrija."},
]

# Avaliações 7–9
VOLUME2["avaliacoes"] += [
    {
        "titulo": "Avaliação de Ortografia — 2º Semestre",
        "criterios": "Objetivo: verificar o domínio das grafias do 2º semestre (AM/AN, X, S/Z/Ç consolidados) e a justificativa das regras. Aplicação coletiva, 40 minutos.",
        "questoes": [
            "Complete com AM ou AN: eles cant__, o s__gue, o c__po, o t__bém? (também).",
            "Complete com X, CH ou SS: pei_e, _uva, pa_ar, _adrez.",
            "Complete com S ou Z: ca_a, _ebra, me_a, ra_ão.",
            "Complete com Ç ou SS: cora_ão, po_o, a_úcar, _apéu.",
            "Explique com suas palavras: por que CASA tem som de Z?",
            "Escreva 3 palavras com X e diga o som de cada uma.",
            "Escreva o plural de: CANÇÃO (CANÇÕES), LIÇÃO (LIÇÕES), PÃO (PÃES).",
            "Corrija a frase: 'O caro paso na rua suja' (O carro passou na rua suja).",
        ],
        "gabarito": [
            ("Q1", "cantam, sangue, campo, também", "AM/AN"),
            ("Q2", "peixe, chuva, passar, xadrez", "X, CH, SS"),
            ("Q3", "casa, zebra, mesa, razão", "S entre vogais e Z"),
            ("Q4", "coração, poço, açúcar, chapéu", "Ç e digrafos"),
            ("Q5", "Regra do S entre vogais com som de Z", "Justificativa ortográfica"),
            ("Q6", "xadrez (/tʃ/), exame (/z/), táxi (/ks/)", "Polissemia do X"),
            ("Q7", "canções, lições, pães", "Ditongos nasais"),
            ("Q8", "carro, passou", "Autocorreção ortográfica"),
        ],
    },
    {
        "titulo": "Avaliação de Fluência Leitora — Final do Ano",
        "criterios": "Objetivo: medir a fluência (precisão, ritmo, expressividade) em texto conhecido e desconhecido. Aplicação individual: leitura de 1 minuto com registro de palavras lidas corretamente.",
        "questoes": [
            "Leia o texto 1 (conhecido) em voz alta por 1 minuto: 'O coelho fugiu do jardim. A chuva começou a cair. Ele correu para o ninho e se escondeu até o sol voltar.'",
            "Leia o texto 2 (desconhecido) em voz alta por 1 minuto: 'A biblioteca da escola ganhou uma estante nova. As crianças escolheram histórias de fadas e de dragões. Todos queriam ler primeiro o livro do coelho aventureiro.'",
            "O professor registra: palavras lidas corretamente no texto 1 e no texto 2.",
            "Responda oralmente: de quem fala o texto 1? O que aconteceu depois da chuva?",
            "Responda oralmente: o que a biblioteca ganhou? Qual livro todos queriam ler?",
            "Leia com expressividade a frase: 'Todos queriam ler primeiro o livro do coelho aventureiro!'",
            "Autoavaliação: minha leitura ficou mais rápida e bonita do que no início do ano?",
        ],
        "gabarito": [
            ("Q1–Q2", "Registro de palavras/minuto", "Medida de fluência"),
            ("Q3", "Comparação dos dois textos", "Precisão e ritmo"),
            ("Q4", "Do coelho; ele se escondeu no ninho", "Compreensão do texto conhecido"),
            ("Q5", "Uma estante nova; o livro do coelho aventureiro", "Compreensão do texto novo"),
            ("Q6", "Leitura expressiva com entonação", "Prosódia"),
            ("Q7", "Reflexão sobre o progresso", "Metacognição"),
        ],
    },
    {
        "titulo": "Avaliação Integrada Final do Ano (2º Ano)",
        "criterios": "Objetivo: verificar a consolidação das metas do ano (leitura fluente, ortografia das grafias trabalhadas, produção de gêneros e compreensão). Aplicação em duas sessões de 40 minutos, com pausa.",
        "questoes": [
            "Leia o texto: 'O menino soltava pipas no campo. O vento levou a pipa para longe. O menino não ficou triste: correu atrás dela e a encontrou perto da cerca.' Quantas frases tem o texto?",
            "Quem soltava pipas? Para onde o vento levou a pipa? Onde o menino encontrou a pipa?",
            "Retire do texto: uma palavra com TR, uma palavra com ENCONTRO DOIS? (campo tem AN).",
            "Escreva o final da história com 2 frases usando uma palavra com CH e uma com NH.",
            "Complete: a pipa _ooa no céu (voa). O menino _orreu (correu). A _erca é de madeira (cerca).",
            "Escreva um bilhete para um amigo combinando de soltar pipas no sábado.",
            "Separe em sílabas: PIPAS, CAMPO, CERCA, VENTO.",
            "Autoavaliação: o que eu aprendi de melhor neste ano? O que ainda quero melhorar?",
        ],
        "gabarito": [
            ("Q1", "3 frases", "Estrutura do texto"),
            ("Q2", "O menino; para longe; perto da cerca", "Localização de informações"),
            ("Q3", "soltava? (TR); campo (AN)", "Identificação de grafias"),
            ("Q4", "Final coerente com CH e NH", "Produção textual"),
            ("Q5", "voa, correu, cerca", "Ortografia"),
            ("Q6", "Bilhete com estrutura (para quem, recado, de quem)", "Gênero textual"),
            ("Q7", "PI-PAS, CAM-PO, CER-CA, VEN-TO", "Segmentação silábica"),
            ("Q8", "Reflexão escrita", "Metacognição"),
        ],
    },
]
PERFIS[2] = VOLUME2

# --- Cortes de calibração (alvo: 648 pp, igual ao Volume 1) ---
VOLUME2["unidades"] = [u for u in VOLUME2["unidades"] if u["n"] not in {17, 21}]
_ktmp, _vistos = [], set()
for _f in VOLUME2["kumon"]:
    if _f["id"] not in _vistos:
        _vistos.add(_f["id"]); _ktmp.append(_f)
VOLUME2["kumon"] = _ktmp
del VOLUME2["sons"][42:50]         # remove sons 43..50 (mantém 51: segmentação, 52: ditado)
VOLUME2["sons"].append({
    "id": 53,
    "titulo": "Revisão Geral — Relaxamento Articulatório",
    "texto": "O aluno revisa as boquinhas das grafias estudadas, compara as "
             "sílabas com CH/C e NH/LH, completa um quadro de revisão com as "
             "palavras-alvo e escreve uma frase usando duas grafias revisadas. "
             "Encerra com a leitura em voz alta de um texto curto com todas "
             "as grafias do ano.",
})
VOLUME2["avaliacoes"] = [a for a in VOLUME2["avaliacoes"] if "Consciência Fonológica" not in a["titulo"]]

PERFIS[2] = VOLUME2

# =====================================================================
# Perfis 3º, 4º e 5º ano — clones adaptados do mesmo método (SPEC-935-R220)
# A estrutura pedagógica (unidades, kumon, sons, rastreio) é a mesma;
# mudam títulos, focos, BNCC e apresentação por ano.
# =====================================================================
import copy as _copy

_TS = {
    3: ["Bem-vindo ao 3º Ano",
        "Revisão: encontros consonantais",
        "Acentuação: agudo e circunflexo",
        "O til nos ditongos nasais",
        "S com som de Z",
        "X com sons de Z, CH e S",
        "G e J",
        "SS e C entre vogais",
        "C e QU nas sílabas",
        "R forte: RR e R inicial",
        "Dígrafos NH, LH e CH",
        "Encontros consonantais avançados",
        "H inicial e H medial",
        "M e N antes de P e B",
        "Finais AM e ÃO",
        "Dicionário e ordem alfabética",
        "Produção: o bilhete",
        "Revisão ortográfica do bimestre",
        "Ponto de exclamação e interrogação",
        "Produção: o convite",
        "Sarau de leitura do 3º Ano"],
    4: ["Bem-vindo ao 4º Ano",
        "O parágrafo",
        "Ponto final e vírgula",
        "Substantivos próprio e comum",
        "Adjetivos na descrição",
        "Verbos no texto",
        "Ortografia: S, Z e X",
        "Ortografia: G e J",
        "Ortografia: Ç, SS e C",
        "Dígrafos na escrita",
        "Til e acentuação",
        "Discurso direto",
        "Discurso indireto",
        "Rima e poema",
        "Produção: a notícia",
        "Revisão ortográfica",
        "Interpretação: ideias principais",
        "Produção: a carta",
        "Concordância básica",
        "Produção: o diário",
        "Sarau de leitura do 4º Ano"],
    5: ["Bem-vindo ao 5º Ano",
        "A crônica",
        "A notícia",
        "O artigo de opinião",
        "A propaganda",
        "A instrução",
        "A carta e o e-mail",
        "O relato pessoal",
        "O diário",
        "A fábula moderna",
        "O conto",
        "Produção: reescrita criativa",
        "Ortografia: revisão geral",
        "Acentuação: oxítonas e paroxítonas",
        "Hífen em palavras do cotidiano",
        "Pontuação: dois-pontos",
        "Fluência leitora",
        "Revisão textual em pares",
        "Produção: a reportagem",
        "O sarau final",
        "Sarau de leitura do 5º Ano"],
}

_FOCOS = {
    3: ["Acolhida e rotina do 3º ano",
        "Fixar encontros consonantais já estudados no 2º ano",
        "Reconhecer o acento agudo e o circunflexo nas palavras",
        "Ler e escrever palavras com til (ã, õ, ãe, ão)",
        "Usar S no fim de sílaba com som de Z",
        "Reconhecer os três sons possíveis do X",
        "Diferenciar G e J em palavras conhecidas",
        "Diferenciar SS e C na escrita entre vogais",
        "Usar C e QU conforme a vogal seguinte",
        "Escrever R forte em início e com RR entre vogais",
        "Consolidar os dígrafos NH, LH e CH",
        "Ler encontros consonantais em palavras maiores",
        "Usar H inicial e H medial nas palavras do cotidiano",
        "Aplicar M antes de P e B",
        "Escrever palavras terminadas em AM e ÃO",
        "Localizar palavras no dicionário e ordem alfabética",
        "Produzir bilhetes com início, meio e fim",
        "Revisar as grafias do bimestre em texto próprio",
        "Usar ? e ! na leitura expressiva e na escrita",
        "Produzir convites com informações completas",
        "Celebrar a fluência em leitura em voz alta"],
    4: ["Acolhida e rotina do 4º ano",
        "Escrever parágrafos com ideia única",
        "Usar ponto final e vírgula na enumeração",
        "Diferenciar substantivos próprio e comum",
        "Usar adjetivos para descrever personagens",
        "Reconhecer verbos de ação no texto",
        "Revisar a ortografia de S, Z e X",
        "Revisar a ortografia de G e J",
        "Revisar a ortografia de Ç, SS e C",
        "Consolidar a escrita de dígrafos",
        "Acentuar corretamente palavras com til",
        "Pontuar a fala dos personagens (discurso direto)",
        "Recontar a fala no discurso indireto",
        "Ler e produzir poemas com rima",
        "Produzir notícia com lead e fatos",
        "Revisar a própria escrita com checklist",
        "Localizar a ideia principal de cada parágrafo",
        "Produzir cartas com remetente e destinatário",
        "Concordar sujeito e verbo em frases curtas",
        "Produzir diários com registro pessoal",
        "Celebrar a fluência e a entonação na leitura"],
    5: ["Acolhida e rotina do 5º ano",
        "Ler e produzir crônicas do cotidiano",
        "Produzir notícias com estrutura jornalística",
        "Argumentar em artigo de opinião",
        "Analisar a linguagem da propaganda",
        "Produzir instruções passo a passo",
        "Escrever carta e e-mail com linguagem adequada",
        "Relatar experiências pessoais com ordem cronológica",
        "Manter registro pessoal no diário",
        "Ler e reescrever fábulas com moral explícita",
        "Produzir contos com personagem e conflito",
        "Reescrever um texto mudando o narrador",
        "Revisar todas as grafias estudadas",
        "Acentuar oxítonas e paroxítonas com segurança",
        "Usar hífen em palavras compostas cotidianas",
        "Usar dois-pontos na introdução de falas e listas",
        "Ler com fluência, ritmo e expressividade",
        "Revisar textos em pares com critérios do livro",
        "Produzir reportagens com entrevista",
        "Organizar o sarau final de leitura",
        "Celebrar o percurso leitor do 5º ano"],
}

_BNCC = {
    3: "EF03LP01, EF03LP02, EF03LP03, EF03LP05, EF03LP08, EF03LP09",
    4: "EF04LP01, EF04LP02, EF04LP03, EF04LP05, EF04LP06, EF04LP07, EF04LP09",
    5: "EF05LP01, EF05LP02, EF05LP03, EF05LP04, EF05LP05, EF05LP08, EF05LP10",
}

_SOBRE = {
    3: "O 3º ano consolida a alfabetização e avança para a ortografia: "
       "acentuação, til, dígrafos consolidados e produção de bilhetes e "
       "convites. O método continua com Boquinha, Kumon diário, rastreio "
       "integrado e leitura de fluência.",
    4: "O 4º ano passa a ler para aprender: interpretação, parágrafo, "
       "pontuação, classes de palavras e produção de notícia, carta e "
       "diário. O rastreio integrado continua observando fluência e "
       "ortografia sem diagnosticar.",
    5: "O 5º ano trabalha gêneros textuais completos: crônica, notícia, "
       "artigo de opinião, propaganda, reportagem e o sarau final. A "
       "fluência leitora e a revisão textual tornam-se metas centrais do "
       "método.",
}

for _ano in (3, 4, 5):
    _v = _copy.deepcopy(VOLUME2)
    _v["ano"] = _ano
    _v["titulo_ano"] = f"Alfabetizar Bem --- {_ano}º Ano"
    _v["bncc"] = _BNCC[_ano]
    _v["sobre"] = _SOBRE[_ano]
    for _i, _un in enumerate(_v["unidades"]):
        _un["titulo"] = _TS[_ano][_i]
        _un["foco"] = _FOCOS[_ano][_i]
        _un["bncc"] = _BNCC[_ano]
    PERFIS[_ano] = _v

# --- Sanitização IPA: símbolos sem glifo em Latin Modern (SPEC-935-R220) ---
_IPA = {"tʃ": "ch", "ʃ": "ch", "ɲ": "nh", "ʎ": "lh", "ɾ": "r", "ʁ": "r", "ʷ": "u"}

def _san(v):
    if isinstance(v, dict):
        return {k: _san(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_san(x) for x in v]
    if isinstance(v, tuple):
        return tuple(_san(x) for x in v)
    if isinstance(v, str):
        for _a, _b in _IPA.items():
            v = v.replace(_a, _b)
        return v
    return v

for _a in list(PERFIS):
    PERFIS[_a] = _san(PERFIS[_a])
