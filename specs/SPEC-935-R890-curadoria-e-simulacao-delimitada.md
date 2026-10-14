---
spec_id: SPEC-935-R890
title: Curadoria de quinze projetos e contrato honesto de simulação clássica
component: reasoning.quantum
status: implemented
test_file: tests/test_r890_quantum_provenance.py
---

# R890 — Curadoria complementar e simulação delimitada

## Intenção e fatos reproduzidos

O usuário pediu continuar a avaliação e adaptação de DeepChem, ipleiria-thesis,
ASSISTENTE-SHI, py-xiaozhi, xiaozhi-esp32-server, xiaozhi-esp32, TorBot,
litert-samples, anny, mcp_server_exe, torchquantum, ai-edge-quantizer,
AI-ML-Cheatsheets, whatsapp-mcp e genai-toolbox. Serão avaliadas fontes públicas
fixadas por commit, licença, contratos, dependências, rede e sobreposição.
Não instalar indiscriminadamente os runtimes nem conectar contas, voz ou serviços.
REA apoia a inspeção estática de alvos compatíveis; Python/TeX não ganham uma
análise semântica por simples menção à ferramenta.

A comparação com TorchQuantum expôs no Core uma suíte clássica predefinida
que ignora a pergunta, atribui confiança fixa 0.85 e chama massa de suporte de
fidelidade. A entropia de Shannon da medição era descrita como emaranhamento.
A presença de Qiskit ainda liberava a alocação Python de 2**n até n=100,
sem existir o dispatcher MPS anunciado. Essas observações não validam um modelo
ou equipamento quântico; são defeitos de contrato e de limite local.

## Adaptação escolhida

1. Preservar a suíte Bell/GHZ/superposição local, declarando
   `execution_kind=classical_simulation`, `backend=python_statevector`,
   `quantum_hardware_used=false`, `query_evaluated=false`.
2. A saída do motor não apresenta os experimentos fixos como resposta à pergunta.
   Confiança legada pode ser 0.0 com interpretação explícita; não é probabilidade
   calibrada. A evidência tipada retorna configuração, seeds, métricas e digest.
3. Renomear a massa no suporte da PMF para `support_mass`, sem chamá-la de
   fidelidade. Incluir distância de variação total entre frequências empíricas
   e a distribuição exata do simulador, preservando counts por seed.
   Isso descreve amostragem do próprio modelo, sem validar hardware/backend.
4. Identificar `measurement_entropy` como Shannon das probabilidades de
   medição. API legada `entanglement_entropy` não pode continuar afirmando
   que Shannon prova emaranhamento: ou calcular a partição declarada ou
   preservar alias depreciado explicitamente nomeado e sem tal alegação.
5. Limite rígido de 2 a 20 qubits antes da alocação, independentemente de
   Qiskit instalado. Inteiros estritos para qubits/shots/seeds, limites de
   shots e número de seeds antes de laços; cada seed deve estar em
   `0..2**63-1`, inclusive, antes de construir circuitos; informar os limites reais.
6. Preparar os pesos cumulativos da medição uma vez para evitar recalcular
   todo o vetor para cada shot, mantendo reprodutibilidade das seeds.
7. Conectar a proveniência ao retorno do primário e à observação no MetaBus:
   resumo tipado/digest/configuração, sem despejar histograma ilimitado na
   memória, sem promover confiança ou modificar expressão formal.

## Aceite e plano

- Criar testes R890 antes da correção e observar RED: perguntas distintas não
  são tratadas como respondidas; distribuição uniforme com um shot não tem
  ajuste perfeito; presença de Qiskit não libera 21/100 qubits; tipos/limites
  inválidos são recusados antes de executar; memória preserva proveniência
  e o ledger de confiança permanece inalterado.
- Atualizar `reasoning/quantum.py`, o motor em `reasoning/engines.py` e a
  observação em `mci/metacognitive_loop.py`; manter consumidores e testes
  afetados com expectativas honestas, sem reduzir casos negativos.
- Rodar testes novos e regressões dirigidas do raciocínio/primário.
- Publicar três levantamentos R890 e manifestos com origem, testes e limites;
  registrar ciclo somente após execução. Nenhum ganho de tokens, eficácia
  clínica, benefício educacional ou desempenho quântico é presumido.

A indexação integral R889 será retomada somente após congelar estas alterações
nos arquivos de produção, para não descartar candidatos por fontes mutáveis.
