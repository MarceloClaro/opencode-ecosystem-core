# Gabarito comentado: 100 checkpoints {#gabarito}


Cada conceito tem **um checkpoint**, repetido nas 10 lentes e nos 3 níveis.
Muitas perguntas são abertas: a resposta é um **critério de qualidade**, não
uma frase única. Se a sua resposta não citar o conceito e um limite, volte
à lauda indicada.

> **Como usar:** tente responder sem consultar; depois leia a resposta
> esperada e o critério. O objetivo não é acertar a frase do livro; é
> conseguir explicar, aplicar e reconhecer o limite.

## G001 — Bit {#g-001}

**Pergunta:** Você consegue escrever seu primeiro nome em binário?

**Resposta esperada:** Um bit é a menor diferença que decidimos registrar: 0 ou 1.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A analogia não explica probabilidade; o bit clássico é exclusivo.

**Onde conferir:** [ideia](#l-0001) · [além](#l-0006) · [prática](#l-0003) · [checkpoint](#l-0010)

**Experimento E01 — Base |0⟩:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** Com 8 bits, há 256 combinações; uma letra ASCII cabe em 8 bits.

## G002 — Qubit {#g-002}

**Pergunta:** Você consegue calcular P(0) para α=0,6?

**Resposta esperada:** Um qubit é descrito por duas amplitudes, e a medição produz um resultado.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A moeda tem lado definido; o qubit não tem valor escondido.

**Onde conferir:** [ideia](#l-0011) · [além](#l-0016) · [prática](#l-0013) · [checkpoint](#l-0020)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** A esfera de Bloch representa um qubit; o interior não é acessível.

## G003 — Amplitude {#g-003}

**Pergunta:** Você consegue explicar por que |α|² + |β|² = 1?

**Resposta esperada:** Amplitude é o número que dá peso a cada estado de base.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A amplitude não é uma probabilidade; é preciso elevar ao quadrado.

**Onde conferir:** [ideia](#l-0021) · [além](#l-0026) · [prática](#l-0023) · [checkpoint](#l-0030)

**Experimento E09 — Codificação de amplitude:** simulado P(1) = 0,735 (ideal 0,750); backend P(1) = 0,743 (ideal 0,750); sobreposição 99,2%.

**Complemento:** A regra de Born transforma amplitude em probabilidade.

## G004 — Probabilidade {#g-004}

**Pergunta:** Você consegue distinguir probabilidade de frequência observada?

**Resposta esperada:** Probabilidade é a previsão de longo prazo para um resultado.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Uma amostra pequena flutua; a probabilidade não garante o próximo resultado.

**Onde conferir:** [ideia](#l-0031) · [além](#l-0036) · [prática](#l-0033) · [checkpoint](#l-0040)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** A lei dos grandes números explica por que a frequência se estabiliza.

## G005 — Medição {#g-005}

**Pergunta:** Você consegue explicar por que a ordem das medições importa?

**Resposta esperada:** Medir produz um resultado e altera o estado; não é ler um valor escondido.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A caixa pode já ter um valor; o qubit não é assim.

**Onde conferir:** [ideia](#l-0041) · [além](#l-0046) · [prática](#l-0043) · [checkpoint](#l-0050)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** O 'colapso' é um nome para a atualização do estado após a medição.

## G006 — Base {#g-006}

**Pergunta:** Você consegue explicar por que medir na base errada dá ruído?

**Resposta esperada:** Uma base é o conjunto de estados em relação ao qual medimos.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Bases diferentes não são 'ângulos' da mesma foto; são perguntas diferentes.

**Onde conferir:** [ideia](#l-0051) · [além](#l-0056) · [prática](#l-0053) · [checkpoint](#l-0060)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** BB84 usa duas bases incompatíveis para detectar espionagem.

## G007 — Fase {#g-007}

**Pergunta:** Você consegue prever o resultado de H→Z→H?

**Resposta esperada:** Fase é a relação entre amplitudes; ela não aparece na medição isolada.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A fase não é um atraso no tempo real; é uma relação matemática.

**Onde conferir:** [ideia](#l-0061) · [além](#l-0066) · [prática](#l-0063) · [checkpoint](#l-0070)

**Experimento E04 — Interferência H-Z-H:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A fase relativa é o recurso que permite a interferência.

## G008 — Interferência {#g-008}

**Pergunta:** Você consegue explicar H→H e H→Z→H?

**Resposta esperada:** Interferência é a soma de amplitudes que reforça ou cancela probabilidades.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A amplitude quântica não é uma vibração material.

**Onde conferir:** [ideia](#l-0071) · [além](#l-0076) · [prática](#l-0073) · [checkpoint](#l-0080)

**Experimento E04 — Interferência H-Z-H:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** O experimento de dupla fenda é a demonstração clássica.

## G009 — Emaranhamento {#g-009}

**Pergunta:** Você consegue explicar por que a marginal de Bob é 50/50?

**Resposta esperada:** Emaranhamento é uma correlação quântica entre partes de um estado conjunto.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: As luvas têm valores escondidos; o emaranhamento não é explicado por variáveis locais.

**Onde conferir:** [ideia](#l-0081) · [além](#l-0086) · [prática](#l-0083) · [checkpoint](#l-0090)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** Bell mostrou que variáveis ocultas locais não reproduzem as correlações.

## G010 — Estado de Bell {#g-010}

**Pergunta:** Você consegue listar os quatro estados de Bell?

**Resposta esperada:** O estado de Bell é a forma mais simples de emaranhamento maximal.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A imagem das moedas sugere um mecanismo que a teoria não afirma.

**Onde conferir:** [ideia](#l-0091) · [além](#l-0096) · [prática](#l-0093) · [checkpoint](#l-0100)

**Experimento E07 — CHSH:** simulado S = 2,828 (ideal 2,828); backend S = 2,383 (ideal 2,828); sobreposição 93,6%.

**Complemento:** O estado de Bell é usado em teleportação e criptografia.

## G011 — Onda piloto {#g-011}

**Pergunta:** Você consegue explicar o que a onda guia e o que ela não guia?

**Resposta esperada:** Na teoria de Bohm, a função de onda guia partículas com posição definida.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O rio é matemático e, para várias partículas, vive em muitas dimensões.

**Onde conferir:** [ideia](#l-0101) · [além](#l-0106) · [prática](#l-0103) · [checkpoint](#l-0110)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** Bohm publicou a teoria em 1952; ela reproduz as previsões não relativísticas.

## G012 — Equação do guia {#g-012}

**Pergunta:** Você consegue explicar por que a fase importa para a trajetória?

**Resposta esperada:** A velocidade da partícula depende do gradiente da fase da função de onda.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação é não local para várias partículas; não é uma força clássica.

**Onde conferir:** [ideia](#l-0111) · [além](#l-0116) · [prática](#l-0113) · [checkpoint](#l-0120)

**Experimento E04 — Interferência H-Z-H:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A equação de Bohm é uma releitura da equação de Schrödinger.

## G013 — Equilíbrio quântico {#g-013}

**Pergunta:** Você consegue explicar o que é uma distribuição de equilíbrio?

**Resposta esperada:** A distribuição |ψ|² é preservada pela dinâmica de Bohm.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A hipótese explica por que a regra de Born funciona, mas não por que o universo começou assim.

**Onde conferir:** [ideia](#l-0121) · [além](#l-0126) · [prática](#l-0123) · [checkpoint](#l-0130)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** A equivariância é a propriedade matemática central.

## G014 — Não localidade {#g-014}

**Pergunta:** Você consegue explicar por que não há signaling?

**Resposta esperada:** Na teoria de Bohm, a velocidade de uma partícula depende das outras.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A não localidade não permite enviar sinais controláveis.

**Onde conferir:** [ideia](#l-0131) · [além](#l-0136) · [prática](#l-0133) · [checkpoint](#l-0140)

**Experimento E07 — CHSH:** simulado S = 2,828 (ideal 2,828); backend S = 2,383 (ideal 2,828); sobreposição 93,6%.

**Complemento:** O teorema de Bell mostra que a não localidade é difícil de evitar.

## G015 — Colapso efetivo {#g-015}

**Pergunta:** Você consegue explicar a diferença entre colapso e colapso efetivo?

**Resposta esperada:** Em Bohm, não há colapso fundamental; a partícula termina em uma componente.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A imagem do galho é clássica; a função de onda é matemática.

**Onde conferir:** [ideia](#l-0141) · [além](#l-0146) · [prática](#l-0143) · [checkpoint](#l-0150)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A medição é um processo físico, não um postulado místico.

## G016 — Ordem implicada {#g-016}

**Pergunta:** Você consegue explicar o limite da analogia?

**Resposta esperada:** Bohm propôs que o mundo explícito se desdobra de uma totalidade implicada.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: É uma visão filosófica, não uma teoria física testável por si só.

**Onde conferir:** [ideia](#l-0151) · [além](#l-0156) · [prática](#l-0153) · [checkpoint](#l-0160)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A analogia do holograma é matemática e clássica.

## G017 — Holomovimento {#g-017}

**Pergunta:** Você consegue dar um exemplo de processo que vira forma?

**Resposta esperada:** Holomovimento é o fluxo dinâmico do qual emergem formas explícitas.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O termo é filosófico; não é uma equação operacional.

**Onde conferir:** [ideia](#l-0161) · [além](#l-0166) · [prática](#l-0163) · [checkpoint](#l-0170)

**Experimento E17 — Interferência de três qubits:** simulado P(000) = 0,258 (ideal 0,250); backend P(000) = 0,229 (ideal 0,250); sobreposição 90,8%.

**Complemento:** Bohm usou a imagem para pensar processo em vez de coisas.

## G018 — Diálogo {#g-018}

**Pergunta:** Você consegue listar três gestos do diálogo?

**Resposta esperada:** Diálogo é investigação coletiva de suposições, não debate para vencer.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Diálogo não é terapia, assembleia ou busca obrigatória de consenso.

**Onde conferir:** [ideia](#l-0171) · [além](#l-0176) · [prática](#l-0173) · [checkpoint](#l-0180)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** Bohm distingue diálogo de debate em 'On Dialogue'.

## G019 — Suspensão de suposições {#g-019}

**Pergunta:** Você consegue nomear uma suposição sua sobre 'medir'?

**Resposta esperada:** Suspender é colocar uma crença entre parênteses para examiná-la.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Suspender não é abandonar; é ganhar distância para observar.

**Onde conferir:** [ideia](#l-0181) · [além](#l-0186) · [prática](#l-0183) · [checkpoint](#l-0190)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A suspensão é uma prática, não uma prova lógica.

## G020 — Totalidade {#g-020}

**Pergunta:** Você consegue explicar a diferença entre soma e relação?

**Resposta esperada:** Totalidade é a ideia de que o todo não se reduz a partes independentes.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Totalidade não significa harmonia; pode haver conflito e desordem.

**Onde conferir:** [ideia](#l-0191) · [além](#l-0196) · [prática](#l-0193) · [checkpoint](#l-0200)

**Experimento E06 — GHZ de 4 qubits:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A totalidade aparece na física, na ecologia e na pedagogia.

## G021 — Porta X {#g-021}

**Pergunta:** Você consegue prever X|0⟩ e X|1⟩?

**Resposta esperada:** A porta X inverte 0 e 1, como um NOT quântico.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: X não cria superposição; ela apenas troca os estados de base.

**Onde conferir:** [ideia](#l-0201) · [além](#l-0206) · [prática](#l-0203) · [checkpoint](#l-0210)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** X é a matriz [[0,1],[1,0]]; X² = I.

## G022 — Porta H {#g-022}

**Pergunta:** Você consegue explicar por que H(H|0⟩)=|0⟩?

**Resposta esperada:** H cria uma superposição equilibrada a partir de um estado de base.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: H não é 'um pouco de 0 e um pouco de 1'; é uma transformação precisa.

**Onde conferir:** [ideia](#l-0211) · [além](#l-0216) · [prática](#l-0213) · [checkpoint](#l-0220)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** H é a matriz (1/√2)[[1,1],[1,-1]]; H² = I.

## G023 — Porta Z {#g-023}

**Pergunta:** Você consegue explicar H→Z→H?

**Resposta esperada:** Z troca o sinal da amplitude de |1⟩ sem mudar probabilidades isoladas.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Z não muda a probabilidade; ela muda o que acontece depois.

**Onde conferir:** [ideia](#l-0221) · [além](#l-0226) · [prática](#l-0223) · [checkpoint](#l-0230)

**Experimento E04 — Interferência H-Z-H:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** Z é diag(1,-1); a fase relativa é o recurso da interferência.

## G024 — CNOT {#g-024}

**Pergunta:** Você consegue listar a tabela verdade do CNOT?

**Resposta esperada:** CNOT inverte o alvo quando o controle é 1.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: CNOT não copia um estado quântico arbitrário; ela cria correlação.

**Onde conferir:** [ideia](#l-0231) · [além](#l-0236) · [prática](#l-0233) · [checkpoint](#l-0240)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** CNOT é a porta de duas entradas que gera o estado de Bell.

## G025 — Circuito {#g-025}

**Pergunta:** Você consegue desenhar um circuito de Bell?

**Resposta esperada:** Um circuito é uma sequência de portas e medições sobre qubits.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A ordem importa; matrizes não comutam em geral.

**Onde conferir:** [ideia](#l-0241) · [além](#l-0246) · [prática](#l-0243) · [checkpoint](#l-0250)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A profundidade do circuito mede o número de camadas.

## G026 — Circuito de Bell {#g-026}

**Pergunta:** Você consegue prever os quatro resultados possíveis?

**Resposta esperada:** H no controle e CNOT produzem (|00⟩+|11⟩)/√2.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A imagem clássica não explica a violação de Bell.

**Onde conferir:** [ideia](#l-0251) · [além](#l-0256) · [prática](#l-0253) · [checkpoint](#l-0260)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** O circuito de Bell é o 'olá, mundo' do emaranhamento.

## G027 — GHZ {#g-027}

**Pergunta:** Você consegue escrever o QASM 2.0 do GHZ de 4 qubits?

**Resposta esperada:** GHZ é a generalização do Bell para três ou mais qubits.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Em hardware real, o GHZ perde coerência rapidamente com o número de qubits.

**Onde conferir:** [ideia](#l-0261) · [além](#l-0266) · [prática](#l-0263) · [checkpoint](#l-0270)

**Experimento E06 — GHZ de 4 qubits:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** O GHZ é usado em metrologia e testes de não localidade.

## G028 — QASM 2.0 {#g-028}

**Pergunta:** Você consegue validar seu QASM no Qiskit localmente?

**Resposta esperada:** QASM 2.0 é uma linguagem textual para descrever circuitos quânticos.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: QASM não é um algoritmo; é uma notação de circuito.

**Onde conferir:** [ideia](#l-0271) · [além](#l-0276) · [prática](#l-0273) · [checkpoint](#l-0280)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** QASM 2.0 é aceito por CIQuanta, Tiangong e Qiskit.

## G029 — Transpilação {#g-029}

**Pergunta:** Você consegue explicar por que a profundidade aumentou?

**Resposta esperada:** Transpilar adapta o circuito às portas e conexões do hardware.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A tradução pode aumentar a profundidade e o ruído.

**Onde conferir:** [ideia](#l-0281) · [além](#l-0286) · [prática](#l-0283) · [checkpoint](#l-0290)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** O mapeamento de qubits lógicos para físicos é parte do processo.

## G030 — Medição múltipla {#g-030}

**Pergunta:** Você consegue calcular o erro padrão de uma proporção?

**Resposta esperada:** Medir vários qubits produz um bitstring e uma distribuição.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A distribuição não mostra o estado completo; mostra uma amostra.

**Onde conferir:** [ideia](#l-0291) · [além](#l-0296) · [prática](#l-0293) · [checkpoint](#l-0300)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** A amostragem tem erro estatístico que diminui com o número de tiros.

## G031 — PennyLane {#g-031}

**Pergunta:** Você consegue escrever um QNode de Bell?

**Resposta esperada:** PennyLane é uma biblioteca de circuitos quânticos diferenciáveis.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A diferenciação automática não substitui a interpretação física.

**Onde conferir:** [ideia](#l-0301) · [além](#l-0306) · [prática](#l-0303) · [checkpoint](#l-0310)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** PennyLane integra com simuladores e vários provedores.

## G032 — Cirq {#g-032}

**Pergunta:** Você consegue ler o diagrama textual do Cirq?

**Resposta esperada:** Cirq é uma biblioteca do Google baseada em linhas de qubits.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O diagrama textual é útil, mas não é uma figura de livro.

**Onde conferir:** [ideia](#l-0311) · [além](#l-0316) · [prática](#l-0313) · [checkpoint](#l-0320)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** Cirq é usado em pesquisa com hardware supercondutor.

## G033 — Qiskit {#g-033}

**Pergunta:** Você consegue comparar o Bell de Qiskit com o de Cirq?

**Resposta esperada:** Qiskit é a biblioteca da IBM para circuitos, estados e visualização.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O desenho do circuito não é o circuito físico; é uma representação.

**Onde conferir:** [ideia](#l-0321) · [além](#l-0326) · [prática](#l-0323) · [checkpoint](#l-0330)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** Qiskit inclui Statevector, transpilação e visualizações.

## G034 — QNode {#g-034}

**Pergunta:** Você consegue explicar o papel do dispositivo no QNode?

**Resposta esperada:** Um QNode é uma função quântica que retorna uma medição.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O QNode não é o hardware; é a descrição executável.

**Onde conferir:** [ideia](#l-0331) · [além](#l-0336) · [prática](#l-0333) · [checkpoint](#l-0340)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** QNodes podem ser diferenciados e otimizados.

## G035 — Cirq Circuit {#g-035}

**Pergunta:** Você consegue desenhar um circuito com dois momentos?

**Resposta esperada:** Um Circuit do Cirq é uma sequência de momentos e operações.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Momentos não são tempo físico; são uma ordenação lógica.

**Onde conferir:** [ideia](#l-0341) · [além](#l-0346) · [prática](#l-0343) · [checkpoint](#l-0350)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** O Cirq usa momentos para organizar operações paralelas.

## G036 — QuantumCircuit {#g-036}

**Pergunta:** Você consegue explicar a diferença entre qreg e creg?

**Resposta esperada:** QuantumCircuit é a estrutura do Qiskit para portas e medições.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O circuito lógico precisa ser transpilado para o hardware.

**Onde conferir:** [ideia](#l-0351) · [além](#l-0356) · [prática](#l-0353) · [checkpoint](#l-0360)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** O Qiskit separa circuito lógico e circuito transpilado.

## G037 — Statevector {#g-037}

**Pergunta:** Você consegue calcular as probabilidades a partir do vetor?

**Resposta esperada:** Statevector é o vetor de amplitudes de um sistema quântico.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O vetor cresce como 2^n; não é acessível por medição única.

**Onde conferir:** [ideia](#l-0361) · [além](#l-0366) · [prática](#l-0363) · [checkpoint](#l-0370)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** O estado é uma descrição matemática; a medição é uma amostra.

## G038 — Esfera de Bloch {#g-038}

**Pergunta:** Você consegue localizar |0⟩, |1⟩ e H|0⟩ na esfera?

**Resposta esperada:** A esfera de Bloch representa o estado de um único qubit.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A esfera não mostra emaranhamento de dois qubits.

**Onde conferir:** [ideia](#l-0371) · [além](#l-0376) · [prática](#l-0373) · [checkpoint](#l-0380)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** O interior da esfera não é acessível; a superfície é o estado puro.

## G039 — Amostragem {#g-039}

**Pergunta:** Você consegue explicar por que a frequência flutua?

**Resposta esperada:** Amostrar é repetir preparo e medição para estimar probabilidades.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A amostra não é o estado; é uma sombra estatística.

**Onde conferir:** [ideia](#l-0381) · [além](#l-0386) · [prática](#l-0383) · [checkpoint](#l-0390)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** O erro padrão cai com a raiz do número de tiros.

## G040 — gjq-client {#g-040}

**Pergunta:** Você consegue listar um backend sem executar um circuito?

**Resposta esperada:** gjq-client é o cliente Python da plataforma quântica Guoji/Tiangong.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O cliente não garante acesso; depende de conta, fila e backend.

**Onde conferir:** [ideia](#l-0391) · [além](#l-0396) · [prática](#l-0393) · [checkpoint](#l-0400)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** O SDK suporta Sampler, Estimator e Sessões; o servidor MCP gjq-runtime-mcp-server expõe sample_tool e estimate_tool para agentes.

## G041 — Supercondutor {#g-041}

**Pergunta:** Quem paga a energia e a manutenção de um criostato?

**Resposta esperada:** Computadores supercondutores usam circuitos resfriados a milikelvin.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0401) · [além](#l-0406) · [prática](#l-0403) · [checkpoint](#l-0410)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G042 — Qubit físico {#g-042}

**Pergunta:** Quem tem acesso ao hardware e quem só vê resultados?

**Resposta esperada:** Um qubit físico é um dispositivo concreto, com erros e calibração.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0411) · [além](#l-0416) · [prática](#l-0413) · [checkpoint](#l-0420)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G043 — Decoerência {#g-043}

**Pergunta:** Um ambiente monitorado pode ser tão invasivo quanto um espião?

**Resposta esperada:** Decoerência é a perda de informação quântica para o ambiente.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0421) · [além](#l-0426) · [prática](#l-0423) · [checkpoint](#l-0430)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G044 — T1 e T2 {#g-044}

**Pergunta:** Quem publica esses dados e com que frequência?

**Resposta esperada:** T1 mede relaxação de energia; T2 mede perda de coerência de fase.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0431) · [além](#l-0436) · [prática](#l-0433) · [checkpoint](#l-0440)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G045 — Erro de leitura {#g-045}

**Pergunta:** Um erro sistemático pode prejudicar um grupo específico?

**Resposta esperada:** A leitura de um qubit pode inverter o resultado com alguma probabilidade.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0441) · [além](#l-0446) · [prática](#l-0443) · [checkpoint](#l-0450)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G046 — Ruído {#g-046}

**Pergunta:** Quem decide o nível de ruído aceitável em um serviço público?

**Resposta esperada:** Ruído é toda perturbação indesejada que afeta o estado ou a leitura.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0451) · [além](#l-0456) · [prática](#l-0453) · [checkpoint](#l-0460)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G047 — CIQuanta {#g-047}

**Pergunta:** Quem pode usar os computadores e em que condições?

**Resposta esperada:** O CIQuanta é o centro de computação quântica da Paraíba, em João Pessoa.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0461) · [além](#l-0466) · [prática](#l-0463) · [checkpoint](#l-0470)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G048 — Tiangong {#g-048}

**Pergunta:** Uma dependência externa pode comprometer a soberania de dados?

**Resposta esperada:** Tiangong/Guoji é a plataforma de nuvem quântica com simuladores e hardware.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0471) · [além](#l-0476) · [prática](#l-0473) · [checkpoint](#l-0480)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G049 — Fila de jobs {#g-049}

**Pergunta:** Uma fila mal projetada pode excluir escolas com menos recursos?

**Resposta esperada:** Jobs em nuvem entram em fila e podem demorar ou falhar.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0481) · [além](#l-0486) · [prática](#l-0483) · [checkpoint](#l-0490)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G050 — API key {#g-050}

**Pergunta:** Quem audita o uso da chave e por quanto tempo?

**Resposta esperada:** Uma API key é uma credencial secreta que autoriza o acesso à nuvem.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O resultado de hoje não garante o de amanhã; calibração muda.

**Onde conferir:** [ideia](#l-0491) · [além](#l-0496) · [prática](#l-0493) · [checkpoint](#l-0500)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G051 — GHZ real {#g-051}

**Pergunta:** Quem deve saber que o resultado tem 21% de erro?

**Resposta esperada:** O GHZ de 4 qubits no Guoji08 mostrou 78,8% de fidelidade proxy.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0501) · [além](#l-0506) · [prática](#l-0503) · [checkpoint](#l-0510)

**Experimento E06 — GHZ de 4 qubits:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G052 — VQC XOR {#g-052}

**Pergunta:** Um resultado de 100% em 4 pontos pode enganar uma política pública?

**Resposta esperada:** Um classificador de 2 qubits aprendeu XOR com 4 pontos e 100% no backend.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0511) · [além](#l-0516) · [prática](#l-0513) · [checkpoint](#l-0520)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G053 — Classificador {#g-053}

**Pergunta:** Quem responde quando o classificador erra?

**Resposta esperada:** Um classificador mapeia dados para rótulos por meio de um modelo.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0521) · [além](#l-0526) · [prática](#l-0523) · [checkpoint](#l-0530)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G054 — Encoding {#g-054}

**Pergunta:** Dados pessoais podem ser reconstruídos a partir do encoding?

**Resposta esperada:** Encoding é a forma de colocar dados clássicos em um circuito quântico.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0531) · [além](#l-0536) · [prática](#l-0533) · [checkpoint](#l-0540)

**Experimento E09 — Codificação de amplitude:** simulado P(1) = 0,735 (ideal 0,750); backend P(1) = 0,743 (ideal 0,750); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G055 — Ansatz {#g-055}

**Pergunta:** Quem decide a arquitetura e com base em quê?

**Resposta esperada:** Ansatz é a arquitetura parametrizada do circuito.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0541) · [além](#l-0546) · [prática](#l-0543) · [checkpoint](#l-0550)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G056 — Treino {#g-056}

**Pergunta:** Um modelo treinado com dados enviesados pode ser corrigido?

**Resposta esperada:** Treinar é ajustar parâmetros para reduzir uma função de perda.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0551) · [além](#l-0556) · [prática](#l-0553) · [checkpoint](#l-0560)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G057 — Acurácia {#g-057}

**Pergunta:** Uma métrica única pode esconder desigualdades?

**Resposta esperada:** Acurácia é a fração de acertos em um conjunto de teste.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0561) · [além](#l-0566) · [prática](#l-0563) · [checkpoint](#l-0570)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G058 — Phase damping {#g-058}

**Pergunta:** Um ruído invisível pode ser ignorado em uma auditoria?

**Resposta esperada:** Phase damping destrói a coerência de fase sem mudar populações.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0571) · [além](#l-0576) · [prática](#l-0573) · [checkpoint](#l-0580)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G059 — Depolarizing {#g-059}

**Pergunta:** Quem aceita a perda de precisão em troca de velocidade?

**Resposta esperada:** Depolarizing mistura o estado com ruído isotrópico.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0581) · [além](#l-0586) · [prática](#l-0583) · [checkpoint](#l-0590)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G060 — Ruído benéfico? {#g-060}

**Pergunta:** Quem repete o experimento e publica o resultado negativo?

**Resposta esperada:** A hipótese do repositório é que um nível pequeno de ruído pode regularizar o treino.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O teste é pequeno; não generaliza para outros dados ou modelos.

**Onde conferir:** [ideia](#l-0591) · [além](#l-0596) · [prática](#l-0593) · [checkpoint](#l-0600)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G061 — Vetor {#g-061}

**Pergunta:** Quem pode visualizar um vetor de 50 qubits?

**Resposta esperada:** Um vetor de estado lista as amplitudes de cada configuração.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0601) · [além](#l-0606) · [prática](#l-0603) · [checkpoint](#l-0610)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G062 — Matriz {#g-062}

**Pergunta:** Uma operação linear pode ser auditada?

**Resposta esperada:** Uma matriz representa uma operação linear sobre o vetor de estado.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0611) · [além](#l-0616) · [prática](#l-0613) · [checkpoint](#l-0620)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G063 — Produto interno {#g-063}

**Pergunta:** Dois estados distintos podem ser confundidos por um observador?

**Resposta esperada:** O produto interno mede a sobreposição entre dois estados.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0621) · [além](#l-0626) · [prática](#l-0623) · [checkpoint](#l-0630)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G064 — Produto tensorial {#g-064}

**Pergunta:** Quem consegue armazenar o estado completo de muitos qubits?

**Resposta esperada:** O produto tensorial combina espaços de qubits.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0631) · [além](#l-0636) · [prática](#l-0633) · [checkpoint](#l-0640)

**Experimento E13 — Produto tensorial |01⟩:** simulado P(01) = 1,000 (ideal 1,000); backend P(01) = 0,957 (ideal 1,000); sobreposição 95,7%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G065 — Matriz densidade {#g-065}

**Pergunta:** Uma mistura estatística pode esconder responsabilidade?

**Resposta esperada:** A matriz densidade descreve estados puros e mistos.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0641) · [além](#l-0646) · [prática](#l-0643) · [checkpoint](#l-0650)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G066 — Traço {#g-066}

**Pergunta:** Uma soma que sempre dá 1 pode mascarar perdas?

**Resposta esperada:** O traço é a soma da diagonal; para densidades, vale 1.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0651) · [além](#l-0656) · [prática](#l-0653) · [checkpoint](#l-0660)

**Experimento E05 — Estado de Bell:** simulado P(00)+P(11) = 1,000 (ideal 1,000); backend P(00)+P(11) = 0,941 (ideal 1,000); sobreposição 94,1%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G067 — Autovalor {#g-067}

**Pergunta:** Quem escolhe quais observáveis medir?

**Resposta esperada:** Autovalores são os valores possíveis de uma medição.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0661) · [além](#l-0666) · [prática](#l-0663) · [checkpoint](#l-0670)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G068 — Fourier {#g-068}

**Pergunta:** Uma compressão pode apagar detalhes importantes?

**Resposta esperada:** A transformada de Fourier decompõe um sinal em frequências.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0671) · [além](#l-0676) · [prática](#l-0673) · [checkpoint](#l-0680)

**Experimento E12 — QFT de 3 qubits:** simulado P(000) = 0,117 (ideal 0,125); backend P(000) = 0,120 (ideal 0,125); sobreposição 95,7%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G069 — Holograma {#g-069}

**Pergunta:** Quem controla a reconstrução controla a narrativa?

**Resposta esperada:** Um holograma distribui informação sobre o todo.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0681) · [além](#l-0686) · [prática](#l-0683) · [checkpoint](#l-0690)

**Experimento E17 — Interferência de três qubits:** simulado P(000) = 0,258 (ideal 0,250); backend P(000) = 0,229 (ideal 0,250); sobreposição 90,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G070 — Fourier quântico {#g-070}

**Pergunta:** Algoritmos de fatoração podem ameaçar a privacidade?

**Resposta esperada:** A QFT é a versão quântica da transformada de Fourier.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A equação não explica por que o mundo segue a equação.

**Onde conferir:** [ideia](#l-0691) · [além](#l-0696) · [prática](#l-0693) · [checkpoint](#l-0700)

**Experimento E12 — QFT de 3 qubits:** simulado P(000) = 0,117 (ideal 0,125); backend P(000) = 0,120 (ideal 0,125); sobreposição 95,7%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G071 — Nanoaula {#g-071}

**Pergunta:** Quem garante que os tijolos formam uma casa?

**Resposta esperada:** Uma nanoaula é uma unidade de 5 a 10 minutos com um conceito e uma evidência.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0701) · [além](#l-0706) · [prática](#l-0703) · [checkpoint](#l-0710)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G072 — Autodidatismo {#g-072}

**Pergunta:** Quem tem tempo e silêncio para estudar sozinho?

**Resposta esperada:** Autodidatismo é a capacidade de organizar o próprio estudo com critérios.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0711) · [além](#l-0716) · [prática](#l-0713) · [checkpoint](#l-0720)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G073 — Feedback {#g-073}

**Pergunta:** Quem recebe feedback e quem pode dá-lo?

**Resposta esperada:** Feedback é informação sobre a diferença entre o resultado e a meta.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0721) · [além](#l-0726) · [prática](#l-0723) · [checkpoint](#l-0730)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G074 — Checkpoint {#g-074}

**Pergunta:** Um checkpoint pode ser usado para excluir em vez de ensinar?

**Resposta esperada:** Um checkpoint é uma parada verificável antes de avançar.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0731) · [além](#l-0736) · [prática](#l-0733) · [checkpoint](#l-0740)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G075 — Erro produtivo {#g-075}

**Pergunta:** Quem é punido por errar em público?

**Resposta esperada:** Erro produtivo é aquele que revela uma hipótese ou lacuna.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0741) · [além](#l-0746) · [prática](#l-0743) · [checkpoint](#l-0750)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G076 — Roda de diálogo {#g-076}

**Pergunta:** Quem não consegue falar em roda e como incluir?

**Resposta esperada:** A roda organiza falas, escuta e silêncio em um tempo protegido.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0751) · [além](#l-0756) · [prática](#l-0753) · [checkpoint](#l-0760)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G077 — Projeto {#g-077}

**Pergunta:** Quem se beneficia e quem arca com os custos?

**Resposta esperada:** Um projeto articula pergunta, hipótese, experimento, evidência e limite.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0761) · [além](#l-0766) · [prática](#l-0763) · [checkpoint](#l-0770)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G078 — Rubrica {#g-078}

**Pergunta:** Uma rubrica pode reproduzir privilégios de linguagem?

**Resposta esperada:** Uma rubrica descreve níveis de desempenho observáveis.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0771) · [além](#l-0776) · [prática](#l-0773) · [checkpoint](#l-0780)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G079 — Adaptação {#g-079}

**Pergunta:** Quem participa da decisão de adaptar?

**Resposta esperada:** Adaptar é ajustar acesso, tempo e linguagem sem baixar a meta conceitual.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0781) · [além](#l-0786) · [prática](#l-0783) · [checkpoint](#l-0790)

**Experimento E09 — Codificação de amplitude:** simulado P(1) = 0,735 (ideal 0,750); backend P(1) = 0,743 (ideal 0,750); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G080 — Acessibilidade {#g-080}

**Pergunta:** Quem foi consultado no design?

**Resposta esperada:** Acessibilidade é remover barreiras para que todos possam participar.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: A técnica não funciona igual para todos os estudantes.

**Onde conferir:** [ideia](#l-0791) · [além](#l-0796) · [prática](#l-0793) · [checkpoint](#l-0800)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G081 — Acesso {#g-081}

**Pergunta:** Uma política de acesso pode reproduzir desigualdades regionais?

**Resposta esperada:** Acesso é a possibilidade real de usar infraestrutura, dados e formação.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0801) · [além](#l-0806) · [prática](#l-0803) · [checkpoint](#l-0810)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G082 — Dupla finalidade {#g-082}

**Pergunta:** Uma ferramenta usada para vigiar pode ser justificada por segurança?

**Resposta esperada:** A mesma tecnologia pode servir a fins benéficos e danosos.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0811) · [além](#l-0816) · [prática](#l-0813) · [checkpoint](#l-0820)

**Experimento E07 — CHSH:** simulado S = 2,828 (ideal 2,828); backend S = 2,383 (ideal 2,828); sobreposição 93,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G083 — Privacidade {#g-083}

**Pergunta:** Um modelo pode revelar dados usados no treinamento?

**Resposta esperada:** Privacidade é o controle sobre informação que diz respeito a você.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0821) · [além](#l-0826) · [prática](#l-0823) · [checkpoint](#l-0830)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G084 — LGPD {#g-084}

**Pergunta:** Quem é o controlador e quem é o operador?

**Resposta esperada:** A LGPD regula o tratamento de dados pessoais no Brasil.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0831) · [além](#l-0836) · [prática](#l-0833) · [checkpoint](#l-0840)

**Experimento E08 — Gerador quântico de números:** simulado |P(0)-P(1)| = 0,037 (ideal 0,000); backend |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição 96,4%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G085 — Custo {#g-085}

**Pergunta:** Um recurso caro deve ser reservado a que tipo de pergunta?

**Resposta esperada:** Custo inclui hardware, energia, tempo, fila e formação de pessoas.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0841) · [além](#l-0846) · [prática](#l-0843) · [checkpoint](#l-0850)

**Experimento E18 — Amostragem binomial:** simulado P(1) = 0,483 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 99,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G086 — Ambiente {#g-086}

**Pergunta:** Quem arca com o passivo ambiental?

**Resposta esperada:** Refrigeração e energia têm impacto ambiental.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0851) · [além](#l-0856) · [prática](#l-0853) · [checkpoint](#l-0860)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G087 — Trabalho {#g-087}

**Pergunta:** A automação pode precarizar o trabalho de quem opera o sistema?

**Resposta esperada:** Novas tecnologias mudam tarefas e exigem novas formações.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0861) · [além](#l-0866) · [prática](#l-0863) · [checkpoint](#l-0870)

**Experimento E11 — Interferência de dois qubits:** simulado P(00) = 0,488 (ideal 0,500); backend P(00) = 0,474 (ideal 0,500); sobreposição 94,3%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G088 — Desinformação {#g-088}

**Pergunta:** Uma notícia verdadeira pode ser usada para enganar pelo enquadramento?

**Resposta esperada:** Desinformação é informação falsa ou fora de contexto que circula como verdade.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0871) · [além](#l-0876) · [prática](#l-0873) · [checkpoint](#l-0880)

**Experimento E07 — CHSH:** simulado S = 2,828 (ideal 2,828); backend S = 2,383 (ideal 2,828); sobreposição 93,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G089 — Consenso {#g-089}

**Pergunta:** Quem tem poder para encerrar a conversa?

**Resposta esperada:** Consenso é acordo suficiente para agir, não unanimidade de crenças.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0881) · [além](#l-0886) · [prática](#l-0883) · [checkpoint](#l-0890)

**Experimento E06 — GHZ de 4 qubits:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G090 — Responsabilidade {#g-090}

**Pergunta:** Uma empresa pode terceirizar a responsabilidade para o usuário?

**Resposta esperada:** Responsabilidade é responder por decisões e consequências.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: Não há consenso moral automático; há trade-offs.

**Onde conferir:** [ideia](#l-0891) · [além](#l-0896) · [prática](#l-0893) · [checkpoint](#l-0900)

**Experimento E02 — Base |1⟩ e leitura:** simulado P(1) = 1,000 (ideal 1,000); backend P(1) = 0,986 (ideal 1,000); sobreposição 98,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G091 — Pergunta {#g-091}

**Pergunta:** Quem formulou a pergunta e quem ficou fora?

**Resposta esperada:** Uma boa pergunta é delimitada, investigável e ligada a uma decisão.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0901) · [além](#l-0906) · [prática](#l-0903) · [checkpoint](#l-0910)

**Experimento E03 — Superposição H|0⟩:** simulado P(1) = 0,496 (ideal 0,500); backend P(1) = 0,482 (ideal 0,500); sobreposição 98,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G092 — Hipótese {#g-092}

**Pergunta:** Uma hipótese conveniente pode ser protegida de testes?

**Resposta esperada:** Uma hipótese é uma explicação testável, não uma opinião.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0911) · [além](#l-0916) · [prática](#l-0913) · [checkpoint](#l-0920)

**Experimento E07 — CHSH:** simulado S = 2,828 (ideal 2,828); backend S = 2,383 (ideal 2,828); sobreposição 93,6%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G093 — Evidência {#g-093}

**Pergunta:** Quem coletou a evidência e com que interesse?

**Resposta esperada:** Evidência é um dado ou observação que sustenta ou enfraquece uma afirmação.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0921) · [além](#l-0926) · [prática](#l-0923) · [checkpoint](#l-0930)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G094 — Limite {#g-094}

**Pergunta:** Quem é prejudicado quando o limite é escondido?

**Resposta esperada:** Limite é o que o modelo, o experimento ou a analogia não alcança.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0931) · [além](#l-0936) · [prática](#l-0933) · [checkpoint](#l-0940)

**Experimento E14 — Ruído de fase:** simulado P(0) = 1,000 (ideal 1,000); backend P(0) = 0,992 (ideal 1,000); sobreposição 99,2%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G095 — Replicação {#g-095}

**Pergunta:** Quem tem recursos para replicar um experimento caro?

**Resposta esperada:** Replicar é repetir um experimento com registros e condições explícitas.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0941) · [além](#l-0946) · [prática](#l-0943) · [checkpoint](#l-0950)

**Experimento E06 — GHZ de 4 qubits:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G096 — Narrativa {#g-096}

**Pergunta:** Uma narrativa heroica pode esconder custos e fracassos?

**Resposta esperada:** Narrativa organiza fatos em uma sequência com sentido.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0951) · [além](#l-0956) · [prática](#l-0953) · [checkpoint](#l-0960)

**Experimento E17 — Interferência de três qubits:** simulado P(000) = 0,258 (ideal 0,250); backend P(000) = 0,229 (ideal 0,250); sobreposição 90,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G097 — Visualização {#g-097}

**Pergunta:** Quem escolheu as cores e os destaques?

**Resposta esperada:** Visualização codifica dados em posição, cor e forma.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0961) · [além](#l-0966) · [prática](#l-0963) · [checkpoint](#l-0970)

**Experimento E16 — Esfera de Bloch:** simulado ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1); backend ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição 98,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G098 — Apresentação {#g-098}

**Pergunta:** Quem não terá acesso à sua apresentação?

**Resposta esperada:** Apresentar é tornar uma ideia compreensível para uma plateia específica.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0971) · [além](#l-0976) · [prática](#l-0973) · [checkpoint](#l-0980)

**Experimento E15 — GHZ via QASM 2.0:** simulado P(0000)+P(1111) = 1,000 (ideal 1,000); backend P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição 78,8%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G099 — Portfólio {#g-099}

**Pergunta:** Quem pode acessar o portfólio e por quanto tempo?

**Resposta esperada:** Portfólio é uma coleção organizada de evidências de aprendizagem.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0981) · [além](#l-0986) · [prática](#l-0983) · [checkpoint](#l-0990)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

## G100 — Próximo passo {#g-100}

**Pergunta:** Quem pode me ajudar a dar esse passo?

**Resposta esperada:** Próximo passo é a menor ação concreta que reduz incerteza.

**Critério:** a resposta deve citar o conceito e um limite. Limite do conceito: O projeto não esgota o problema; escolhe um recorte.

**Onde conferir:** [ideia](#l-0991) · [além](#l-0996) · [prática](#l-0993) · [checkpoint](#l-1000)

**Experimento E10 — Classificador XOR (VQC):** simulado Acurácia = 4/4; backend Acurácia = 4/4; sobreposição 95,9%.

**Complemento:** A lauda de laboratório mostra a aplicação.

> **Limite do gabarito:** ele não substitui a prática. Se você só ler a
> resposta, não aprende; se fizer a prática e explicar o resultado, aprende.