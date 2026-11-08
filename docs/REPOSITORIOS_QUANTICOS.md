# Repositórios quânticos — catálogo de curadoria (R1099)

**Data da verificação:** 2026-11-08
**Escopo:** GitHub, Gitee, GitCode, AtomGit e Coding (coding.net)
**Método:** consulta HTTP direta às páginas e às APIs públicas; leitura do arquivo `LICENSE` na raiz quando disponível; nenhum repositório foi clonado, instalado ou executado.
**Limite:** estrelas, versões e licenças mudam. A licença verificada na raiz não cobre automaticamente submódulos, `third_party/` ou assets. “Sem licença” significa copyright padrão: não copiar.

## Legenda de decisão

| Decisão | Significado |
|---|---|
| **Referência** | Consulta conceitual e bibliográfica; não copiar código. |
| **Adaptar** | Reuso compatível com a licença, com atribuição e aviso preservado. |
| **Integrar** | Proposta de registro/uso no ecossistema, sujeita a revisão de licença, segurança e aprovação. |
| **Não integrar** | Licença ausente/incompatível, escopo fora do livro ou risco não mitigado. |

## 1. MindSpore e MindQuantum (fontes indicadas pelo usuário)

| Item | Verificação |
|---|---|
| Site oficial | <https://www.mindspore.cn/en> — página ativa; MindSpore 2.11 anunciado; “MindSpore Quantum” listado em *Scientific Computing*. |
| Documentação | <https://www.mindspore.cn/mindquantum/docs/en/stable/index.html> |
| Gitee | <https://gitee.com/mindspore/mindquantum> — Apache-2.0; 3.125 estrelas; 4.315 forks; atualização 2026-10-12; release v0.11.0; a página indica migração oficial para o AtomGit e mantém o snapshot legível. |
| AtomGit (canônico após migração) | <https://atomgit.com/mindspore/mindquantum> — HTTP 200; Apache-2.0. |
| Espelho GitHub | <https://github.com/mindspore-ai/mindquantum> — `VERSION.txt` em 0.12.0; Apache-2.0. |
| Framework-base | <https://atomgit.com/mindspore/mindspore> — Apache-2.0. |
| Artigo de citação | arXiv:2406.17248 — *MindSpore Quantum: A User-Friendly, High-Performance, and AI-Compatible Quantum Computing Framework*. |

**Função:** framework de computação quântica para algoritmos NISQ, simulador HiQ, circuitos parametrizados, redes neurais quânticas, ruído, química quântica e otimização.

**Relevância para o livro:** trilha de VQC/XOR (E10), ruído de fase (E14), leitura de counts no simulador e comparação com Qiskit. Serve como segunda implementação independente para o leitor que não usa Qiskit.

**Decisão:** **Referência + Adaptar**. Reutilizar tutoriais e exemplos com atribuição Apache-2.0 e aviso preservado; não copiar código para o corpo do livro sem a nota de licença. A versão do Gitee (0.11.0) está atrás do espelho GitHub (0.12.0); citar a versão efetivamente usada.

**Risco:** o Gitee é snapshot migrado; o endereço canônico passou ao AtomGit. Não tratar a estrela ou a versão como prova de qualidade científica.

## 2. GitHub

### 2.1 Bibliotecas, cursos e livros

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://github.com/Qiskit/textbook> | Apache-2.0 | Textbook Qiskit; circuitos, algoritmos e exercícios | **Referência + Adaptar** com atribuição |
| <https://github.com/PennyLaneAI/pennylane> | Apache-2.0 | Programação quântica diferenciável; autodiff | **Referência** |
| <https://github.com/ProjectQ-Framework/ProjectQ> | Apache-2.0 | Compilador e simulador quântico | **Referência** |
| <https://github.com/softwareQinc/qpp> | MIT | Simulador C++ de alto desempenho | **Referência** |
| <https://github.com/tensorflow/quantum> | Apache-2.0 | TensorFlow Quantum; QML sobre TF | **Referência** |
| <https://github.com/microsoft/QuantumKatas> | MIT | Katas de aprendizado; Q#/Python/Jupyter | **Adaptar** exercícios com atribuição |
| <https://github.com/microsoft/Quantum-NC> | Licença Microsoft não comercial | Kit de computação quântica | **Referência restrita**; não integrar ao código MIT |
| <https://github.com/JackHidary/quantumcomputingbook> | Sem licença na raiz | Código do livro *Quantum Computing: An Applied Approach* | **Referência**; não copiar |
| <https://github.com/corbett/QuantumComputing> | GPL-3.0 | Curso/livro de computação quântica | **Referência**; copyleft impede incorporação ao MIT |
| <https://github.com/quantum-ods/qmlcourse> | CC BY 4.0 | Curso de QML em notebooks | **Adaptar** com atribuição |
| <https://github.com/gitkarma/quantum_computing_course2025> | Sem licença na raiz | Curso 2025 | **Referência**; não copiar |
| <https://github.com/desireevl/awesome-quantum-computing> | CC0-1.0 | Índice de recursos quânticos | **Referência** |

### 2.2 Verificação formal em Lean 4

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://github.com/Timeroot/Lean-QuantumInfo> | MIT | Informação quântica formalizada em Lean | **Referência** para o apêndice Lean; não importar prova sem compilar |
| <https://github.com/LionSR/QICLean> | Apache-2.0 | Informação quântica em Lean | **Referência** |
| <https://github.com/LionSR/TNLean> | Apache-2.0 | Redes tensoriais em Lean | **Referência** |

### 2.3 Bohm, onda piloto e sistemas abertos

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://github.com/wangleiphy/BohmianFlow> | MIT | Fluxo bohmiano e trajetórias | **Referência + Adaptar** para figuras com atribuição |
| <https://github.com/lsiemens/pilot_wave> | BSD-3-Clause | Simulação de onda piloto | **Referência + Adaptar** |
| <https://github.com/anssiZander/BohmianSternGerlach3D-public> | MIT | Stern-Gerlach bohmiano em 3D | **Referência** para ilustração |
| <https://github.com/cameron-cognitive/bohmian_density_matrix> | MIT | Relaxação de matriz densidade bohmiana | **Referência** |
| <https://github.com/jostylr/bohmian-mechanics> | Sem licença na raiz | Mecânica bohmiana interativa | **Referência**; não copiar |
| <https://github.com/cameron-cognitive/bohmian-mixed-state-relaxation> | Sem licença na raiz | Relaxação de estado misto | **Não integrar** até verificar licença |
| <https://github.com/xi-zhao/OpenQuantum> | MIT | Sistemas quânticos abertos | **Referência** |

### 2.4 MCPs quânticos

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://github.com/Lokesh-2025/quantum-hardware-mcp> | MIT | MCP para hardware quântico; 52 ferramentas e jobs pagos | **Auditado; não registrar automaticamente** — habilitação manual com controle de custo |
| <https://github.com/YuChenSSR/quantum-simulator-mcp> | MIT | MCP de simulador em imagem Docker; Qiskit antigo | **Não registrar** — substituído pelo `quantum-sim-core` nativo |
| <https://github.com/YuChenSSR/symbolica-mcp> | MIT | MCP de computação em imagem Docker; `exec` arbitrário | **BLOQUEADO** — ver auditoria R1099 |
| <https://github.com/barvhaim/qiskit-mcp-server> | Sem licença localizada | MCP Qiskit | **Não integrar** até licença explícita |
| <https://github.com/PhelanShao/orca-mcp-server> | Sem licença localizada | MCP química quântica (ORCA) | **Não integrar** |
| <https://github.com/qu3ai/qu3-app> | Sem licença localizada | Aplicação quântica | **Não integrar** |

### 2.5 GJQ / CETC-ICQ

| Fonte | Licença | Função | Decisão |
|---|---|---|---|
| <https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html> | Documentação oficial | SDK, backends, Sampler/Estimator, MPS, sessões e PQC | **Referência** |
| <https://github.com/guoji-quantum/gjq_client> | Apache-2.0 | SDK oficial `gjq-client==0.2.1` | **Instalar** a partir do PyPI |
| <https://github.com/MarceloClaro/gjq_client> | Apache-2.0 | Fork-espelho `0.2.1.post1` | **Referência**; não substitui o PyPI |
| <https://github.com/guoji-quantum/gjq-runtime-mcp-server> | Apache-2.0 | MCP oficial com 12 ferramentas | **Auditado; não registrar** — `obs=` incompatível e sem `confirm` |
| <https://github.com/MarceloClaro/gjq-runtime-mcp-server> | Apache-2.0 | Fork auditado em `89897458` | **Referência**; o Core usa `gjq-runtime` nativo |
| <https://github.com/guoji-quantum/industry_solution> | README apenas | Repositório institucional de casos | **Referência**; sem código executável |

## 3. Gitee

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://gitee.com/mindspore/mindquantum> | Apache-2.0 | MindQuantum; snapshot migrado ao AtomGit | **Referência + Adaptar** |
| <https://gitee.com/baidu/qcompute> | Apache-2.0 | QCompute SDK; simulador e linguagem híbrida | **Referência** |
| <https://gitee.com/OriginQ/Quantum-programming-textbook> | Sem licença | Textbook de programação quântica da OriginQ | **Referência**; não copiar |
| <https://gitee.com/whu_mmap_cliang/Course_QC> | Sem licença | Curso de computação quântica da Universidade de Wuhan | **Referência**; não copiar |
| <https://gitee.com/quictucas/quictopen> | GPL-3.0 | Plataforma QuICT | **Referência**; copyleft impede incorporação |

## 4. GitCode

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://gitcode.com/OriginQ/QPanda-2> | Apache-2.0 | QPanda 2; framework C++/Python da OriginQC | **Referência** |
| <https://gitcode.com/gh_mirrors/cu/cuda-quantum> | Apache-2.0 | CUDA Quantum; simulação em GPU | **Referência** |
| <https://gitcode.com/gh_mirrors/qu/QuantumKatas> | MIT | Espelho das QuantumKatas | **Referência**; preferir o original no GitHub |
| `https://gitcode.com/gh_mirrors/quantum/quantum` | — | Caminho testado retornou 404 | **Não usar**; canônico é <https://github.com/tensorflow/quantum> |

## 5. AtomGit

| Repositório | Licença | Função | Decisão |
|---|---|---|---|
| <https://atomgit.com/mindspore/mindquantum> | Apache-2.0 | Destino canônico do MindQuantum após a migração | **Referência + Adaptar** |
| <https://atomgit.com/mindspore/mindspore> | Apache-2.0 | Framework-base do MindQuantum | **Referência** |

## 6. Coding (coding.net)

**Resultado:** nenhum repositório quântico público verificável foi localizado.

**Evidências da sondagem:**

| Endereço | Resultado |
|---|---|
| <https://coding.net/> | HTTP 200; página do Tencent Cloud CODING DevOps |
| <https://coding.net/explore> | HTTP 404 |
| <https://coding.net/search?q=quantum> | HTTP 404 |
| <https://coding.net/api/explore/projects> | HTTP 404 |

**Interpretação:** o Coding atua hoje como plataforma de DevOps empresarial; não foi encontrado catálogo público de repositórios nem endpoint de busca aberto. Links diretos de projetos antigos podem existir, mas não há como verificá-los sem URL explícita. **Não incluir repositórios não verificados.**

## 7. Propostas de integração ao ecossistema

1. **`quantum-tools-coach`**: trilha MindQuantum acrescentada com `mindquantum==0.11.0`, VQC, ruído, simulador HiQ e citação arXiv:2406.17248; espelho GitHub em 0.12.0 e Gitee migrado ao AtomGit.
2. **MCPs quânticos**: a auditoria R1099 está em `docs/AUDITORIA_MCPS_QUANTICOS_R1099.md`. O `quantum-hardware-mcp` foi auditado e permanece para habilitação manual; `quantum-simulator-mcp` foi substituído pelo `quantum-sim-core` nativo; `symbolica-mcp` está BLOQUEADO por execução arbitrária de código. O `gjq-runtime` nativo foi registrado com `confirm=True` e gate de hardware; o servidor oficial GJQ não foi registrado por incompatibilidade de assinatura e ausência de confirmação. `qiskit-mcp-server`, `orca-mcp-server` e `qu3-app` continuam bloqueados por ausência de licença localizada.
3. **Figuras bohmianas**: usar `BohmianFlow` (MIT), `pilot_wave` (BSD-3-Clause), `BohmianSternGerlach3D-public` (MIT) e `bohmian_density_matrix` (MIT) como referência para gráficos, com atribuição e sem copiar assets de terceiros. Regras em `docs/FIGURAS_BOHMIANAS_R1099.md`.
4. **Lean 4**: manter `Lean-QuantumInfo`, `QICLean` e `TNLean` como referência bibliográfica; o apêndice do livro continua provado apenas pelo `livro-core/lean/QuantumTrails.lean` compilado. Limites em `docs/LEAN_REFERENCIAS_R1099.md`.
5. **Didática**: usar `Qiskit/textbook` (Apache-2.0) e `qmlcourse` (CC BY 4.0) para conferir sequência e exercícios, com atribuição explícita. Mapa em `docs/DIDATICA_QUANTICA_R1099.md`.
6. **GJQ**: instalar `gjq-client==0.2.1` no `.venv-quantum`, registrar o MCP `gjq-runtime` e manter o agente `gjq-quantum-research` e a skill `gjq-pesquisa-quantica`. Detalhes em `docs/GJQ_PESQUISA_QUANTICA_R1099.md`.

## 8. Riscos e limites

- **Licença na raiz não é auditoria completa:** submódulos, datasets e imagens podem ter termos próprios.
- **Sem licença = todos os direitos reservados:** não copiar, não adaptar e não redistribuir.
- **GPL-3.0 e licença não comercial:** não incorporar ao código MIT do livro; usar somente como referência conceitual.
- **Estrelas e versões não medem rigor:** a decisão do catálogo é editorial e de licença, não uma nota científica.
- **Execução limitada:** o simulador local e os testes de MCP foram executados; nenhum job real foi submetido à GJQ nesta sessão.
- **Gitee/GitCode podem espelhar repositórios desatualizados:** confirmar o endereço canônico e a versão antes de citar.

## 9. Próximos passos

1. Revisar este catálogo e autorizar quais itens entram em `opencode.json` como MCP.
2. Se autorizado, criar um agente/skill de curadoria de repositórios quânticos com gate de licença e proveniência.
3. Fixar versões e hashes dos repositórios efetivamente usados no livro.
4. Repetir a sondagem do Coding apenas se houver uma URL pública concreta a verificar.
