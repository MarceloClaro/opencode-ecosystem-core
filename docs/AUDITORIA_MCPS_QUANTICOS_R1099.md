# Auditoria de MCPs quânticos — R1099

**Data:** 2026-11-08
**Escopo:** `Lokesh-2025/quantum-hardware-mcp`, `YuChenSSR/quantum-simulator-mcp`, `YuChenSSR/symbolica-mcp`
**Método:** clone raso; leitura estática do código; consulta ao registro do Docker Hub; download e listagem das camadas pequenas das imagens; nenhuma imagem foi executada e nenhum job quântico foi submetido.

## Veredito

| MCP | Fonte disponível | Licença | Decisão |
|---|---|---|---|
| `quantum-hardware-mcp` | Sim, no repositório | MIT | **Auditado; não registrado automaticamente** — exige instalação manual, tokens e controle de custo por job |
| `quantum-simulator-mcp` | Somente dentro da imagem Docker | MIT | **Não registrado** — Docker ausente, Qiskit antigo e sem limites; substituído pelo `quantum-sim-core` |
| `symbolica-mcp` / `computing-mcp` | Somente dentro da imagem Docker | MIT | **BLOQUEADO** — executa código arbitrário com `exec` e ignora o `timeout` |
| `quantum-sim-core` (nativo) | Sim, no Core | MIT | **Registrado e habilitado** — Qiskit 2.x, limites e `confirm=True` |

## 1. `Lokesh-2025/quantum-hardware-mcp`

| Item | Valor |
|---|---|
| Commit auditado | `5ac7d0c0d294feb76f1a3142345b331304dcc2cf` |
| Licença | MIT |
| `server.py` | 276.184 bytes; SHA-256 `0fb7d007ca76a9187687c447a9875b46629ce2b86e474ae59297d5414b39ce6d` |
| `tools_chemistry.py` | 30.671 bytes; SHA-256 `c13b899f01a13a9ebdadb20aed066eb11029da6130edbf8d65487c1d678e4648` |
| `requirements.txt` | SHA-256 `a604850bda8e5beb9e8fc968bad4345c7bd1b31c2901e8ef202067a405d6a4a6` |
| Ferramentas | 52 |
| Testes no repositório | 127 |
| Backends | IBM Quantum, IonQ e AWS Braket |

**Achados estáticos:**

- Não foram encontrados `subprocess`, `os.system`, `eval(`, `exec(` ou `shell=True`.
- O servidor lê `IBM_QUANTUM_TOKEN`, `IONQ_API_KEY`, credenciais AWS e, opcionalmente, `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` de um `.env` ao lado do código.
- Há chamadas HTTP a IBM, IonQ e Turso; os endpoints observados são os dos provedores e do banco configurado.
- O banco SQLite é local ao diretório do servidor.
- Ferramentas de execução aceitam `simulate_only=True` em parte dos fluxos, mas `submit_job`, `ionq_submit_job` e equivalentes podem consumir créditos reais.
- Não há filtro de ferramentas por perfil: quem habilita o MCP expõe as 52 ferramentas.

**Risco:** custo financeiro e uso de credenciais. O código é auditável, mas a habilitação automática contraria o princípio de menor privilégio.

**Decisão:** não registrar em `opencode.json`. Para uso manual, instalar em ambiente isolado, definir tokens apenas no ambiente, manter `simulate_only=True` por padrão e exigir aprovação humana antes de qualquer submissão. O comando sugerido é:

```bash
cd /caminho/quantum-hardware-mcp
python -m venv .venv
.venv/bin/pip install -r requirements.txt
IBM_QUANTUM_TOKEN=... .venv/bin/python server.py --transport stdio
```

## 2. `YuChenSSR/quantum-simulator-mcp`

| Item | Valor |
|---|---|
| Commit auditado | `9dcb2ad377ef785bf7a981d57c7a15b7414306cc` |
| Licença | MIT |
| Repositório | Apenas `README.md` e `LICENSE`; o código está na imagem Docker |
| Imagem | `ychen94/quantum-simulator-mcp:latest` |
| Digest da tag | `sha256:7b72d9d3b93ac0b207fb72bd7e9f1eea16549b9f327a48f907434e8698efb52f` |
| Manifest amd64 | `sha256:8402050072a5f37e89077d85dd1b3c278ec3e60f89120670e9fbe9b5ccba3b24` |
| Tamanho amd64 | 238.370.860 bytes |
| Fonte extraída | `quantum_simulator.py`, 18.594 bytes |
| SHA-256 da fonte | `a72556108e7c69fb57eca316d42661ca90364b5dcd7fe8cafd5c3dd45a5dc11d` |

**Achados estáticos:**

- Não foram encontrados `subprocess`, `os.system`, `eval(`, `exec(` ou acesso a rede.
- Usa `QuantumCircuit.from_qasm_str` e Qiskit Aer para `counts`, `statevector`, `unitary`, `amplitudes`, `probabilities` e histogramas.
- Grava PNGs em `/data/quantum_simulator_results`, normalmente montado em `/tmp` do host.
- Usa `qiskit.execute`, removido no Qiskit 1.0; a imagem está congelada em Qiskit antigo.
- Não impõe limite de qubits, shots ou tamanho do QASM; um circuito grande pode consumir memória e tempo.
- O `timeout` não é aplicado pelo servidor.

**Risco:** dependência de imagem de terceiro, API obsoleta, ausência de limites e superfície de escrita no host. O Docker não está instalado neste ambiente, então a imagem não pôde ser testada.

**Decisão:** não registrar. Em vez de executar a imagem, o Core passou a oferecer o `quantum-sim-core`, com código local, Qiskit 2.x e limites explícitos.

## 3. `YuChenSSR/symbolica-mcp` (`ychen94/computing-mcp`)

| Item | Valor |
|---|---|
| Commit auditado | `3a4c39358821fae25602db069d32acc4f294c2c6` |
| Licença | MIT |
| Repositório | Apenas `README.md` e `LICENSE`; o código está na imagem Docker |
| Imagem | `ychen94/computing-mcp:latest` |
| Digest da tag | `sha256:04359a9141d7d80daefeed7adc31dd3b28052f208b76a9851af65d4a15f0d16d` |
| Manifest amd64 | `sha256:fb29abf4862ebd7b59099938fed53c334d164d74d46f55d635cc595e75858b58` |
| Tamanho amd64 | 384.229.322 bytes |
| Fonte extraída | `server.py`, 12.346 bytes |
| SHA-256 da fonte | `815f2ad366f9f90eb53135118f602da04f9b9244de93b1dade8de66a88e78954` |

**Achados estáticos:**

- A ferramenta `execute_python` monta um bloco com bibliotecas científicas e chama `exec(full_code, globals_dict)` sobre o código fornecido pelo usuário.
- O parâmetro `timeout` é aceito na assinatura, mas **não é usado** para interromper a execução.
- O container monta `/tmp` do host em `/app/shared` e grava figuras nesse diretório.
- Não há sandbox de processo, limite de memória, bloqueio de rede ou validação de imports.
- Qualquer código Python compatível com o ambiente pode ler variáveis de ambiente, abrir sockets, apagar arquivos montados e consumir CPU indefinidamente.

**Risco:** execução arbitrária de código com persistência no host e sem timeout efetivo. A licença MIT permite auditar e reutilizar, mas não torna a execução segura.

**Decisão:** **BLOQUEADO**. Não registrar, não executar e não montar `/tmp` do host nesse container. Para cálculo simbólico, preferir uma ferramenta local com allowlist de operações ou um sandbox com timeout, rede desabilitada e filesystem efêmero.

## 4. Substituto nativo: `quantum-sim-core`

| Item | Valor |
|---|---|
| Arquivo | `integrations/quantum_simulator_mcp.py` |
| Licença | MIT (código do Core) |
| Runtime | `.venv-quantum/bin/python` |
| Qiskit | 2.3.0 |
| Qiskit Aer | 0.18.2 |
| Limites | 12 qubits, 10.000 shots, 50.000 caracteres de QASM |
| Ferramentas | `sim_status`, `sim_noise_models`, `sim_run_qasm`, `sim_audit_counts` |
| Gate | `sim_run_qasm` exige `confirm=True` |
| Efeitos | sem rede, sem escrita de arquivos e sem leitura de segredos |

**Semântica:** recebe OpenQASM 2.0, transpila para o simulador Aer, aplica `none`, `depolarizing`, `thermal_relaxation` ou `readout_error`, devolve counts, probabilidades, erro padrão e metadados. A auditoria confere a soma dos counts contra os shots.

**Limite:** simulação local não prova fidelidade de hardware, emaranhamento ou vantagem quântica.

## 5. Gates e riscos residuais

- **Licença não é segurança:** os três projetos são MIT, mas um deles executa código arbitrário.
- **Fonte fora do repositório:** duas imagens só puderam ser auditadas por extração de camadas; a cadeia de build não foi reproduzida.
- **Docker ausente:** nenhuma imagem foi executada; o teste do `quantum-sim-core` foi feito no `.venv-quantum`.
- **Credenciais:** o MCP de hardware lê tokens de um `.env` local; nunca versionar esse arquivo.
- **Custo:** ferramentas de submissão podem consumir créditos; a habilitação deve ser manual e por job.
- **Atualização:** hashes e digests valem para a data desta auditoria.

## 6. Reprodução

```bash
# 1. Clonar sem executar
git clone --depth 1 https://github.com/Lokesh-2025/quantum-hardware-mcp.git
git clone --depth 1 https://github.com/YuChenSSR/quantum-simulator-mcp.git
git clone --depth 1 https://github.com/YuChenSSR/symbolica-mcp.git

# 2. Conferir os commits
git -C quantum-hardware-mcp rev-parse HEAD
git -C quantum-simulator-mcp rev-parse HEAD
git -C symbolica-mcp rev-parse HEAD

# 3. Testar o substituto nativo
.venv-quantum/bin/python -m pytest tests/test_r1099_quantum_simulator_mcp.py -q
```

Não há chave, token ou credencial neste documento.
