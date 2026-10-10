"""Executa o MIRA pelo orquestrador e adapta o deck ao site R783."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from marceloclaro.orchestrator import MarceloClaroOrchestrator


def main():
    folder = Path(__file__).resolve().parent / "mira"
    result = MarceloClaroOrchestrator(auto_load_agents=True).present_task(str(folder))
    if not result.get("ok") or not result.get("passed"):
        raise RuntimeError(result)
    deck = folder / "apresentacao/deck.html"
    original = deck.read_text(encoding="utf-8")
    result["sha256_deck_original"] = hashlib.sha256(deck.read_bytes()).hexdigest()
    subtitles = {
        'O projeto por trás da pesquisa': 'OpenCode Ecosystem Core',
        'O caminho de uma tarefa': 'Pedido, coordenação e encaminhamento',
        'Escolher e concluir são etapas diferentes': 'Execução depende do ambiente',
        'MIRA apresenta as ideias': 'Comunicação visual do trabalho',
        'Uma escolha explicável': 'O problema do roteamento',
        'Uma equipe para entender': 'Analogia de programas especializados',
        'Quatro perguntas, uma nota': 'Critérios definidos no modelo',
        'Imagine cem fichas': 'Pesos da comparação, não probabilidades',
        'Ana e Cid no exemplo': 'Números registrados no trabalho',
        'Experimente e explique': 'Desafios e perguntas no site',
        'Regras e testes': 'Fórmulas e situações simuladas',
        'Filtrar antes de comparar': 'Critérios de elegibilidade',
        'Quatro critérios se combinam': 'Combinação com pesos fixos',
        'Pesos que somam um': 'Normalização das utilidades',
        'Ana e Cid': 'Exemplo registrado no trabalho',
        'Evidência em dois planos': 'Formalização e bancada interna',
        'O alcance dos resultados': 'Limitações da evidência',
        'Continuidade da pesquisa': 'Próximas perguntas científicas',
        'Fonte da apresentação': 'Versão editorial e autoria',
    }
    def refine_slide(match):
        slide = match.group(0)
        heading = re.search(r'<h1>(.*?)</h1>', slide).group(1)
        subtitle = subtitles.get(heading, 'Roteamento inspirado em atenção')
        return re.sub(r'<p class="sub">.*?</p>', '<p class="sub">' + subtitle + '</p>', slide, count=1, flags=re.S)
    original = re.sub(r'<section class="slide.*?</section>', refine_slide, original, flags=re.S)
    style = '''<style id="site-accessibility">
    :root{--bg:#f5f6f0;--fg:#17291c;--muted:#536451;--line:#d7decd}
    .glass-card{background:rgba(255,255,255,.7);box-shadow:0 16px 60px #35563815;border-radius:10px}
    .glass-card h1{font-family:Georgia,serif;font-weight:400;letter-spacing:-.035em;color:#355638}
    .accent{background:linear-gradient(90deg,#355638,#97ac73,#cfe598)}
    .grid .cell{background:#e9eee2;border-radius:6px}
    .anim-stage{background:#e4eadc}
    nav button{background:#355638;color:white;border-color:#355638;border-radius:5px}
    .site-tools{position:fixed;top:16px;left:26px;right:26px;display:flex;justify-content:space-between;z-index:12;font-size:12px}
    .site-tools button,.site-tools a{padding:7px 12px;border:1px solid #aebf9f;border-radius:5px;background:#f5f6f0;color:#355638;text-decoration:none}
    :focus-visible{outline:3px solid #648348;outline-offset:4px}
    body.paused *,body.paused *::before{animation-play-state:paused!important}
    @media(max-width:600px){.glass-card{padding:25px 22px;max-height:77vh}.slide{padding:9vh 6vw}.site-tools{left:20px;right:20px;font-size:10px}nav{right:20px}nav button{font-size:12px}.counter{left:20px}}
    @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
    </style>'''
    tools = '''<div class="site-tools"><a href="../../index.html">← Voltar ao site</a><button id="deck-motion" aria-pressed="false">Pausar movimento</button></div>
    <script>
    const motionButton=document.getElementById('deck-motion');
    function pauseDeck(value){document.body.classList.toggle('paused',value);motionButton.setAttribute('aria-pressed',String(value));motionButton.textContent=value?'Retomar movimento':'Pausar movimento'}
    pauseDeck(matchMedia('(prefers-reduced-motion: reduce)').matches);
    motionButton.addEventListener('click',()=>pauseDeck(!document.body.classList.contains('paused')));
    document.querySelector('nav').setAttribute('aria-label','Navegação dos slides');
    document.querySelectorAll('svg').forEach(svg=>{svg.setAttribute('role','img');svg.setAttribute('aria-label','Metáfora visual animada do conceito apresentado no título do slide')});
    </script>'''
    enhanced = original.replace('</head>', style + '</head>', 1).replace('</body>', tools + '</body>', 1)
    deck.write_text(enhanced, encoding='utf-8')
    result['sha256_deck_publicado'] = hashlib.sha256(deck.read_bytes()).hexdigest()
    result['adaptacao'] = 'Subtítulos editoriais, tema, pausa, retorno ao site, foco e redução de movimento aplicados após conformidade do pipeline original.'
    result['deck'] = 'mira/apresentacao/deck.html'
    result['conformidade'] = 'mira/apresentacao/CONFORMIDADE.md'
    (folder / 'execucao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
