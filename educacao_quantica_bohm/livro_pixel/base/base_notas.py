# -*- coding: utf-8 -*-
"""Notas de cálculo por conceito.

Cada nota explica, em linguagem de leitor, a fórmula, a substituição e o
resultado de um número que aparece na lauda. As notas são inseridas nas lentes
"laboratório" e "para ir além" dos níveis N1 e N2; no N0, o livro continua sem
fórmula. Números ilustrativos (ética, pedagogia, custo) são marcados como tal.
"""

from __future__ import annotations


def N(formula: str, conta: str, resultado: str, limite: str) -> dict[str, str]:
    return {
        "formula": formula,
        "conta": conta,
        "resultado": resultado,
        "limite": limite,
    }


NOTAS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ P1
    "bit": N(
        "Um número em base 2 é uma soma de potências de 2.",
        "13 = 8 + 4 + 1 = 1×2³ + 1×2² + 0×2¹ + 1×2⁰.",
        "13₁₀ = 1101₂. Conferindo: 8 + 4 + 0 + 1 = 13.",
        "A conta mostra a representação; não explica por que o bit é a menor diferença registrável.",
    ),
    "qubit": N(
        "|ψ⟩ = α|0⟩ + β|1⟩, com |α|² + |β|² = 1.",
        "Com α = 0,6 e β = 0,8: 0,6² + 0,8² = 0,36 + 0,64 = 1.",
        "P(0) = |α|² = 0,36 e P(1) = |β|² = 0,64.",
        "As amplitudes não são probabilidades; a medição entrega um resultado, não os dois.",
    ),
    "amplitude": N(
        "A probabilidade é o módulo ao quadrado da amplitude: P = |α|².",
        "α = 0,6 → P = 0,6² = 0,36. α = −0,6 → P = (−0,6)² = 0,36.",
        "O sinal muda a fase, não a probabilidade isolada.",
        "Duas amplitudes iguais em módulo e opostas em fase podem cancelar na interferência.",
    ),
    "probabilidade": N(
        "p = N_evento / N_total; EP = √(p(1−p)/N).",
        "p = 484/1024 = 0,4727. EP = √(0,4727×0,5273/1024) = 0,0156.",
        "p = 47,27% e intervalo de 95% ≈ 47,27% ± 3,06%.",
        "Uma amostra de 1024 tiros não prova o valor de longo prazo; apenas o estima.",
    ),
    "medicao": N(
        "Para H|0⟩ = (|0⟩+|1⟩)/√2, P(0) = P(1) = 1/2.",
        "Em 1024 tiros, o esperado é 512; o desvio padrão é √(1024×0,5×0,5) = 16.",
        "Uma contagem típica fica em 512 ± 32 (dois desvios).",
        "Cada tiro exige preparar o estado de novo; medir o mesmo qubit repetidamente não dá a mesma estatística.",
    ),
    "base": N(
        "|+⟩ = (|0⟩+|1⟩)/√2. Na base Z, P(0) = 1/2; na base X, P(+) = 1.",
        "Medir |+⟩ em Z: 0,5. Medir |+⟩ em X: 1,0.",
        "A mesma preparação dá respostas diferentes porque a pergunta mudou.",
        "Base não é um ângulo da mesma foto; é uma escolha experimental com consequência física.",
    ),
    "fase": N(
        "H Z H = X. A fase relativa inverte a interferência.",
        "H Z H |0⟩ = X|0⟩ = |1⟩; portanto P(1) = 1.",
        "Sem a fase Z, H H |0⟩ = |0⟩ e P(0) = 1.",
        "A fase global (multiplicar todo o estado por −1) não muda nada; só a fase relativa importa.",
    ),
    "interferencia": N(
        "A = (1/√2)(1 + e^{iφ}); P = |A|² = cos²(φ/2).",
        "φ = π → cos²(π/2) = 0. φ = 0 → cos²(0) = 1.",
        "Em φ = π, as duas amplitudes se cancelam e P = 0.",
        "A interferência exige coerência; ruído de fase destrói o cancelamento.",
    ),
    "emaranhamento": N(
        "|Φ⁺⟩ = (|00⟩+|11⟩)/√2.",
        "P(00) = |1/√2|² = 1/2; P(11) = 1/2; P(01) = P(10) = 0.",
        "Cada qubit isolado tem P(0) = 1/2, mas os resultados são correlacionados.",
        "Correlação não é sinal: não se transmite informação mais rápido que a luz.",
    ),
    "bell": N(
        "Fidelidade proxy = (N00 + N11) / N_total.",
        "N00 = 484, N11 = 480, N = 1024: (484+480)/1024 = 964/1024.",
        "0,9414 = 94,1%; os 5,9% restantes são 01 e 10.",
        "É uma proxy de fidelidade, não uma tomografia completa do estado.",
    ),

    # ------------------------------------------------------------------ P2
    "onda_piloto": N(
        "ψ = R e^{iS/ħ}; a velocidade guiada é v = ∇S/m.",
        "Para uma onda plana, S = ħkx; então ∇S = ħk e v = ħk/m.",
        "v = ħk/m; a fase codifica o momento.",
        "A onda piloto é uma interpretação; a previsão coincide com a mecânica quântica usual.",
    ),
    "equacao_guia": N(
        "v = (ħ/m) Im(∇ψ/ψ).",
        "Para ψ = e^{ikx}: ∇ψ/ψ = ik; Im(ik) = k; v = ħk/m.",
        "v = ħk/m, o mesmo resultado da onda plana.",
        "Para várias partículas, a velocidade de uma depende das posições das outras.",
    ),
    "equilibrio_quantico": N(
        "ρ = |ψ|²; a continuidade exige ∂ρ/∂t + ∇·(ρv) = 0.",
        "Para ψ = e^{ikx}, ρ = 1 e v = ħk/m; ∂ρ/∂t = 0 e ∇·(ρv) = 0.",
        "A distribuição se conserva: 0 + 0 = 0.",
        "O equilíbrio quântico é um postulado da interpretação, não um teorema geral.",
    ),
    "nao_localidade": N(
        "v₁ = (ħ/m) Im(∇₁ψ/ψ), que depende de x₂.",
        "Se ψ = f(x₁−x₂), então ∇₁f = −∇₂f; a velocidade de 1 depende da posição de 2.",
        "A dependência é instantânea no formalismo, mas não permite enviar sinais.",
        "Não localidade não é violação da relatividade: não há mensagem controlável.",
    ),
    "colapso_efetivo": N(
        "A trajetória entra em um dos pacotes; a probabilidade é |c_i|².",
        "Se c₁ = 0,7, então |c₁|² = 0,49.",
        "Há 49% de chance de a partícula terminar no pacote 1.",
        "Em Bohm não há colapso fundamental: a partícula já estava em uma trajetória.",
    ),
    "ordem_implicada": N(
        "Um par de Fourier: f(x) e F(k); Δx·Δk ≥ 1/2.",
        "Um pulso estreito em x tem espectro largo em k; um pulso largo tem espectro estreito.",
        "A largura de um domínio compensa a do outro.",
        "A ordem implicada é uma analogia filosófica; não é uma equação testável por si só.",
    ),
    "holomovimento": N(
        "O fluxo é dado por v = ∇S/m; a forma explícita emerge do movimento.",
        "Com S = ħ(kx − ωt), ∇S = ħk e v = ħk/m.",
        "A velocidade é constante para uma onda plana; a forma fica implícita na fase.",
        "Holomovimento é metáfora; a conta operacional é a equação do guia.",
    ),
    "dialogo": N(
        "O roteiro de 9 minutos é 1 + 4 + 2 + 2.",
        "Com 10 pessoas, 4 minutos de fala dão 24 segundos por pessoa.",
        "9 min = 540 s; 4 min = 240 s; 240/10 = 24 s.",
        "Diálogo não é debate: o objetivo é examinar suposições, não vencer.",
    ),
    "suspensao": N(
        "Atualização bayesiana: P(H|E) = P(E|H)P(H) / P(E).",
        "P(H)=0,5; P(E|H)=0,8; P(E|¬H)=0,2; P(E)=0,8×0,5+0,2×0,5=0,5.",
        "P(H|E)=0,8×0,5/0,5=0,8.",
        "Suspender não é abandonar a crença; é colocá-la entre parênteses e testá-la.",
    ),
    "totalidade": N(
        "Correlação de Bell: E(a,b) = −cos(a−b).",
        "a=b → E=−1; a−b=90° → E=0; a−b=180° → E=+1.",
        "O todo correlaciona as partes de um modo que não se reduz a valores locais.",
        "Totalidade é uma lente filosófica; o número que a testa é a correlação.",
    ),

    # ------------------------------------------------------------------ P3
    "porta_x": N(
        "X = [[0,1],[1,0]]; X|0⟩=|1⟩ e X|1⟩=|0⟩.",
        "X|0⟩ = [0,1]ᵀ = |1⟩; X² = I.",
        "X inverte a base computacional, mas também troca amplitudes de uma superposição.",
        "X não é um NOT clássico para estados arbitrários: ele é uma matriz unitária.",
    ),
    "porta_h": N(
        "H = (1/√2)[[1,1],[1,−1]]; H|0⟩=(|0⟩+|1⟩)/√2.",
        "H|0⟩ = (1/√2)(|0⟩+|1⟩); P(0)=P(1)=1/2.",
        "H cria superposição e também muda a base de medida.",
        "H não é um sorteio: é uma rotação de base reversível.",
    ),
    "porta_z": N(
        "Z = [[1,0],[0,−1]]; Z|0⟩=|0⟩ e Z|1⟩=−|1⟩.",
        "Z não muda P(0) nem P(1) na base Z; muda a fase relativa.",
        "Medir depois de Z, na base Z, dá a mesma distribuição.",
        "O efeito de Z aparece na interferência, não na medida isolada.",
    ),
    "cnot": N(
        "CNOT: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩.",
        "O primeiro bit é o controle; o segundo é o alvo.",
        "CNOT|10⟩ = |11⟩; CNOT|11⟩ = |10⟩.",
        "CNOT é condicional; sem superposição, ele é uma cópia clássica condicional.",
    ),
    "circuito": N(
        "Aplicar portas é multiplicar matrizes; a ordem importa.",
        "CNOT(H⊗I)|00⟩ = (|00⟩+|11⟩)/√2; P(00)=P(11)=1/2.",
        "O circuito de Bell produz duas amplitudes iguais.",
        "Inverter a ordem de H e CNOT muda o estado resultante.",
    ),
    "bell_circuito": N(
        "H no qubit 0 e CNOT(0,1).",
        "H|0⟩=(|0⟩+|1⟩)/√2; CNOT → (|00⟩+|11⟩)/√2.",
        "As probabilidades são 0,5 para 00 e 0,5 para 11.",
        "O circuito ideal não tem ruído; o backend acrescenta erro de porta e leitura.",
    ),
    "ghz": N(
        "H no qubit 0 e CNOT em cada um dos demais.",
        "Para 3 qubits: (|000⟩+|111⟩)/√2; para 4: (|0000⟩+|1111⟩)/√2.",
        "P(000)=P(111)=0,5 no caso ideal de 3 qubits.",
        "GHZ é frágil: um erro em um qubit afeta a correlação global.",
    ),
    "qasm": N(
        "OPENQASM 2.0 é um texto com registradores, portas e medidas.",
        "Um GHZ de 4 qubits usa 1 h, 3 cx e 4 measure.",
        "qreg q[4]; creg c[4]; h q[0]; cx q[0],q[1]; ...",
        "O texto descreve o circuito; não prova que o backend o executou.",
    ),
    "transpilacao": N(
        "Transpilar reescreve o circuito nas portas nativas do backend.",
        "Um H pode virar U2; um CNOT pode virar uma sequência de portas nativas.",
        "O unitário ideal é preservado; a profundidade e o erro mudam.",
        "Transpilação não é otimização gratuita: cada porta nativa tem erro.",
    ),
    "medicao_multipla": N(
        "p̂ = N_evento/N; EP = √(p̂(1−p̂)/N).",
        "Com p̂=0,5 e N=1024: EP=√(0,25/1024)=0,0156.",
        "Intervalo de 95% ≈ 0,5 ± 0,031.",
        "A medida é destrutiva; repetir exige preparar o estado de novo.",
    ),

    # ------------------------------------------------------------------ P4
    "pennylane": N(
        "⟨Z⟩ = P(0) − P(1).",
        "Para H|0⟩, P(0)=P(1)=0,5; ⟨Z⟩=0,5−0,5=0.",
        "O valor esperado é 0; a medida individual ainda é 0 ou 1.",
        "Convenções de ordem de qubits e de bases variam entre frameworks.",
    ),
    "cirq": N(
        "Um Circuit é organizado em momentos; cada momento tem portas disjuntas.",
        "H no momento 1; CNOT no momento 2; medida no momento 3.",
        "Profundidade = 3 momentos.",
        "Momentos são uma escolha de agendamento; não mudam o unitário ideal.",
    ),
    "qiskit": N(
        "Um QuantumCircuit de n qubits tem 2ⁿ amplitudes.",
        "Para n=2, 2²=4 amplitudes: |00⟩, |01⟩, |10⟩, |11⟩.",
        "O statevector é um vetor de 4 números complexos.",
        "O simulador é exato sem ruído; o backend não é.",
    ),
    "qnode": N(
        "Regra do deslocamento: ∂⟨Z⟩/∂θ = [⟨Z⟩(θ+π/2) − ⟨Z⟩(θ−π/2)]/2.",
        "Se ⟨Z⟩(θ)=cos θ, então a derivada é −sen θ.",
        "A regra avalia o circuito em dois pontos e combina os resultados.",
        "Nem toda porta é diferenciável; a regra vale para geradores conhecidos.",
    ),
    "cirq_circuit": N(
        "O Circuit agrupa operações em momentos.",
        "X(q0) no momento 1; CNOT(q0,q1) no momento 2; measure no momento 3.",
        "3 momentos, 2 qubits.",
        "A ordem dos qubits e os nomes das portas mudam entre bibliotecas.",
    ),
    "quantumcircuit": N(
        "Um circuito de 2 qubits e 2 bits clássicos tem 4 amplitudes e 4 resultados.",
        "As medidas mapeiam q0→c0 e q1→c1.",
        "O circuito é uma receita; o resultado só existe depois da execução.",
        "Circuito não é o mesmo que estado; o estado é o que o circuito prepara.",
    ),
    "statevector": N(
        "Dimensão do statevector = 2ⁿ.",
        "n=4 → 2⁴=16 amplitudes; cada amplitude é um número complexo.",
        "16 complexos ≈ 256 bytes em complex128.",
        "A simulação exata cresce exponencialmente; por isso existem simuladores de tensor network.",
    ),
    "bloch": N(
        "x = 2P(0)_X − 1; z = 2P(0)_Z − 1; |r| = √(x²+y²+z²).",
        "Para H|0⟩: P(0)_X=1 → x=1; P(0)_Z=0,5 → z=0.",
        "|r| = √(1²+0²+0²) = 1.",
        "A esfera de Bloch só representa um qubit; para dois ou mais, use matriz densidade.",
    ),
    "amostragem": N(
        "EP = √(p(1−p)/N); intervalo de 95% ≈ p ± 1,96·EP.",
        "p=0,5, N=1024: EP=0,0156; 1,96×0,0156=0,0306.",
        "Intervalo ≈ [0,469; 0,531].",
        "O erro de amostragem não é o erro de porta; são fontes diferentes.",
    ),
    "gjq_client": N(
        "A soma dos counts deve ser igual ao número de tiros.",
        "1024 tiros → Σ counts = 1024.",
        "Se a soma não for 1024, o experimento não teve os tiros declarados.",
        "A API entrega counts; ela não garante que o backend estava calibrado.",
    ),

    # ------------------------------------------------------------------ P5
    "supercondutor": N(
        "Abaixo de Tc, a resistência cai a zero; o fóton de micro-ondas lê o qubit.",
        "Alumínio: Tc ≈ 1,2 K. Dilution fridge: ≈ 10 mK.",
        "10 mK < 1,2 K: o alumínio está supercondutor.",
        "Temperatura baixa é necessária, mas não suficiente para alta fidelidade.",
    ),
    "qubit_fisico": N(
        "Energia do fóton: E = hf; h = 6,626×10⁻³⁴ J·s.",
        "f = 4,20 GHz = 4,20×10⁹ Hz.",
        "E = 6,626×10⁻³⁴ × 4,20×10⁹ ≈ 2,78×10⁻²⁴ J.",
        "A frequência é uma fotografia; a fidelidade depende de portas, leitura e ambiente.",
    ),
    "decoerencia": N(
        "A coerência decai como e^{−t/T2}; a população como e^{−t/T1}.",
        "Médias da calibração: T1=73,07 µs; T2=26,36 µs.",
        "2T1=146,14 µs; T2=26,36 µs ≤ 146,14 µs.",
        "Médias escondem a dispersão entre qubits; um qubit pode ser muito pior.",
    ),
    "t1_t2": N(
        "P(t)=e^{−t/T1}; coerência(t)=e^{−t/T2}.",
        "Em t=T1, P=1/e≈0,368; em t=T2, a coerência cai a 1/e.",
        "Depois de um T1, cerca de 36,8% da população permanece.",
        "T1 e T2 medem processos diferentes: população e fase.",
    ),
    "erro_leitura": N(
        "Erro de leitura = média de P(1|0) e P(0|1).",
        "Exemplo: P(1|0)=0,008 e P(0|1)=0,008.",
        "Erro médio = 0,8%; em 1024 tiros, ≈ 8 leituras erradas.",
        "Erro de leitura não é erro de porta; a mitigação é outra.",
    ),
    "ruido": N(
        "Fidelidade F = 1 − ε; para k portas, F_total ≈ F^k.",
        "F1=99,74% → ε1=0,26%; F2=97,54% → ε2=2,46%.",
        "Dez portas de dois qubits: 0,9754¹⁰ ≈ 0,779.",
        "Fidelidade de porta não garante desempenho de algoritmo; o padrão de erro importa.",
    ),
    "ciquanta": N(
        "Acesso é pré-requisito; o experimento precisa de conta, fila e shots.",
        "1024 shots por circuito; 4 circuitos = 4096 shots.",
        "O custo e o tempo crescem com o número de circuitos.",
        "Acesso não é reprodutibilidade: outro usuário pode receber outra calibração.",
    ),
    "tiangong": N(
        "Comparação de escala: 156 qubits / 20 qubits = 7,8.",
        "Baihua tem 7,8× mais qubits que Guoji08.",
        "A fidelidade proxy do GHZ, porém, foi menor no Baihua (65,1% vs 78,8%).",
        "Número de qubits não é medida de qualidade.",
    ),
    "fila": N(
        "Tempo total ≈ tempo de fila + tempo de execução.",
        "Se a fila é 10 min por job e há 4 jobs, o total é ≈ 40 min.",
        "1024 shots podem levar segundos; a espera domina.",
        "Tempo de fila não é tempo de cálculo.",
    ),
    "api_key": N(
        "Uma chave hexadecimal de 32 caracteres tem 16 bytes = 128 bits.",
        "Espaço de busca ≈ 2¹²⁸.",
        "A segurança depende de não vazar a chave e de rotacioná-la.",
        "Chave forte não protege dados mal configurados.",
    ),

    # ------------------------------------------------------------------ P6
    "ghz_real": N(
        "Fidelidade proxy = (N0000 + N1111)/N.",
        "Guoji08: (418+389)/1024 = 807/1024 = 0,7881.",
        "78,8% no Guoji08; Baihua: (437+230)/1024 = 667/1024 = 65,1%.",
        "A proxy não mede a fase nem o estado completo.",
    ),
    "vqc_xor": N(
        "Predição = 1 se P(1) ≥ 0,5; senão 0.",
        "00: 0,041→0; 01: 0,967→1; 10: 0,952→1; 11: 0,043→0.",
        "4 acertos em 4 = 100%.",
        "Quatro pontos não são generalização; o teto de 100% é fácil de atingir.",
    ),
    "classificador": N(
        "Acurácia = (TP+TN)/N; precisão = TP/(TP+FP); recall = TP/(TP+FN).",
        "TP=2, TN=2, FP=0, FN=0: acurácia=(2+2)/4=1,0.",
        "Precisão=2/2=1,0; recall=2/2=1,0.",
        "Métricas perfeitas em 4 pontos não garantem desempenho em novos dados.",
    ),
    "encoding": N(
        "Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sen(θ/2)|1⟩; P(1)=sen²(θ/2).",
        "O experimento usa θ=2π/3: sen²(π/3)=0,75.",
        "P(1)=0,75; a descrição antiga dizia π/3, que daria 0,25.",
        "O ângulo de codificação é uma escolha; a conta fixa a convenção.",
    ),
    "ansatz": N(
        "O ansatz de 2 qubits e 3 camadas usa 2×2×3 = 12 parâmetros.",
        "Cada camada tem 2 Ry + 2 CNOT + 2 Ry.",
        "12 parâmetros e 6 CNOT no circuito de treino.",
        "Expressividade não garante generalização; o ansatz pode ser raso demais.",
    ),
    "treino": N(
        "COBYLA com 120 iterações e 5 seeds = 600 avaliações.",
        "Cada avaliação calcula P(1) para 4 entradas de treino.",
        "O custo cresce com iterações × seeds × pontos.",
        "Otimização é estocástica; uma seed não é uma prova.",
    ),
    "acuracia": N(
        "Acurácia = acertos/N.",
        "4/4 = 1,0 = 100%.",
        "Com n=4 e 100%, o intervalo de 95% é largo; a regra de três dá limite inferior ≈ 25%.",
        "Acurácia alta em amostra pequena não é evidência de generalização.",
    ),
    "phase_damping": N(
        "Phase damping preserva a população: P(1) não muda.",
        "Modelo efetivo: (1−γ)P(1) + γP(1) = P(1).",
        "Para γ=0,05, P(1) permanece o mesmo.",
        "O modelo é efetivo no observable Z; não é uma simulação completa do canal.",
    ),
    "depolarizing": N(
        "Depolarizing: P(1) → (1−γ)P(1) + γ/2.",
        "P(1)=0,967 e γ=0,05: 0,95×0,967 + 0,025 = 0,9437.",
        "A margem até 0,5 cai de 0,467 para 0,444.",
        "O modelo isotrópico é uma aproximação; o ruído real não é uniforme.",
    ),
    "ruido_benefico": N(
        "Para detectar uma diferença de 5% com 95% de confiança, n ≈ 1,96²×0,25/0,05².",
        "n ≈ 3,8416×0,25/0,0025 = 384,16.",
        "São necessários ≈ 385 pontos por grupo, não 4.",
        "O teste com 4 pontos não sustenta a hipótese de ruído benéfico.",
    ),

    # ------------------------------------------------------------------ P7
    "vetor": N(
        "|r| = √(x² + y² + z²).",
        "S5 no hardware: x=0,877, y=0,035, z=0,539.",
        "|r| = √(0,769+0,001+0,291) = √1,061 = 1,030.",
        "Um vetor físico não passa de 1; o excesso revela viés de leitura e estimativa linear.",
    ),
    "matriz": N(
        "X = [[0,1],[1,0]]; X|0⟩ = [0,1]ᵀ.",
        "X·[1,0]ᵀ = [0,1]ᵀ = |1⟩.",
        "A matriz transforma o vetor de estado.",
        "Matrizes unitárias preservam a norma; nem toda matriz é uma porta válida.",
    ),
    "produto_interno": N(
        "⟨0|0⟩=1; ⟨0|1⟩=0; ⟨ψ|ψ⟩=|α|²+|β|².",
        "Com α=0,6 e β=0,8: 0,36+0,64=1.",
        "A norma do estado é 1.",
        "Produto interno não é probabilidade; a probabilidade é o módulo ao quadrado.",
    ),
    "tensor": N(
        "Dimensão do produto tensorial = 2×2 = 4.",
        "|0⟩⊗|1⟩ = |01⟩; base: 00, 01, 10, 11.",
        "Dois qubits exigem 4 amplitudes.",
        "Produto tensorial não é produto cartesiano; a ordem dos fatores importa.",
    ),
    "densidade": N(
        "ρ = |ψ⟩⟨ψ| para estado puro; Tr(ρ)=1; ρ²=ρ.",
        "Para |+⟩: ρ = 1/2[[1,1],[1,1]].",
        "Tr(ρ)=1; ρ²=ρ, então o estado é puro.",
        "Para estado misto, ρ²≠ρ e Tr(ρ²)<1.",
    ),
    "traco": N(
        "Tr(ρ) = soma dos autovalores = 1.",
        "ρ = [[0,5,0,5],[0,5,0,5]] → Tr=0,5+0,5=1.",
        "A pureza é Tr(ρ²)=0,5²+0,5²+2×0,5²=1.",
        "O traço é independente da base; a pureza mede a mistura.",
    ),
    "autovalor": N(
        "Z|0⟩=+1|0⟩; Z|1⟩=−1|1⟩; ⟨Z⟩=p0−p1.",
        "Com p0=0,6 e p1=0,4: ⟨Z⟩=0,2.",
        "O valor esperado fica entre −1 e +1.",
        "Autovalores são resultados possíveis; o valor esperado é uma média.",
    ),
    "fourier": N(
        "F = (1/√N)[e^{2πijk/N}].",
        "Para N=4, F|0⟩ = (|0⟩+|1⟩+|2⟩+|3⟩)/2.",
        "As quatro probabilidades são 1/4.",
        "A QFT é unitária; não é a FFT clássica.",
    ),
    "holograma": N(
        "I = I₁ + I₂ + 2√(I₁I₂)cos φ.",
        "Com I₁=I₂=1: I = 2 + 2cos φ.",
        "φ=0 → I=4; φ=π → I=0.",
        "O holograma é uma analogia de interferência; não é uma prova da ordem implicada.",
    ),
    "fourier_quantico": N(
        "QFT|j⟩ = (1/√N) Σₖ e^{2πijk/N}|k⟩.",
        "Para N=4 e j=0: (|0⟩+|1⟩+|2⟩+|3⟩)/2.",
        "As probabilidades são 1/4; as fases codificam j.",
        "A QFT não mede diretamente; ela prepara um estado.",
    ),

    # ------------------------------------------------------------------ P8
    "nanoaula": N(
        "7 min = 420 s; 10 lentes = 70 min por conceito.",
        "100 conceitos × 70 min = 7000 min = 116,7 h por nível.",
        "Os três níveis somam ≈ 350 h de leitura ativa.",
        "O tempo é uma estimativa; compreensão não é proporcional ao tempo.",
    ),
    "autodidatismo": N(
        "30 dias × 1 lauda = 30 laudas.",
        "30/3000 = 0,01 = 1% da obra.",
        "A trilha de 30 dias cobre 1% das laudas, mas 30 ideias centrais.",
        "Disciplina não garante compreensão; o checkpoint é o teste.",
    ),
    "feedback": N(
        "Rubrica de 5 critérios × 2 pontos = 10 pontos.",
        "Se 4 critérios valem 2 e 1 vale 1, o total é 9.",
        "A nota é uma soma ponderada, não uma verdade absoluta.",
        "Feedback sem critério vira opinião.",
    ),
    "checkpoint": N(
        "100 conceitos × 1 checkpoint = 100 checkpoints.",
        "Cada checkpoint aparece nas 10 lentes e nos 3 níveis.",
        "O gabarito dá critério e resposta esperada, não uma resposta única.",
        "Checkpoint não é exame; é um teste de compreensão.",
    ),
    "erro_produtivo": N(
        "Taxa de erro = erros/exercícios.",
        "1 erro em 10 = 10%; 3 em 10 = 30%.",
        "10% pede revisão pontual; 30% pede retomar o conceito.",
        "Erro é dado; não é fracasso.",
    ),
    "roda": N(
        "9 min = 1 + 4 + 2 + 2.",
        "10 pessoas → 240 s / 10 = 24 s por pessoa na fala.",
        "O roteiro protege o tempo de quem ouve.",
        "Diálogo não é terapia nem debate.",
    ),
    "projeto": N(
        "Um projeto mínimo tem 4 partes: pergunta, hipótese, experimento, limite.",
        "Se cada parte leva 1 página, o projeto tem 4 páginas.",
        "A saída é um documento replicável, não uma promessa.",
        "Projeto não é marketing.",
    ),
    "rubrica": N(
        "5 critérios × 4 níveis = 20 células.",
        "Se 3 avaliadores discordam em 2 células, a confiabilidade precisa ser discutida.",
        "A rubrica organiza o julgamento; não o elimina.",
        "Rubrica não é verdade objetiva.",
    ),
    "adaptacao": N(
        "3 níveis × 10 lentes = 30 combinações por conceito.",
        "O leitor escolhe 1 combinação por vez.",
        "Adaptar é escolher a porta de entrada, não baixar o padrão.",
        "Adaptação não é simplificação permanente.",
    ),
    "acessibilidade": N(
        "Contraste mínimo recomendado: 4,5:1 para texto normal.",
        "Fundo #070B12 e texto #E8F0FF têm contraste alto.",
        "A fonte de corpo é 10,8 pt; o leitor pode ampliar no PDF.",
        "Acessibilidade não é opcional; é parte do contrato de leitura.",
    ),

    # ------------------------------------------------------------------ P9
    "acesso": N(
        "Custo ilustrativo = custo por shot × número de shots.",
        "A R$ 0,01 por shot, 1024 shots = R$ 10,24.",
        "Quatro circuitos = R$ 40,96 (conta ilustrativa).",
        "O custo real varia com backend, fila e política de acesso.",
    ),
    "dupla_finalidade": N(
        "A mesma tecnologia pode servir a fins civis e militares.",
        "Uma matriz de risco cruza probabilidade e impacto.",
        "Risco = probabilidade × impacto (escala ilustrativa).",
        "A tecnologia não é neutra; o uso precisa de governança.",
    ),
    "privacidade": N(
        "k-anonimato: cada registro se confunde com k−1 outros.",
        "Se k=5, cada registro se esconde entre 5.",
        "k maior reduz reidentificação, mas não a elimina.",
        "Anonimização não é garantia absoluta.",
    ),
    "lgpd": N(
        "Princípios: finalidade, necessidade, transparência e segurança.",
        "Coletar 1 dado necessário é melhor que coletar 10 por precaução.",
        "A minimização reduz risco e custo.",
        "Lei não é ética; cumprir a lei não basta.",
    ),
    "custo": N(
        "Custo total = shots × preço por shot + tempo de fila.",
        "4096 shots × R$ 0,01 = R$ 40,96 (ilustrativo).",
        "O orçamento precisa incluir repetições e falhas.",
        "Custo não é qualidade.",
    ),
    "ambiente": N(
        "Energia ilustrativa = potência × tempo.",
        "Se 1 shot gasta 0,1 J, 4096 shots gastam 409,6 J.",
        "409,6 J ≈ 0,11 Wh (conta ilustrativa).",
        "Os números são ilustrativos; a pegada real depende da infraestrutura.",
    ),
    "trabalho": N(
        "3000 laudas × 7 min = 21.000 min = 350 h.",
        "A 20 h por semana, 350/20 = 17,5 semanas.",
        "O trabalho de leitura é comparável a um semestre intenso.",
        "Trabalho invisível não é trabalho inexistente.",
    ),
    "desinformacao": N(
        "Uma afirmação sem fonte verificável não é evidência.",
        "Se 1 em 10 claims não tem DOI, a taxa de claims frágeis é 10%.",
        "A checagem reduz o risco, mas não o elimina.",
        "Desinformação não é uma propriedade quântica.",
    ),
    "consenso": N(
        "Consenso não é unanimidade.",
        "7 de 10 especialistas concordam → 70% de concordância.",
        "Os 30% discordantes precisam ser ouvidos.",
        "Consenso não é verdade.",
    ),
    "responsabilidade": N(
        "Matriz: quem decide, quem paga, quem é afetado.",
        "Se 3 grupos são afetados e 1 decide, há assimetria.",
        "A assimetria precisa ser declarada e corrigida.",
        "Responsabilidade não pode ser delegada ao algoritmo.",
    ),

    # ------------------------------------------------------------------ P10
    "pergunta": N(
        "Operacionalizar: variável, população, comparação.",
        "Exemplo: P(1) do VQC em 4 entradas, comparado ao acaso (0,5).",
        "A pergunta vira um teste com métrica e limite.",
        "Pergunta não é hipótese; a hipótese precisa ser falsificável.",
    ),
    "hipotese": N(
        "H₀: não há diferença; H₁: há diferença.",
        "Se a acurácia é 100% em 4 pontos, o teste tem pouca potência.",
        "A hipótese precisa de um desenho que possa refutá-la.",
        "Hipótese não é opinião.",
    ),
    "evidencia": N(
        "Evidência = contagem + total + incerteza + fonte.",
        "484/1024 = 0,4727 ± 0,0156.",
        "O número vem com um intervalo e uma origem.",
        "Evidência não é prova definitiva.",
    ),
    "limite": N(
        "Intervalo de 95% ≈ p ± 1,96·EP.",
        "p=0,482, EP=0,0156 → [0,451; 0,513].",
        "A diferença de 1 a 2 pontos pode ser amostragem.",
        "Todo resultado tem um limite; declará-lo é parte do método.",
    ),
    "replicacao": N(
        "Replicar = mesmo código, mesmo backend, mesma seed, nova execução.",
        "Duas execuções com 1024 tiros podem diferir em ≈ ±3%.",
        "A comparação precisa considerar a incerteza.",
        "Replicação não é garantia de generalização.",
    ),
    "narrativa": N(
        "Uma narrativa de evidência tem 3 partes: afirmação, evidência, limite.",
        "Se falta o limite, a narrativa vira propaganda.",
        "A estrutura de 3 partes mantém a honestidade.",
        "Narrativa não é manipulação.",
    ),
    "visualizacao": N(
        "Um gráfico honesto declara eixo, unidade, fonte e n.",
        "Sem unidade, o número não significa nada.",
        "Sem n, a incerteza fica invisível.",
        "Um gráfico pode enganar mesmo com dados corretos.",
    ),
    "apresentacao": N(
        "10 slides × 1 ideia = 10 ideias em 7 minutos.",
        "7 min = 420 s; 420/10 = 42 s por slide.",
        "O tempo impõe prioridade.",
        "Slides não são a pesquisa.",
    ),
    "portfolio": N(
        "Portfólio mínimo: pergunta, experimento, reflexão.",
        "3 artefatos, 1 página cada = 3 páginas.",
        "O portfólio mostra o processo, não só o resultado.",
        "Portfólio não é nota.",
    ),
    "proximo_passo": N(
        "Compromisso: 1 pergunta, 1 experimento, 1 data.",
        "Se a data é em 7 dias, o experimento precisa caber em 7 dias.",
        "O próximo passo é pequeno, verificável e datado.",
        "O próximo passo é seu; o livro não decide por você.",
    ),
}


# Notas específicas do experimento mostrado na lente de laboratório.
# Cada conta usa os counts reais desta edição (Guoji08, 1024 tiros).
NOTAS_EXPERIMENTO: dict[str, dict[str, str]] = {
    "E01": N(
        "P(0) = N₀/N.",
        "N₀=1016, N=1024: 1016/1024 = 0,9922.",
        "P(0)=99,22%; 8 tiros caíram em 1 (0,78%).",
        "O desvio de 0,78% é compatível com erro de leitura; não prova que o estado é |0⟩ perfeito.",
    ),
    "E02": N(
        "P(1) = N₁/N; erro de leitura ≈ N₀/N.",
        "N₁=1010, N₀=14, N=1024: 1010/1024 = 0,9863.",
        "P(1)=98,63%; 14 leituras erradas = 1,37%.",
        "O erro de leitura é uma propriedade do dispositivo, não do estado preparado.",
    ),
    "E03": N(
        "P(1) = N₁/N; desvio = |P(1) − 1/2|.",
        "N₁=494, N=1024: 494/1024 = 0,4824; |0,4824−0,5| = 0,0176.",
        "P(1)=48,24%, dentro de ≈1,1 erro padrão de 50%.",
        "Uma execução não prova que a moeda é justa; o intervalo de confiança é largo.",
    ),
    "E04": N(
        "H-Z-H devolve |1⟩; P(1) = N₁/N.",
        "N₁=1010, N=1024: 1010/1024 = 0,9863.",
        "P(1)=98,63% (ideal 100%); 14 tiros em 0.",
        "A fase Z foi aplicada; o desvio restante é ruído, não uma fase residual.",
    ),
    "E05": N(
        "Fidelidade proxy = (N₀₀ + N₁₁)/N.",
        "(484+480)/1024 = 964/1024 = 0,9414.",
        "94,14%; 60 tiros em 01/10.",
        "A proxy não mede fase nem pureza; é uma soma de populações.",
    ),
    "E06": N(
        "Fidelidade proxy = (N₀₀₀₀ + N₁₁₁₁)/N.",
        "(418+389)/1024 = 807/1024 = 0,7881.",
        "78,81%; 217 tiros fora de 0000/1111.",
        "O GHZ é frágil; a proxy cai rápido com o número de qubits.",
    ),
    "E07": N(
        "E = (N₀₀+N₁₁−N₀₁−N₁₀)/N; S = E₀₀+E₀₁+E₁₀−E₁₁.",
        "E₀₀=588/1024=0,5742; E₀₁=590/1024=0,5762; E₁₀=580/1024=0,5664; E₁₁=−682/1024=−0,6660.",
        "S = 0,5742+0,5762+0,5664+0,6660 = 2,3828.",
        "S>2 viola a desigualdade clássica; uma execução não é prova estatística definitiva.",
    ),
    "E08": N(
        "|P(0)−P(1)| = |N₀−N₁|/N.",
        "N₀=530, N₁=494: |36|/1024 = 0,0352.",
        "Desbalanceamento de 3,52%.",
        "Um gerador quântico ideal tem 0%; o desvio é ruído e amostragem.",
    ),
    "E09": N(
        "Ry(2π/3)|0⟩ = cos(π/3)|0⟩ + sen(π/3)|1⟩; P(1)=sen²(π/3).",
        "sen²(π/3)=0,75. Medido: 761/1024 = 0,7432.",
        "P(1)=74,32% (ideal 75%).",
        "A diferença de 0,68 ponto percentual é compatível com 1024 tiros.",
    ),
    "E10": N(
        "Predição = 1 se P(1) ≥ 0,5; acurácia = acertos/4.",
        "P(1): 42/1024=0,041; 990/1024=0,967; 975/1024=0,952; 44/1024=0,043.",
        "Predições 0,1,1,0; 4 acertos em 4.",
        "Quatro pontos não medem generalização; o teste é pequeno.",
    ),
    "E11": N(
        "P(00) = N₀₀/N.",
        "N₀₀=485, N=1024: 485/1024 = 0,4736.",
        "P(00)=47,36% (ideal 50%).",
        "A interferência de dois qubits concentra a distribuição, mas o ruído espalha.",
    ),
    "E12": N(
        "P(000) = N₀₀₀/N; ideal 1/8 = 0,125.",
        "N₀₀₀=123, N=1024: 123/1024 = 0,1201.",
        "P(000)=12,01% (ideal 12,5%).",
        "A QFT uniformiza as probabilidades; a fase não é medida aqui.",
    ),
    "E13": N(
        "P(01) = N₀₁/N.",
        "N₀₁=980, N=1024: 980/1024 = 0,9570.",
        "P(01)=95,70% (ideal 100%).",
        "O produto tensorial |01⟩ é uma base; o erro restante é leitura e porta.",
    ),
    "E14": N(
        "H-X-H deveria devolver |0⟩; P(0)=N₀/N.",
        "N₀=1016, N=1024: 1016/1024 = 0,9922.",
        "P(0)=99,22% (ideal 100%).",
        "O ruído de fase não é visível na população Z; ele aparece na coerência.",
    ),
    "E15": N(
        "O QASM carrega o mesmo GHZ; a proxy é (N₀₀₀₀+N₁₁₁₁)/N.",
        "(418+389)/1024 = 807/1024 = 0,7881.",
        "78,81%, igual ao GHZ montado no console.",
        "O formato QASM não muda o circuito; o backend e a calibração mudam.",
    ),
    "E16": N(
        "⟨Z⟩ = (N₀−N₁)/N; ⟨X⟩ = (N₀−N₁)/N na base X.",
        "Z: (530−494)/1024=0,0352; X: (1016−8)/1024=0,9844.",
        "⟨Z⟩=+0,035; ⟨X⟩=+0,984.",
        "O estado é aproximadamente |+⟩; a pequena componente Z é erro.",
    ),
    "E17": N(
        "P(000) = N₀₀₀/N; ideal 1/4 = 0,25.",
        "N₀₀₀=235, N=1024: 235/1024 = 0,2295.",
        "P(000)=22,95% (ideal 25%).",
        "A caminhada de três qubits distribui amplitude; o padrão depende da fase.",
    ),
    "E18": N(
        "P(1)=N₁/N; EP=√(p(1−p)/N).",
        "N₁=494, N=1024: p=0,4824; EP=√(0,4824×0,5176/1024)=0,0156.",
        "P(1)=48,24% ± 1,56% (1 EP).",
        "O desvio de 50% é compatível com amostragem; não prova viés do backend.",
    ),
}
