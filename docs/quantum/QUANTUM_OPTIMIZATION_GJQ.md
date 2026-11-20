# Harness de otimização QUBO/QAOA com GJQ/Tiangong

**Estado desta entrega:** implementação local e testes sem rede; nenhuma
dependência quântica foi instalada, conta autenticada ou tarefa enviada a uma
QPU. O token de API anteriormente exposto deve ser revogado/rotacionado e não
deve ser copiado para este repositório, linha de comando, prompt ou configuração.

## Escopo e escolhas

O módulo `integrations.quantum_optimization` implementa validação QUBO v1,
energia, hash SHA-256 canônico, baseline clássico exato (até 16 variáveis),
conversão Ising e uma representação intermediária QAOA. O servidor
`integrations.quantum_optimization_mcp` oferece três ferramentas locais e uma
ferramenta externa explicitamente marcada:

| Ferramenta MCP | Efeito |
|---|---|
| `quantum_catalog` | Catálogo estático; sem rede ou credenciais |
| `qubo_inspect` | Validação, Ising e baseline clássico; local |
| `qaoa_prepare` | IR e orçamento previsto; não executa o circuito |
| `qaoa_optimize_gjq` | Avaliações QAOA no GJQ; efeito externo com consentimento por chamada |

O caminho suportado para execução futura é Qiskit + `gjq-client` da Tiangong.
PennyLane aparece como integração opcional descrita pelo GJQ, mas não é
dependência do harness. A documentação consultada mostra diferença de versão:
algumas páginas citam `gjq-client` 0.2.0, enquanto README/changelog do
repositório indicam 0.2.2. A compatibilidade exata com versões atuais de Qiskit
deve ser resolvida antes da instalação e de qualquer execução ao vivo.

Cirq não está conectado ao GJQ: não foi encontrado adaptador documentado no
material consultado; o Google Quantum Engine tem credenciais e disponibilidade
próprias, e a documentação consultada não o apresenta como serviço público
aberto. XQuad não é dependência: o repositório consultado declara
AGPL-3.0-or-later, API pré-1.0 e nenhum backend GJQ listado. Hugging Face
Transformers é classificado aqui como framework de ML/NLP clássico, não como
runtime quântico.

## Contrato QUBO v1

```json
{
  "schema_version": 1,
  "name": "exemplo",
  "num_variables": 2,
  "constant": 0.0,
  "linear": [-1.0, 0.5],
  "quadratic": [[0, 1, 2.0]]
}
```

O modelo minimiza `constant + Σ linear[i] x[i] + Σ quadratic[i,j] x[i]x[j]`,
com `x[i] ∈ {0,1}`. São aceitos 1–20 bits; todos os coeficientes devem ser
finitos e booleanos não são números válidos. Pares quadráticos são
canonicalizados para `i<j`; índices iguais, fora do domínio e pares
duplicados são rejeitados. Baseline exato é limitado a 16 bits; desempates
são determinísticos e lexicográficos.

A conversão usa `x=(1-Z)/2` e mantém o deslocamento constante. O IR QAOA
registra estado inicial Hadamard, separador de fase (`RZ`/`RZZ`), mixer `RX`
e medição. A busca de ângulos é uma busca coordenada determinística e limitada;
não demonstra ótimo global nem vantagem quântica.

## Execução local e transporte MCP

Com o ambiente Python do Core, a execução manual do servidor é:

```text
.venv/bin/python -m integrations.quantum_optimization_mcp
```

O transporte é stdio JSON-RPC e negocia MCP `2024-11-05` e `2025-06-18`;
respostas estruturadas e anotações de ferramenta só são emitidas quando a versão
negociada as suporta. As três ferramentas locais não importam Qiskit,
não leem `GJQ_API_KEY` e não acessam a rede. A configuração de exemplo abaixo
registra o servidor **desabilitado**; a compilação desta entrega não ativa o
MCP nem migra a configuração compartilhada:

```json
{
  "mcp": {
    "quantum-optimization": {
      "type": "local",
      "command": [".venv/bin/python", "-m", "integrations.quantum_optimization_mcp"],
      "enabled": false,
      "timeout": 30000
    }
  }
}
```

Para ativação futura, o operador deverá aprovar a alteração de `enabled`,
resolver e instalar dependências opcionais compatíveis a partir de fontes
primárias atuais e fazer smoke test somente das operações locais primeiro.
Nenhuma dessas ações foi feita nesta entrega.

## Gate para execução externa

`qaoa_optimize_gjq` requer em cada chamada `confirm_remote: true`, o nome exato
de backend, `max_evaluations` de 1–8, `shots` de 1–2048 e `max_total_shots`
explícito, suficiente e não superior a 16.384. A ferramenta ainda exige
`GJQ_API_KEY` no ambiente e verifica o tipo do backend retornado pelo provedor;
simuladores e tipos desconhecidos são recusados. A chave jamais é incluída na
resposta. A integração só carrega Qiskit/GJQ após os gates de consentimento e
credencial.

Esses limites restringem contagem de avaliações/jobs e shots, não custo em
dinheiro, quota, fila, disponibilidade ou saldo do usuário. A identificação de
hardware é baseada na metadata atual do provedor, não em certificação externa.
Falha depois de tentativa de submissão pode deixar estado remoto incerto; não
há retry automático e o painel do provedor deve ser verificado antes de uma
repetição. O servidor não deve ser usado com a credencial exposta na conversa:
primeiro revogue/rotacione-a; depois forneça a credencial nova ao processo
através de variável de ambiente protegida. Não a passe como argumento MCP.

## Fontes primárias consultadas

- [Documentação GJQ/Tiangong](https://tiangongqs.com/docs/en/index.html?theme=light)
- [Framework, backends, circuitos e jobs GJQ](https://tiangongqs.com/docs/en/framework/index.html)
- [Repositório e changelog `gjq_client`](https://github.com/guoji-quantum/gjq_client)
- [Qiskit](https://github.com/Qiskit/qiskit) e documentação `/qiskit/qiskit`
  via Context7
- [PennyLane](https://github.com/PennyLaneAI/pennylane) e documentação
  `/pennylaneai/pennylane` via Context7
- [Cirq](https://github.com/quantumlib/Cirq) e [Google Quantum Engine](https://quantumai.google/cirq/google/engine)
- [XQuad](https://github.com/QuipNetwork/xquad)
- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- [MCP specification — tools, 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP specification — lifecycle, 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)

As fontes sustentam o mapa documental, não a disponibilidade atual de backend,
compatibilidade instalada, execução no hardware, custo, optimalidade ou
vantagem quântica. A última análise documental desta spec é datada de 2026-11-20.
