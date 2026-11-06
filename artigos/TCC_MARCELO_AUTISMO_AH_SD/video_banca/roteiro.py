# -*- coding: utf-8 -*-
"""Roteiro e conteúdo dos slides do vídeo de banca.

Cada cena tem uma narração (fonte do TTS) e um conteúdo visual sintético.
A duração é medida depois, a partir do áudio gerado.
"""

SCENES = [
    {
        "id": "01_abertura",
        "layout": "title",
        "eyebrow": "TCC · BANCA DE DEFESA",
        "title": "Dupla excepcionalidade no Brasil",
        "subtitle": "Autismo, altas habilidades/superdotação e desafios de identificação",
        "meta": "Censo Escolar 2021–2024",
        "author": "Marcelo Claro Laranjeira",
        "institution": "FACUMINAS · Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica",
        "narration": (
            "Olá. Este é o trabalho Dupla excepcionalidade no Brasil: autismo, altas habilidades ou superdotação e desafios de identificação a partir do Censo Escolar, de 2021 a 2024. "
            "Sou Marcelo Claro Laranjeira, da Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica, da Facuminas."
        ),
    },
    {
        "id": "02_roteiro",
        "layout": "cards3",
        "eyebrow": "ROTEIRO",
        "title": "Três ideias em sete minutos",
        "cards": [
            ("1", "O problema", "O que é a dupla excepcionalidade e por que ela é invisível"),
            ("2", "As evidências", "O que o Censo Escolar revela sobre a distância entre TEA e AH/SD"),
            ("3", "As implicações", "O que a neuropsicopedagogia pode fazer diante desse cenário"),
        ],
        "narration": (
            "Em poucos minutos, vou apresentar três ideias. "
            "Primeiro, o que é a dupla excepcionalidade e por que ela é invisível. "
            "Segundo, o que os dados oficiais revelam sobre a distância entre autismo e altas habilidades. "
            "Terceiro, o que a neuropsicopedagogia pode fazer diante desse cenário."
        ),
    },
    {
        "id": "03_problema",
        "layout": "split",
        "eyebrow": "O PROBLEMA",
        "title": "Duas condições, um único estudante",
        "left_title": "O que é",
        "left_text": "Coexistência de autismo e altas habilidades/superdotação.",
        "right_title": "O que acontece",
        "right_text": "A escola identifica uma dimensão e apaga a outra.",
        "bullets": ["Mascaramento recíproco", "Diagnóstico tardio", "Intervenção parcial"],
        "narration": (
            "A dupla excepcionalidade é a coexistência de autismo e altas habilidades ou superdotação. "
            "O estudante pode ter um raciocínio sofisticado em uma área e, ao mesmo tempo, enfrentar barreiras na comunicação, na regulação emocional e no processamento sensorial. "
            "O problema é que a escola tende a identificar apenas uma dessas dimensões. "
            "Quando identifica o autismo, pode subestimar o talento. Quando identifica a alta habilidade, pode ignorar as necessidades de apoio. "
            "O resultado é uma resposta educativa parcial."
        ),
    },
    {
        "id": "04_pergunta",
        "layout": "content",
        "eyebrow": "PERGUNTA E OBJETIVOS",
        "title": "O que os dados revelam sobre essa distância?",
        "lead_label": "PERGUNTA DE PESQUISA",
        "subtitle": "Como evoluem as matrículas de TEA e AH/SD no Censo Escolar, de 2021 a 2024?",
        "bullets": ["Comparar as duas categorias", "Analisar a distribuição regional", "Construir cenários exploratórios"],
        "footnote": "Estudo exploratório e descritivo · dados secundários oficiais · sem inferência causal",
        "narration": (
            "A pergunta que orientou o trabalho foi: como evoluem, no Censo Escolar de 2021 a 2024, as matrículas de estudantes com autismo e com altas habilidades, e o que esses dados revelam sobre os desafios de identificação? "
            "O objetivo foi comparar as duas categorias, analisar a distribuição regional e construir cenários exploratórios para os próximos anos."
        ),
    },
    {
        "id": "05_metodo",
        "layout": "cards3",
        "eyebrow": "METODOLOGIA",
        "title": "Revisão e dados oficiais",
        "cards": [
            ("1", "Revisão narrativa", "20 obras com DOI ativo e auditável"),
            ("2", "Censo Escolar", "Sinopses do Inep, 2021 a 2024"),
            ("3", "Análise", "Séries, razões, regiões e cenários"),
        ],
        "narration": (
            "A pesquisa combina revisão bibliográfica narrativa e análise de dados secundários oficiais. "
            "Foram utilizadas as Sinopses Estatísticas da Educação Básica do Inep, de 2021 a 2024, com os totais de matrículas em classes comuns e exclusivas. "
            "A literatura científica foi selecionada com base em DOI ativo e auditável. Vinte obras compõem o corpus. "
            "O estudo é exploratório e não pretende estabelecer causalidade."
        ),
    },
    {
        "id": "06_nacional",
        "layout": "chart",
        "eyebrow": "DADOS NACIONAIS",
        "title": "O autismo cresceu 212%; as altas habilidades, 86%",
        "big_left": ("212%", "autismo"),
        "big_right": ("86%", "altas habilidades"),
        "chart": "national.png",
        "narration": (
            "Os dados mostram um crescimento acelerado do autismo: de 294 mil matrículas, em 2021, para 918 mil, em 2024. Um aumento de 212 por cento. "
            "As altas habilidades cresceram de 23,7 mil para 44,1 mil, um aumento de 86 por cento. "
            "Em números absolutos, o autismo ganhou mais de 600 mil matrículas. As altas habilidades ganharam cerca de 20 mil. "
            "A participação do autismo na educação básica passou de 0,63 por cento para 1,95 por cento. A das altas habilidades passou de 0,05 por cento para 0,09 por cento."
        ),
    },
    {
        "id": "07_razao",
        "layout": "chart",
        "eyebrow": "A DISTÂNCIA",
        "title": "A razão TEA/AH/SD subiu de 12,4 para 20,8",
        "big_left": ("20,8", "em 2024"),
        "big_right": ("12,4", "em 2021"),
        "big_colors": ["amber", "teal"],
        "chart": "ratio.png",
        "narration": (
            "A razão entre as duas categorias passou de 12,4 para 20,8. "
            "Em 2024, para cada matrícula de altas habilidades, havia cerca de 21 matrículas de autismo. "
            "A distância aumentou. Isso não prova que a dupla excepcionalidade seja rara. "
            "Indica que a identificação das altas habilidades não acompanhou o crescimento do autismo."
        ),
    },
    {
        "id": "08_regioes",
        "layout": "chart",
        "eyebrow": "REGIÕES",
        "title": "O Nordeste tem 45 matrículas de TEA para cada uma de AH/SD",
        "big_left": ("45,2", "Nordeste"),
        "big_right": ("8,0", "Sul"),
        "chart": "regions.png",
        "narration": (
            "A distribuição regional é desigual. O Nordeste tem a maior razão: 45 matrículas de autismo para cada uma de altas habilidades. "
            "O Sul tem a menor: 8 para 1. O Sudeste concentra o maior número absoluto de autismo. O Sul concentra o maior número de altas habilidades. "
            "A diferença sugere que a identificação depende de critérios, instrumentos e prioridades locais, e não apenas da prevalência."
        ),
    },
    {
        "id": "09_estados",
        "layout": "chart",
        "eyebrow": "ESTADOS",
        "title": "Ceará e Paraná: mesma ordem de grandeza, realidades distintas",
        "big_left": ("121,8", "Ceará"),
        "big_right": ("3,9", "Paraná"),
        "chart": "states.png",
        "narration": (
            "Nos estados, o contraste é ainda mais forte. O Ceará tem razão de 121,8. O Paraná, de 3,9. "
            "Os dois têm ordens de grandeza semelhantes de autismo, mas o Paraná identifica 12.807 matrículas de altas habilidades, contra 574 no Ceará. "
            "A explicação mais plausível não é a prevalência, mas a capacidade de identificação."
        ),
    },
    {
        "id": "10_cenarios",
        "layout": "split",
        "eyebrow": "CENÁRIOS 2025–2027",
        "title": "A lacuna persiste mesmo com convergência",
        "left_title": "Linear",
        "left_text": "1,51 mi TEA · 65,8 mil AH/SD · razão 22,9",
        "right_title": "Convergência",
        "right_text": "1,22 mi TEA · 86,3 mil AH/SD · razão 14,2",
        "bullets": ["Cenários exploratórios", "Não são previsões", "Dependem de políticas de identificação"],
        "narration": (
            "Construímos três cenários para 2025 a 2027. No cenário linear, o autismo chega a 1,5 milhão de matrículas em 2027, e as altas habilidades a 65,8 mil. A razão sobe para 22,9. "
            "No cenário de convergência, com crescimento maior das altas habilidades, a razão cai para 14,2, mas a diferença absoluta continua grande. "
            "Os cenários são exploratórios. Não são previsões."
        ),
    },
    {
        "id": "11_literatura",
        "layout": "content",
        "eyebrow": "LITERATURA",
        "title": "O mascaramento apaga uma das dimensões",
        "lead_label": "ACHADO DA LITERATURA",
        "subtitle": "A identificação tende a ser unilateral.",
        "bullets": ["A alta habilidade esconde o autismo", "O autismo esconde a alta habilidade", "O resultado é diagnóstico tardio e intervenção parcial"],
        "narration": (
            "A literatura internacional e brasileira aponta para o mascaramento. A alta habilidade pode esconder o autismo. O autismo pode esconder a alta habilidade. "
            "O resultado é diagnóstico tardio, intervenções parciais e sofrimento. "
            "Estudos brasileiros recentes mostram que a dupla excepcionalidade ainda é pouco pesquisada e pouco reconhecida nas escolas. A identificação tende a ser unilateral."
        ),
    },
    {
        "id": "12_neuro",
        "layout": "cards3",
        "eyebrow": "NEUROPSICOPEDAGOGIA",
        "title": "Avaliar, intervir, articular",
        "cards": [
            ("1", "Avaliação abrangente", "Funções cognitivas, aprendizagem, regulação e sensorialidade"),
            ("2", "Intervenção baseada em forças", "Potencialidades sem negligenciar os apoios"),
            ("3", "Articulação", "Escola, família e rede de apoio"),
        ],
        "narration": (
            "A neuropsicopedagogia pode contribuir em três frentes. "
            "Primeiro, a avaliação abrangente, que considera funções cognitivas, aprendizagem, regulação emocional e processamento sensorial. "
            "Segundo, a intervenção baseada em forças, que parte das potencialidades sem negligenciar os apoios. "
            "Terceiro, a articulação entre escola, família e rede de apoio. O objetivo não é rotular, mas compreender o estudante e construir condições de aprendizagem."
        ),
    },
    {
        "id": "13_conclusao",
        "layout": "conclusion",
        "eyebrow": "CONCLUSÃO",
        "title": "Três ideias para levar",
        "cards": [
            ("1", "A distância cresceu", "212% de crescimento do TEA contra 86% das AH/SD"),
            ("2", "A subidentificação é plausível", "Os dados são compatíveis com a invisibilidade da dupla excepcionalidade"),
            ("3", "Sem dados cruzados, a invisibilidade persiste", "O Censo não cruza TEA e AH/SD"),
        ],
        "narration": (
            "Três ideias para levar. Primeira: a distância entre autismo e altas habilidades cresceu no Censo. "
            "Segunda: essa distância é compatível com a subidentificação das altas habilidades e com a invisibilidade da dupla excepcionalidade. "
            "Terceira: sem protocolos, formação e dados cruzados, a dupla excepcionalidade continuará fora das estatísticas e das políticas. "
            "O estudo tem limitações: o Censo não cruza as categorias e os cenários não são previsões. Mas os dados permitem afirmar que a inclusão precisa olhar para os estudantes que ficam entre as duas categorias."
        ),
    },
    {
        "id": "14_encerramento",
        "layout": "closing",
        "eyebrow": "ENCERRAMENTO",
        "title": "Obrigado",
        "subtitle": "Dupla excepcionalidade no Brasil",
        "author": "Marcelo Claro Laranjeira",
        "institution": "FACUMINAS · Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica",
        "meta": "Brasília · 2026",
        "note": "Voz sintética",
        "narration": (
            "Obrigado pela atenção. Este trabalho foi apresentado por Marcelo Claro Laranjeira, da Facuminas, em 2026. "
            "O texto completo, os dados e a auditoria das referências estão disponíveis. "
            "Voz sintética. Muito obrigado."
        ),
    },
]
