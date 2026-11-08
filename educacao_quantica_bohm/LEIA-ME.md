# Do Bit ao Todo — 3000 laudas de física quântica

**Uma obra nanoescalável e bilíngue:** 100 conceitos × 10 lentes × 3 níveis =
**3000 laudas de uma página**, mais **100 fichas de evidência** com DOI/URL, compiladas em um **PDF A5 navegável** com design
editorial **pixel**. O português é a língua de explicação; o chinês
(mandarim) entra como **ponte sonora** no meio de cada lauda, com hanzi, pinyin,
tons e microfrases.

> **Design:** corpo do texto em **Atkinson Hyperlegible** (legível); menus,
> capítulos, títulos e subtítulos em **Press Start 2P** (pixel); hanzi em
> **Noto Serif CJK SC**. Fundo preto, sprites e capa gerados por código.

---

## O que está pronto

| Arquivo | O que é |
|---|---|
| `livro_pixel/LIVRO_3000_LAUDAS.pdf` | **3550 páginas**: 3000 laudas + 400 notas de cálculo + 100 fichas + arquitetura de leitura, sumário navegável, história de Bohm, sobre o autor, manual do leitor, código dos 18 experimentos, trilhas por nível, verificação em Lean 4, pacote de publicação, mapas, glossário, anexo e fecho |
| `livro_pixel/LIVRO_3000_LAUDAS.html` | versão HTML para edição/inspeção |
| `livro_pixel/secoes/0001..3000_*.md` | **3000 arquivos separados**, um por lauda |
| `livro_pixel/MAPA.md` | mapa dos 100 conceitos com links e páginas |
| `livro_pixel/ARQUITETURA_LEITURA.md` | contrato de leitura, sete movimentos, fio condutor e mapa de dependências |
| `livro_pixel/SUMARIO.md` | sumário navegável com números de página gerados pelo PDF |
| `livro_pixel/HISTORIA_BOHM.md` | a tese secreta, a USP e a filosofia da totalidade |
| `livro_pixel/LABORATORIO_LEITOR.md` | instalação, API key, código 01–07, CSV, circuitos e galeria de figuras |
| `livro_pixel/CODIGO_EXPERIMENTOS.md` | script completo dos 18 experimentos, da instalação ao resultado |
| `livro_pixel/TRILHAS_NIVEIS.md` | trilhas do fundamental ao PhD, com experimentos, checkpoints e critérios |
| `livro_pixel/TRILHAS_FERRAMENTAS.md` | instalar, acessar GJQ, executar, interpretar e auditar |
| `livro_pixel/LEAN_QUANTUM.md` | apêndice de verificação formal em Lean 4 |
| `../livro-core/lean/QuantumTrails.lean` | teoremas de H, X, Z, CNOT e CHSH verificados no Lean 4 |
| `laboratorio_leitor/08_experimentos_18.py` | versão standalone dos 18 experimentos, com CLI, JSON e CSV |
| `livro_pixel/GLOSSARIO_CHINES.md` | 100 termos em hanzi, pinyin, tons e leitura de apoio |
| `scripts/gerar_figuras_niveis.py` | 6 ilustrações da escada N0 → PhD |
| `livro_pixel/INDICE_3000.csv` | índice lauda → nível → parte → conceito → arquivo |
| `livro_pixel/FICHAS.md` | índice das 100 fichas de evidência |
| `livro_pixel/fichas/F001..F100_*.md` | **100 fichas** com fonte, DOI, prática e grau de evidência |
| `livro_pixel/niveis/` | divisores dos níveis N0, N1 e N2 |
| `livro_pixel/base/` | base curada de 100 conceitos |
| `scripts/gerar_ilustracoes.py` | circuitos PennyLane/Cirq/Qiskit, Bloch, probabilidades, emaranhamento, onda piloto, holograma, diálogo |
| `scripts/gerar_resultados_reais.py` | figuras do GHZ, VQC, CHSH e dois backends a partir dos JSONs |
| `scripts/executar_nuvem.py` | GHZ, QASM, VQC e CHSH no backend, com task IDs e JSON |
| `scripts/experimentos_100.py` | 18 circuitos-base para os 100 conceitos, simulado + backend |
| `dados_experimentos/` | um JSON por experimento e o relatório dos 100 conceitos |
| `dados_experimentos/RELATORIO_EXPERIMENTOS.md` | tabela com 18 circuitos e 100 conceitos |
| `ANEXO_QUALIS_A1.md` | parecer crítico do estudo de VQC com ruído benéfico |
| `PRATICA_SWAP_TEST.md` | prática Tiangong: SWAP test com QASM e resultado real |
| `OFICINA_SCRIPTS.md` | 18 experimentos com código, linha a linha, cálculo e resultado |
| `CAPITULO_CEARA_PARAIBA_GJQ.md` | Ceará, Paraíba, CIQuanta e por que GJQ |
| `GABARITO.md` | 100 checkpoints com resposta esperada, critério e resultado |
| `TRILHA_LEIGO.md` | trilha de 30 dias, 30 práticas |
| `livro_pixel/sprites_conceitos/` | 100 ícones de conceito (hanzi) |
| `BLOCH_SUITE.md` | 6 circuitos de Bloch, simulação × hardware |
| `dados_hardware/calibracao_basica.csv` | calibração fornecida pelo operador |
| `dados_hardware/swap_test_guoji08.json` | P(0), sobreposição e task ID do SWAP test |
| `scripts/analise_vqc_ruido.py` | réplica com DensityMatrix e canais de Kraus |
| `scripts/validar_vqc_rapido.py` | validação 2/4 qubits, 5 folds, IC95% |
| `dados_qualis/` | JSONs e relatórios da validação |
| `dados_referencias/` | DOIs verificados via Crossref/DataCite |
| `scripts/pratica_swap_test.py` | simula e executa o SWAP test no Guoji08 |
| `scripts/gerar_figura_calibracao.py` | figura dos parâmetros de calibração |
| `scripts/gerar_figura_swap_test.py` | figura P(0)/sobreposição do SWAP test |
| `scripts/bloch_suite.py` | suíte de Bloch (6 estados × 3 bases) |
| `scripts/gerar_figura_bloch_suite.py` | figura 3D da suíte de Bloch |
| `scripts/gerar_fichas.py` | gera as 100 fichas |
| `scripts/verificar_dois.py` | verifica DOIs e grava o relatório |
| `scripts/gerar_qasm.py` | circuitos OpenQASM 2.0 para o editor da Tiangong |
| `livro_pixel/scripts/pixel_art.py` | capa, sprites e banners pixel |
| `dados_hardware/ghz4_guoji08.json` | contagens reais do GHZ de 4 qubits |
| `dados_hardware/vqc_xor_guoji08.json` | resultado do VQC XOR |
| `dados_hardware/chsh_guoji08.json` | correladores e S do CHSH |
| `dados_hardware/ghz4_qasm_guoji08.json` | GHZ carregado de QASM 2.0 |
| `circuitos_qasm/` | `bell.qasm`, `ghz4.qasm`, CHSH e VQC para colar no editor |
| `notebooks/AULA_BOHM_LABORATORIO.ipynb` | laboratório guiado |
| `livro/LIVRO_BOHM_BLACK.pdf` | edição compacta anterior (54 páginas) |
| `SPEC-BOHM-PIXEL-001.md` | especificação formal |
| `tests/test_pixel_book.py` | verificação automatizada |

---

## Como compilar

```bash
# 0. Gerar os QASM para o editor da Tiangong
.venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_qasm.py

# 0b. Simular os 18 experimentos dos 100 conceitos
.venv-quantum/bin/python educacao_quantica_bohm/scripts/experimentos_100.py --sim

# 1. Gerar as 3000 laudas (100 conceitos × 10 lentes × 3 níveis)
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/gerar_secoes.py

# 2. Compilar o PDF navegável (~3 min)
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/build_pixel_fast.py

# 3. Gerar as figuras científicas e as ilustrações dos níveis
.venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_ilustracoes.py
.venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_resultados_reais.py
.venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_figuras_niveis.py

# 4. Gerar a arte pixel (capa/sprites)
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/scripts/pixel_art.py

# 5. Verificar
.venv-quantum/bin/python -m pytest educacao_quantica_bohm/tests/test_pixel_book.py -v

# 6. Opcional: executar no backend (exige GJQ_API_KEY)
export GJQ_API_KEY="sua-chave"
.venv-quantum/bin/python educacao_quantica_bohm/scripts/experimentos_100.py --real --backend Guoji08
.venv-quantum/bin/python educacao_quantica_bohm/scripts/experimentos_100.py --report
.venv-quantum/bin/python educacao_quantica_bohm/scripts/executar_nuvem.py --backend Guoji08
```

> **Por que `build_pixel_fast.py`?** O `build_pixel.py` antigo usava Pandoc para
> parsear milhares de fenced divs e travava. O build rápido monta o HTML diretamente
> (as laudas já são HTML) e usa Pandoc apenas na abertura, no mapa e nas partes.

---

## Estrutura pedagógica

Cada lauda tem:

0. **nível** (N0 leigo/fundamental, N1 médio/graduação, N2 pós/PhD);
1. **cabeçalho pixel bilíngue** (código, lente, conceito, hanzi);
2. **corpo didático** em fonte legível;
3. **PONTE SONORA** no meio do corpo: hanzi, pinyin, tons, leitura de
   apoio e microfrase;
4. **caixa de RIGOR CIENTÍFICO** com definição precisa e nota
   **PARA O PROFESSOR**;
5. **CHECKPOINT**;
6. **barra de progresso** com as 10 lentes.

As 10 lentes:

`ideia em 60s` · `analogia + limite` · `mão na massa` · `laboratório` ·
`erro comum` · `para ir além` · `roda de diálogo` · `ética e sociedade` ·
`conexão com a vida` · `checkpoint`.

### Trilhas

- **N0 · 21 min:** ideia + analogia + vida de um conceito, sem matemática.
- **N1 · 70 min:** as 10 laudas de um conceito, com circuito e tabela.
- **N2 · 100 min:** as 10 laudas + replicação com outra seed/backend.
- **7 min:** 1 lauda.
- **50 min:** 5 laudas de um conceito.
- **100 min:** 10 laudas + roda de diálogo.
- **7 dias:** 1 conceito por dia.
- **Pesquisa:** 10 laudas + replicação com outra seed/backend.

---

## Resultados do backend (Guoji08, 1024 tiros)

### GHZ de 4 qubits

| Resultado | Ideal | Guoji08 |
|---|---:|---:|
| `0000` | 512 | 418 |
| `1111` | 512 | 389 |
| outros | 0 | 217 |
| fidelidade proxy | 100% | **78,8%** |

> **Rótulo do console:** o console da Tiangong exibe `Guoji No.8 (simulate)`.
> O identificador da API é `Guoji08`. Em 7 nov. 2026, a verificação
> `configuration().simulator` retornou **`False`**, indicando hardware; o rótulo
> `(simulate)` é modo de execução. Evidência:
> `dados_hardware/verificacao_guoji08.json`. O livro mantém “resultados do
> backend” porque hardware não é sinônimo de resultado perfeito.

### VQC XOR de 2 qubits

| Entrada | Rótulo | Ideal P(1) | Backend P(1) | Acertou? |
|---|---|---:|---:|---|
| 00 | 0 | 0,000 | 0,041 | sim |
| 01 | 1 | 1,000 | 0,967 | sim |
| 10 | 1 | 1,000 | 0,952 | sim |
| 11 | 0 | 0,000 | 0,043 | sim |

**Leitura honesta:** 4/4 acertos em quatro pontos **não** são generalização. O
teste foi pequeno e o teto era 100%. Phase damping não muda a população Z;
depolarização reduz a margem. A hipótese de “ruído benéfico” do repositório
`Beneficial-Quantum-Noise-in-Variational-Quantum-Classifiers` **não foi testada**
— ela exigiria dataset maior, split treino/teste, múltiplas seeds e treino sob
ruído.

### CHSH

| Configuração | E ideal | E no Guoji08 |
|---|---:|---:|
| E00 | +0,707 | +0,574 |
| E01 | +0,707 | +0,576 |
| E10 | +0,707 | +0,566 |
| E11 | −0,707 | −0,666 |

`S = E00 + E01 + E10 − E11 = 2,383`. O limite clássico é 2; o ideal quântico é
2√2 ≈ 2,828. O backend viola o limite clássico, mas não alcança o ideal. Com
1024 tiros por circuito, o erro de S é da ordem de 0,06.

### Dois backends, o mesmo GHZ

| Resultado | Guoji08 (20 q) | Baihua (156 q) |
|---|---:|---:|
| `0000` | 418 | 437 |
| `1111` | 389 | 230 |
| outros | 217 | 357 |
| fidelidade proxy | **78,8%** | **65,1%** |

Mais qubits não significa menos ruído: o Baihua tem 156 qubits e fidelidade
proxy menor neste circuito.

---

## Anexo Qualis A1: VQC e ruído benéfico

O anexo `ANEXO_QUALIS_A1.md` analisa o relatório de otimização bayesiana de VQCs
com ruído benéfico. A conclusão é dura e honesta:

- **cinco trials e um split 50/20** não sustentam “confirmação” nem
  “superioridade estatística”;
- **phase damping preserva populações Z**; se o classificador lê P(1), o forward
  pass não muda, então o ganho não pode vir desse canal no observable medido;
- a réplica rápida com **2 e 4 qubits e 5 folds** não reproduziu o baseline de
  85–88,5% (ficou em 58,6% e 34,3%), e o IC95% é largo;
- o efeito, se existir, exige mais trials, múltiplos datasets, código original e
  validação em hardware.

> **O anexo não “refuta” o ruído benéfico; ele mostra o que ainda falta para
> que a afirmação seja publicável em padrão A1.**

## Cem conceitos, dezoito circuitos

Cada um dos 100 conceitos aponta para um dos 18 circuitos-base em
`livro_pixel/base/base_experimentos.py`. O script `experimentos_100.py` roda a
simulação (statevector + amostragem) e o backend, grava um JSON por experimento
e gera `dados_experimentos/RELATORIO_EXPERIMENTOS.md` com os 100 conceitos.

A métrica universal é a **sobreposição de distribuições**:
`sum_b min(p_sim[b], p_real[b])`. Ela mede semelhança entre counts; não é
fidelidade de estado nem prova de emaranhamento. O livro mostra a leitura
específica de cada circuito (P(0), S, acurácia etc.) ao lado da sobreposição.

## Nuvem quântica

### CIQuanta

Centro Internacional de Computação e Tecnologias Quânticas do Estado da Paraíba,
em João Pessoa. O portal informa dois computadores (20 + 100 qubits), laboratórios
e uma réplica para visitas; a plataforma em nuvem é
`cloudciquanta.secties.pb.gov.br`. Disponibilidade e cadastro podem mudar.

### Tiangong / CETC-ICQ

Plataforma com simuladores e backends supercondutores. O console de circuitos,
consultado em novembro de 2026, listava 15 opções. A selecionada era
`Guoji No.8 (simulate)` (20 qubits); o identificador da API é `Guoji08`.

| Backend no console | Qubits |
|---|---:|
| Baihua | 156 |
| **Guoji No.8 (simulate)** | **20** |
| Qilv-Full Amplitude Simulator | 29 |
| Qilian-Noise Simulator | 29 |
| Qiyao-Single Amplitude Simulator | 29 |
| Qijing-Partial Amplitude Simulator | 29 |
| MPS Simulator | 997 |
| Jiuxiao-Full Amplitude Simulator | 20 |
| Jiuyun-Noise Simulator | 20 |
| Jiuyuan-Single Amplitude Simulator | 200 |
| Jiuci-Partial Amplitude Simulator | 20 |
| Liangshi-Full Amplitude Simulator | 10 |
| Weina-Noise Simulator | 10 |
| Weichi-Single Amplitude Simulator | 10 |
| Weixin-Partial Amplitude Simulator | 10 |

Editor QASM: <https://tiangongqs.com/cloud/circuit>. Jupyter:
`tiangongqs.com/cloud/jupyter`. A pasta `circuitos_qasm/` traz os arquivos
prontos para colar no editor.

### QASM 2.0 do GHZ

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
cx q[0], q[1];
cx q[0], q[2];
cx q[0], q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
```

Os arquivos `bell.qasm`, `ghz4.qasm`, `chsh_e00.qasm` a `chsh_e11.qasm` e
`vqc_xor_00.qasm` a `vqc_xor_11.qasm` estão em `circuitos_qasm/`. Gere de novo
com `scripts/gerar_qasm.py`.

### `gjq-client`

```python
import os
from qiskit import QuantumCircuit
from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

service = GJQRuntimeService(api_key=os.environ["GJQ_API_KEY"])
backend = service.backend("Guoji08")
qc = QuantumCircuit(4, 4)
qc.h(0)
for alvo in (1, 2, 3):
    qc.cx(0, alvo)
qc.measure_all()
isa = generate_preset_pass_manager(backend=backend, optimization_level=2).run(qc)
print(Sampler(backend=backend).run(isa, shots=1024).result(timeout=600)["counts"])
```

O script consolidado executa GHZ, QASM, VQC e CHSH, registra task IDs e grava
JSON em `dados_hardware/`:

```bash
export GJQ_API_KEY="sua-chave"   # nunca grave no projeto
.venv-quantum/bin/python educacao_quantica_bohm/scripts/executar_nuvem.py --backend Guoji08
.venv-quantum/bin/python educacao_quantica_bohm/scripts/executar_nuvem.py --backend Baihua --only ghz
.venv-quantum/bin/python educacao_quantica_bohm/scripts/executar_nuvem.py --dry-run
```

### Servidor MCP `gjq-runtime-mcp-server`

Envolve o `gjq-client` e expõe `list_backends_tool`, `sample_tool`,
`estimate_tool`, `get_task_status_tool`, `get_task_result_tool`, entre outras.
Aceita OpenQASM 2.0 e recursos `circuits://bell-state` e `circuits://ghz-state`.
Instalação: clone, `python -m venv .venv`, `pip install -e .`, `.env` com
`GJQ_API_KEY`, `python -m gjq_runtime_mcp_server`.

---

## Segurança

- A API key usada nos testes **não está** no livro, no notebook, nos JSONs ou no
  HTML. Ela foi passada apenas por variável de ambiente durante a execução.
- O `gjq-client` grava o cache em `~/.gjq_client/gjq_client_account.json`
  (Linux/macOS) ou `%USERPROFILE%\.gjq_client\gjq_client_account.json`
  (Windows). O arquivo contém a `api_key`; use `chmod 600` e trate como senha.
- O servidor MCP usa `.env`/config local; os dois arquivos são segredos.
- **Rotacione a chave** se ela foi compartilhada em chat, print, issue ou
  repositório. Revogue, apague o cache, audite `list_tasks()` e registre o
  incidente.
- Não faça commit de `.env`, cache ou configuração com chave.
- Referência oficial: Tiangong, *Quantum Programming Framework User Guide*,
  seção “API Key and account cache”:
  <https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html#_2-2-api-key-and-account-cache>.

---

## Limites e anti-overclaim

- **3000 laudas** são 100 conceitos × 10 lentes × 3 níveis, geradas a partir de
  uma base curada; não são 3000 ensaios independentes. N0, N1 e N2 mudam a voz,
  a matemática e a evidência, não o conceito.
- **Bohm** é uma interpretação não local, não consenso; a ordem implicada é
  filosófica; o holograma é analogia.
- **Backends** têm ruído, calibração e deriva; os resultados são de uma execução.
  O backend Guoji08 se declara hardware (`simulator=False`); o console exibe
  `(simulate)` como modo. Ainda assim, calibração, fila e leitura importam.
- **VQC 4/4** não é generalização; o teste é uma demonstração de pipeline.
- **Ruído benéfico** é hipótese empírica do repositório citado, não resultado
  deste material.
- **CIQuanta/Tiangong** podem mudar acesso, fila, preço e disponibilidade. O
  editor de circuitos exige login; o QASM é compatível, mas a execução não é
  instantânea nem idêntica entre calibrações.
- **Bilíngue não é tradução integral.** O chinês entra como ponte sonora: 100
  termos, 10 padrões de frase, pinyin aproximado e hanzi simplificado. Não há
  áudio no PDF; para fluência, é preciso um curso e um dicionário com áudio.
- **Impressão:** o design preto é para tela/projetor; para impressão em massa,
  use a edição clara ou imprima apenas as laudas selecionadas.

---

## Adaptação da capa

A capa usa `educacao_quantica/livro/figuras/CAPA/CAPA.png` como fundo em tela
cheia. O retrato pixelado da página de rosto deriva de
`educacao_quantica/livro/figuras/CAPA/1.svg`. Os sprites e banners são
decorativos e gerados por `pixel_art.py`; as **figuras científicas** vêm dos
scripts quânticos.

---

## Verificação

```bash
.venv-quantum/bin/python -m pytest educacao_quantica_bohm/tests/test_pixel_book.py -v
```

O teste verifica:

- 3000 seções e 100 conceitos; 100 fichas de evidência;
- cada seção com RIGOR, CHECKPOINT e PONTE SONORA;
- PDF ≥3000 páginas, A5, 3000 rodapés de lauda e 100 de ficha;
- marcadores PDF para partes e laudas;
- mapa com 100 links e glossário chinês com 100 termos;
- JSONs reais coerentes;
- scripts de figuras, QASM e execução no backend presentes;
- fontes Atkinson/Press Start no CSS;
- ausência da chave literal e de placeholders;
- QASM 2.0 válido para Bell, GHZ, CHSH e VQC;
- 18 experimentos com simulado e backend, e 100 conceitos cobertos;
- cada lauda de prática com caixa `RESULTADO · SIMULADO × BACKEND`;
- relatório com 100 linhas e sobreposição por conceito.

---

## Licença e créditos

O livro é distribuído sob **CC BY-NC-SA 4.0**; o código dos experimentos, sob
**MIT**. O texto legal está em `livro_pixel/LICENCA.md` e em
<https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.pt>. Fontes
Atkinson Hyperlegible, Press Start 2P, VT323 e Noto Serif CJK SC sob SIL Open
Font License 1.1; DejaVu Sans sob Bitstream Vera. Qiskit, PennyLane, Cirq e
`gjq-client` sob Apache 2.0; NumPy e SciPy sob BSD; Matplotlib sob PSF; Optuna
sob MIT. CIQuanta e Tiangong pertencem aos seus respectivos operadores. Bohm é
apresentado como uma interpretação entre várias.