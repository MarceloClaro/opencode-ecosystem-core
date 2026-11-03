# ITS-FINE: correções e preparação real — R924–R926

Este documento atualiza o estado histórico R923. Não foi iniciado treinamento,
baixado checkpoint/modelo do Hugging Face, lido dataset ou alterada a política
manual. As cópias upstream 0.0.15 continuam íntegras; os controles são código
original do Core, por composição.

## O que foi corrigido

| Pendência | Correção no Core |
|---|---|
| Instalação interativa | install-plan/install geram argv fixo com --yes, stdin fechado, engine opencode e confirmação obrigatória |
| Risco de latest/update | TGZ 0.0.15/SRI fixos, npm exec --offline, sem fallback ou update automático |
| Ausência de entrada própria | primary.itsfine_action, CLI marceloclaro itsfine e comando OpenCode /itsfine |
| Verificador e paths | verify do Core ancora componentes via dir_fd/O_NOFOLLOW, recusa traversal/symlinks/corridas e confere hashes |
| Processos antigos sem limite de pipe | Diagnósticos também usam runner bounded, com teto durante leitura, prazo e fechamento de grupo |
| Cleanup incerto | Falha de wait retorna cleanup_incomplete e não declara grupo encerrado; pipes fecham em finally |
| Relato de política | Política existente deve manter bytes; criação nova só aceita defaults negados e é declarada separadamente |
| Extrator YAML | Chaves duplicadas/merge keys são recusadas antes de corpo/permissão; não existe last-key-wins para licença |
| Lean | sorryAx recusado na fonte e no relatório; uma declaração por entrada; falha de thread/memória é operacional, não prova falsa |
| Histórico TDD após instalar dependências | Texto e voz gerenciados têm árvores SHA por caminho/fonte, com limites; nenhuma fonte é simplesmente ignorada |

A recusa de admissões Lean não é uma garantia universal sobre programas
arbitrários. Esta interface verifica uma declaração simples e expõe os axiomas
encontrados; aceita somente os fundamentos convencionais explicitamente listados
no verificador. Mantidos sandbox sem rede, 6 GiB virtuais e heap Lean 2 GiB.

## Motores: dependências efetivamente preparadas

Python dos motores: **3.12.14**, sem trocar o Python 3.14 do Core.

| Motor | Ambiente | Versões centrais observadas | Resultado |
|---|---|---|---|
| hf-peft | .its-fine/venv | torch 2.14.1+cpu, transformers 5.20.1, peft 0.21.2 | Dependências e sonda CPU passaram |
| hf-encoder | mesmo ambiente de texto | mesmo lock, numpy 2.5.4 | Dependências e sonda CPU passaram |
| hf-tts | .its-fine/venvs/hf-tts | torch/torchaudio 2.11.0+cpu, transformers 4.57.3, accelerate 1.12.0, peft 0.18.0, qwen-tts 0.1.1 | Dependências e sonda CPU passaram |

Torch/Torchaudio 2.14.1 não formavam um par publicado: o resolvedor recusou a
tentativa antes da instalação. Voz recebeu o par 2.11.0 do índice oficial CPU,
mantendo o ambiente separado e as versões exigidas pelo motor.

Locks em `integrations/itsfine-locks/*-py312.txt` fixam versões e hashes de
artefatos. As sondas executam imports, pip check e operação pequena de
tensor/gradiente, sem otimizador ou modelo pré-treinado. Não medem qualidade
de geração, classificação ou voz. Dependências de UI instaladas por pacotes
não significam que um servidor ou interface tenha sido iniciado.

Estados distintos:

- dependencies_ready=true e cpu_probe_passed=true nos três motores;
- accelerator_available=false e training_ready=false neste host;
- CUDA não está disponível no WSL observado, inclusive no torch CUDA do Core;
- para treino GPU será necessário expor a GPU/driver no host e aprovar um perfil
  CUDA compatível, além de modelo, dados e receita. Não falsificamos esses campos.

Recibos em `.its-fine/core/engines/`. `engines-status` revalida locks/interpretador
e executa nova sonda local, não confia em engines_prontos ou em recibo isolado.
A política conservou o SHA256
`7e4a06b8a73ec04775e5aa27665f4f198e4ff3b5474abad2cf64bf763bc54200`.

## Comandos seguros

```bash
python3 -m marceloclaro.cli itsfine verify
python3 -m marceloclaro.cli itsfine engines-status
python3 -m marceloclaro.cli itsfine install-plan \
  --archive .its-fine/core/distributions/sandeco-itsfine-0.0.15.tgz
python3 -m marceloclaro.cli itsfine install \
  --archive .its-fine/core/distributions/sandeco-itsfine-0.0.15.tgz --confirm
python3 -m marceloclaro.cli itsfine engine-plan --engine hf-tts
python3 -m marceloclaro.cli itsfine prepare-engine --engine hf-tts --confirm
```

`--confirm` autoriza apenas aquela instalação/preparação, não altera permissões
nem autoriza treino. O TGZ é adquirido separadamente do npm na versão exata e
validado pelo SRI antes da execução. Reinstalação offline foi executada e
conferiu os 120 arquivos gerenciados sem alterar a política.

Use o verificador Core acima como entrada protegida. O script upstream é
preservado para manter integridade de distribuição; não se afirmou que foi
reescrito ou certificado para entradas arbitrárias fora da fachada.
Reinicie o OpenCode para descobrir o comando /itsfine e a skill atualizada.

## Suíte upstream: limitação externa, não teste inventado

O TGZ 0.0.15 declara `node --test tests/install.test.mjs`, mas não contém esse
arquivo. A auditoria automática registra `upstream_tests_status=not_shipped`
e `upstream_tests_executed=false`. Consultas npm não forneceram repositório;
buscas delimitadas no GitHub para sandeco/its-fine/itsfine/fine não confirmaram
uma origem inequívoca. Não usamos o pacote React homônimo pmndrs/its-fine.

As contraprovas Core estão presentes no repositório e foram executadas como
suíte de integração própria. Isso não substitui nem prova execução da suíte
do autor. Para fechar essa pendência externa é necessário repositório/commit
oficial acessível ou distribuição do autor que inclua os testes e direitos
aplicáveis. Não alteramos o pacote publicado nem fabricamos sua suíte.

## Atestação, review e evidências

O limite plano de 20.000 fontes permaneceu. As árvores gerenciadas continuam
hasheando cada fonte coberta, com teto por árvore de 100.000 arquivos/1 GiB e
64 MiB por arquivo. Texto e voz somaram 46.132 fontes/561.109.405 bytes nesta
observação. Locks, recibos, marker, pyvenv.cfg, manifesto e política entram na
identidade. Bibliotecas nativas fora dos sufixos fonte não ganham certificação.

O bug impediu o próprio runner de registrar a fase inicial: o RED nativo
`outputs/core-r924/runtime-native-red.xml` foi preservado como nativo, sem
assinatura retrospectiva. Após a representação das fontes funcionar, foi
capturado RED autenticado enquanto o vínculo de inputs ainda faltava; depois
o vínculo foi implementado. A revisão independente task-762f6c18 foi estática;
suas propostas foram convertidas em contraprovas, não aceitas como aprovação.
Encerrar filhos ao término do pai é contrato deliberado; não foi removido.

Contratos: SPEC-935-R924, R925 e R926. Evidências finais em `outputs/core-r924/`.
Nenhum resultado é revisão científica externa ou promessa de treino/modelo pronto.
