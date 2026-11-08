#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ponte sonora: 100 termos de chinês (mandarim) ligados aos conceitos.

O objetivo não é substituir um curso de chinês. É usar o conteúdo científico
como material de pronúncia: o estudante vê o hanzi, lê o pinyin com tons,
ouve mentalmente uma leitura de apoio e repete uma microfrase.

Convenções:
- pinyin com sílabas separadas por espaço (para o aprendiz ver o ritmo);
- tons lexicais 1–4 e 5 (neutro);
- leitura de apoio em grafia portuguesa, aproximada, não IPA;
- hanzi simplificado.
"""
from __future__ import annotations

# id do conceito -> (hanzi, pinyin com sílabas separadas)
CHINES: dict[str, tuple[str, str]] = {
    # Parte 1 — informação e medida
    "bit": ("比特", "bǐ tè"),
    "qubit": ("量子比特", "liàng zǐ bǐ tè"),
    "amplitude": ("振幅", "zhèn fú"),
    "probabilidade": ("概率", "gài lǜ"),
    "medicao": ("测量", "cè liáng"),
    "base": ("基", "jī"),
    "fase": ("相位", "xiàng wèi"),
    "interferencia": ("干涉", "gān shè"),
    "emaranhamento": ("纠缠", "jiū chán"),
    "bell": ("贝尔态", "bèi ěr tài"),
    # Parte 2 — a lente de Bohm
    "onda_piloto": ("导波", "dǎo bō"),
    "equacao_guia": ("导波方程", "dǎo bō fāng chéng"),
    "equilibrio_quantico": ("量子平衡", "liàng zǐ píng héng"),
    "nao_localidade": ("非定域性", "fēi dìng yù xìng"),
    "colapso_efetivo": ("有效坍缩", "yǒu xiào tān suō"),
    "ordem_implicada": ("隐缠序", "yǐn chán xù"),
    "holomovimento": ("整体运动", "zhěng tǐ yùn dòng"),
    "dialogo": ("对话", "duì huà"),
    "suspensao": ("悬置", "xuán zhì"),
    "totalidade": ("整体性", "zhěng tǐ xìng"),
    # Parte 3 — circuitos
    "porta_x": ("翻转门", "fān zhuǎn mén"),
    "porta_h": ("哈达玛门", "hā dá mǎ mén"),
    "porta_z": ("相位门", "xiàng wèi mén"),
    "cnot": ("受控非门", "shòu kòng fēi mén"),
    "circuito": ("电路", "diàn lù"),
    "bell_circuito": ("贝尔电路", "bèi ěr diàn lù"),
    "ghz": ("多体纠缠态", "duō tǐ jiū chán tài"),
    "qasm": ("量子汇编", "liàng zǐ huì biān"),
    "transpilacao": ("转译", "zhuǎn yì"),
    "medicao_multipla": ("多次测量", "duō cì cè liáng"),
    # Parte 4 — ferramentas
    "pennylane": ("量子软件", "liàng zǐ ruǎn jiàn"),
    "cirq": ("量子框架", "liàng zǐ kuàng jià"),
    "qiskit": ("量子开发包", "liàng zǐ kāi fā bāo"),
    "qnode": ("量子节点", "liàng zǐ jié diǎn"),
    "cirq_circuit": ("量子线路", "liàng zǐ xiàn lù"),
    "quantumcircuit": ("量子电路", "liàng zǐ diàn lù"),
    "statevector": ("态矢量", "tài shǐ liàng"),
    "bloch": ("布洛赫球", "bù luò hè qiú"),
    "amostragem": ("采样", "cǎi yàng"),
    "gjq_client": ("量子客户端", "liàng zǐ kè hù duān"),
    # Parte 5 — hardware e nuvem
    "supercondutor": ("超导体", "chāo dǎo tǐ"),
    "qubit_fisico": ("物理量子比特", "wù lǐ liàng zǐ bǐ tè"),
    "decoerencia": ("退相干", "tuì xiāng gān"),
    "t1_t2": ("弛豫与相干", "chí yù yǔ xiāng gān"),
    "erro_leitura": ("读取错误", "dú qǔ cuò wù"),
    "ruido": ("噪声", "zào shēng"),
    "ciquanta": ("量子中心", "liàng zǐ zhōng xīn"),
    "tiangong": ("天宫", "tiān gōng"),
    "fila": ("任务队列", "rèn wù duì liè"),
    "api_key": ("密钥", "mì yuè"),
    # Parte 6 — experimentos
    "ghz_real": ("实验多体态", "shí yàn duō tǐ tài"),
    "vqc_xor": ("变分分类器", "biàn fēn fēn lèi qì"),
    "classificador": ("分类器", "fēn lèi qì"),
    "encoding": ("编码", "biān mǎ"),
    "ansatz": ("拟设", "nǐ shè"),
    "treino": ("训练", "xùn liàn"),
    "acuracia": ("准确率", "zhǔn què lǜ"),
    "phase_damping": ("相位阻尼", "xiàng wèi zǔ ní"),
    "depolarizing": ("去极化", "qù jí huà"),
    "ruido_benefico": ("有益噪声", "yǒu yì zào shēng"),
    # Parte 7 — matemática
    "vetor": ("向量", "xiàng liàng"),
    "matriz": ("矩阵", "jǔ zhèn"),
    "produto_interno": ("内积", "nèi jī"),
    "tensor": ("张量积", "zhāng liàng jī"),
    "densidade": ("密度矩阵", "mì dù jǔ zhèn"),
    "traco": ("迹", "jì"),
    "autovalor": ("特征值", "tè zhēng zhí"),
    "fourier": ("傅里叶", "fù lǐ yè"),
    "holograma": ("全息图", "quán xī tú"),
    "fourier_quantico": ("量子傅里叶", "liàng zǐ fù lǐ yè"),
    # Parte 8 — pedagogia
    "nanoaula": ("微课", "wēi kè"),
    "autodidatismo": ("自学", "zì xué"),
    "feedback": ("反馈", "fǎn kuì"),
    "checkpoint": ("检查点", "jiǎn chá diǎn"),
    "erro_produtivo": ("建设性错误", "jiàn shè xìng cuò wù"),
    "roda": ("对话圈", "duì huà quān"),
    "projeto": ("项目", "xiàng mù"),
    "rubrica": ("评分标准", "píng fēn biāo zhǔn"),
    "adaptacao": ("适应", "shì yìng"),
    "acessibilidade": ("无障碍", "wú zhàng ài"),
    # Parte 9 — ética
    "acesso": ("访问", "fǎng wèn"),
    "dupla_finalidade": ("双重用途", "shuāng chóng yòng tú"),
    "privacidade": ("隐私", "yǐn sī"),
    "lgpd": ("数据保护", "shù jù bǎo hù"),
    "custo": ("成本", "chéng běn"),
    "ambiente": ("环境", "huán jìng"),
    "trabalho": ("工作", "gōng zuò"),
    "desinformacao": ("虚假信息", "xū jiǎ xìn xī"),
    "consenso": ("共识", "gòng shí"),
    "responsabilidade": ("责任", "zé rèn"),
    # Parte 10 — projeto
    "pergunta": ("问题", "wèn tí"),
    "hipotese": ("假设", "jiǎ shè"),
    "evidencia": ("证据", "zhèng jù"),
    "limite": ("局限", "jú xiàn"),
    "replicacao": ("复现", "fù xiàn"),
    "narrativa": ("叙事", "xù shì"),
    "visualizacao": ("可视化", "kě shì huà"),
    "apresentacao": ("展示", "zhǎn shì"),
    "portfolio": ("作品集", "zuò pǐn jí"),
    "proximo_passo": ("下一步", "xià yí bù"),
}

# lente -> (modelo hanzi, modelo pinyin, modelo português)
# {zh} e {py} recebem o termo; {titulo} recebe o título do conceito.
FRASES: dict[str, tuple[str, str, str]] = {
    "ideia": ("{zh}是核心概念。", "{py} shì hé xīn gài niàn.",
              "“{titulo}” é o conceito central."),
    "analogia": ("这像{zh}。", "Zhè xiàng {py}.",
                 "Isto se parece com “{titulo}”."),
    "pratica": ("练习{zh}。", "Liàn xí {py}.",
                "Pratique “{titulo}”."),
    "laboratorio": ("观察{zh}。", "Guān chá {py}.",
                    "Observe “{titulo}”."),
    "erro": ("{zh}不是魔法。", "{py} bú shì mó fǎ.",
             "“{titulo}” não é magia."),
    "alem": ("深入了解{zh}。", "Shēn rù liǎo jiě {py}.",
             "Aprofunde-se em “{titulo}”."),
    "dialogo": ("你怎么看{zh}？", "Nǐ zěn me kàn {py}?",
                "O que você pensa de “{titulo}”?"),
    "etica": ("谁受益于{zh}？", "Shéi shòu yì yú {py}?",
              "Quem se beneficia de “{titulo}”?"),
    "vida": ("我在生活中看到{zh}。", "Wǒ zài shēng huó zhōng kàn dào {py}.",
             "Vejo “{titulo}” na vida."),
    "checkpoint": ("我学会了{zh}。", "Wǒ xué huì le {py}.",
                   "Eu aprendi “{titulo}”."),
}

_MARCAS = {
    "ā": 1, "á": 2, "ǎ": 3, "à": 4,
    "ē": 1, "é": 2, "ě": 3, "è": 4,
    "ī": 1, "í": 2, "ǐ": 3, "ì": 4,
    "ō": 1, "ó": 2, "ǒ": 3, "ò": 4,
    "ū": 1, "ú": 2, "ǔ": 3, "ù": 4,
    "ǖ": 1, "ǘ": 2, "ǚ": 3, "ǜ": 4,
}

_SEM_MARCA = {
    "ā": "a", "á": "a", "ǎ": "a", "à": "a",
    "ē": "e", "é": "e", "ě": "e", "è": "e",
    "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
    "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
    "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
    "ǖ": "ü", "ǘ": "ü", "ǚ": "ü", "ǜ": "ü",
}


def sem_tom(texto: str) -> str:
    return "".join(_SEM_MARCA.get(c, c) for c in texto)


def tom_silaba(silaba: str) -> int:
    """Retorna 1–4, ou 5 para sílaba sem marca (neutro)."""
    for ch in silaba:
        if ch in _MARCAS:
            return _MARCAS[ch]
    return 5


def tons(pinyin: str) -> str:
    """Ex.: 'liàng zǐ bǐ tè' -> '4-3-3-4'."""
    return "-".join(str(tom_silaba(s)) for s in pinyin.split())


_INICIAIS = [
    "zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l",
    "g", "k", "h", "j", "q", "x", "r", "z", "c", "s", "y", "w",
]

_FINAIS = {
    "a": "a", "o": "o", "e": "e", "ê": "e", "i": "i", "u": "u", "ü": "yu",
    "ai": "ai", "ei": "ei", "ao": "au", "ou": "ou",
    "an": "an", "en": "en", "ang": "ang", "eng": "eng", "ong": "ong",
    "ia": "ia", "ie": "ie", "iao": "iau", "iu": "iu", "ian": "ien",
    "in": "in", "iang": "iang", "ing": "ing", "iong": "iong",
    "ua": "ua", "uo": "uo", "uai": "uai", "ui": "uei", "uan": "uan",
    "un": "uen", "uang": "uang", "ueng": "ueng",
    "üe": "yue", "üan": "yuan", "ün": "yun", "er": "er",
}

_INICIAIS_PT = {
    "b": "b", "p": "p", "m": "m", "f": "f", "d": "d", "t": "t",
    "n": "n", "l": "l", "g": "g", "k": "k", "h": "r",
    "j": "dj", "q": "tch", "x": "sh",
    "zh": "dj", "ch": "tch", "sh": "sh", "r": "j",
    "z": "dz", "c": "ts", "s": "s", "y": "", "w": "",
}


def _separar(silaba: str) -> tuple[str, str]:
    if silaba in ("zhi", "chi", "shi", "ri", "zi", "ci", "si"):
        return silaba[:-1], "i_apical"
    for ini in _INICIAIS:
        if silaba.startswith(ini):
            return ini, silaba[len(ini):]
    return "", silaba


def _final_pt(final: str, inicial: str) -> str:
    if final == "i_apical":
        return "i"
    # j/q/x escrevem ü como u: ju, qu, xu, jue, juan, jun...
    if inicial in ("j", "q", "x") and final.startswith("u"):
        final = "ü" + final[1:]
    # y/w são semi-vogais: ya, ye, yao, you, yan, yin, yang, ying, yong...
    if inicial == "y":
        mapa_y = {
            "i": "i", "a": "ia", "e": "ie", "ao": "iau", "ou": "iu",
            "an": "ien", "in": "in", "ang": "iang", "ing": "ing",
            "ong": "iong", "u": "yu", "ue": "yue", "uan": "yuan", "un": "yun",
        }
        return mapa_y.get(final, _FINAIS.get(final, final))
    if inicial == "w":
        mapa_w = {
            "u": "u", "a": "ua", "o": "uo", "ai": "uai", "ei": "uei",
            "an": "uan", "en": "uen", "ang": "uang", "eng": "ueng",
        }
        return mapa_w.get(final, _FINAIS.get(final, final))
    return _FINAIS.get(final, final)


def leitura(pinyin: str) -> str:
    """Leitura de apoio em grafia portuguesa. Aproximada; não é IPA."""
    partes = []
    for silaba in pinyin.split():
        limpa = sem_tom(silaba)
        ini, fin = _separar(limpa)
        partes.append(_INICIAIS_PT.get(ini, ini) + _final_pt(fin, ini))
    return "-".join(partes)


def validar(ids_conceitos: list[str]) -> list[str]:
    """Retorna os ids sem entrada chinesa."""
    return [i for i in ids_conceitos if i not in CHINES]