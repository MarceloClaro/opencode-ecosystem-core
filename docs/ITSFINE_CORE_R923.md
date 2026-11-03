# ITS-FINE no Core — R923

> Registro histórico da instalação inicial. O estado atualizado dos motores,
> instalador e validações está em [Correções R924–R926](ITSFINE_CORRECOES_R924.md).

## Instalação observada

Instalado **@sandeco/itsfine 0.0.15**, com tarball npm auditado e fixado por
SHA-512. Comando equivalente ao pedido `npx @sandeco/itsfine install`:

```bash
npm exec --yes --package /tmp/opencode/sandeco-itsfine-0.0.15.tgz -- \
  itsfine install --engines opencode --yes --user marceloclaro
```

O bootstrap inicial excedeu 240 s e não foi contado como concluído. Após
instalar jsonschema na venv própria com prazo explícito, a repetição terminou.
O verificador upstream confirmou **15 skills, 120 arquivos gerenciados, CLI e
schemas**. Nenhum hook Claude foi configurado. Os três motores continuam
`preparado=false/dependencias_ausentes`: não houve treino, download de pesos
ou inferência. Certificados históricos distribuídos não são ensaios locais novos.

Origem: https://registry.npmjs.org/@sandeco%2fitsfine/latest

SRI: `sha512-LpfBJTaZaGBOpH6u1A8DzrsIGFxMjpWL7ZqaVAv8CNeoNtaE+sLxw9DmMiGyfHMlB4UHqDmU9dF8JNpqLSm7hw==`.

## Benefícios e limites

| Componente | Ajuda concreta | O que ainda precisa ser demonstrado |
|---|---|---|
| hf-peft upstream | Dataset, receita LoRA, treino supervisionado, avaliação e exportação GGUF/Ollama | Dados/modelos autorizados, ambiente e benchmark |
| hf-encoder upstream | Decisões tipadas/classificação e calibração | Qualidade e calibração no domínio de uso |
| hf-tts upstream | Pipeline de voz por famílias de modelos | Direitos da voz/dados, ambiente e avaliação humana |
| Adaptador Core original | Status inerte, hashes, plano selado/retomável e diagnósticos sob orçamento | Não autoriza nem executa treino |
| REA + SDD/TDD | Evidência de pacote e contraprovas de integração, paths, adulteração e orçamento | Não equivalem a validação científica ou segurança contra o dono do host |
| MiroFish acadêmico | Ensaiar perguntas e cenários sobre a pesquisa até a defesa | Simulação não é parecer humano nem aprovação científica |

MarceloClaro permanece o primário. RAG continua separado; fine-tuning não
substitui recuperação de fontes auditadas.

## Uso funcional

```bash
python3 -m integrations.itsfine_core status
python3 -m integrations.itsfine_core plan --run-id minha-rodada
python3 -m integrations.itsfine_core run --run-id minha-rodada
```

```python
from marceloclaro.orchestrator import MarceloClaroOrchestrator
core = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
plano = core.itsfine_action({"operation": "plan", "run_id": "minha-rodada"})
resultado = core.itsfine_action({"operation": "run", "plan": plano,
                               "max_steps": 3, "timeout_seconds": 30})
```

`run` apenas verifica hashes e executa `engines` e `route` com argv fixo. Não
aceita comandos, URLs, scripts ou modelos arbitrários. Instalação e política
são revalidadas antes de cada processo; cancelamento/orçamento interrompem com
estado explícito. A skill sugerida não é invocada. O diagnóstico real terminou
`awaiting_human`: 3 passos, 2 processos somente leitura, próxima `fine-objective`.
Consultar um run_id inexistente não cria dados ou uma rodada treinada.

`.its-fine/policy.json` continua exclusivo do usuário. A adaptação não altera
allow_process, dados, endpoints, transferências, Kaggle ou Colab. Autonomia
implementada é **de diagnóstico e planejamento**, não treino irrestrito.
Reinicie o OpenCode para descobrir as skills novas em `.agents` e a skill
original `.opencode/skills/itsfine-core`. Não há hot-reload da sessão corrente.
Skills-filhas desabilitadas devem ser lidas/conduzidas pelo primário no contexto.

## REA e gaps observados

REA 6.4.0 executou `analyze_javascript_application` sobre o pacote distribuído,
sem executá-lo: 13 arquivos relevantes, 2 JS parseados, 3.620 nós AST e zero
falhas de parsing JS. As 28 ocorrências do analisador **não são 28 bugs**.
A parte Python foi complementada por leitura estática manual.

Evidência: `ev_277240ca2186690029c50bf9aaeb83aeb8b2de9760cadf85903c2078bda1ed3e`.
Artefato SHA256: `804c8b130274c4dd1bf2cf160ee5de3e886bc3ed96ffc94e6d3dcee7cf27d7a2`.
Resposta integral SHA256: `3eca6a2d956f07111eea2b6e3c34c6ae3e97a33c0e18e136b5f782e3f9bf467a`, retida em `.opencode/rea/evidence/`.

| Gap delimitado | Tratamento |
|---|---|
| Instalação interativa/Claude-Codex por padrão | Seleção explícita OpenCode, sem hooks adicionais |
| Bootstrap sem deadline global próprio | Timeout registrado e dependência resolvida com prazo explícito |
| update consulta/delega latest | Versão/SRI fixados; adaptador não atualiza pacote |
| Skills em .agents sem fachada primária específica | Método itsfine_action, CLI original e skill itsfine-core |
| Verificador upstream confia em paths do manifesto | Ponte confina diretórios, recusa traversal/symlinks e deriva |
| Testes referenciados por npm test não vêm no tarball | Contraprovas locais próprias; suíte upstream não foi alegada |
| README diz 14 skills; instalador entregou 15 | Contagem efetivamente observada preservada |
| Sem licença raiz no package.json/tarball | Instalação local autorizada e composição, não redistribuição de fork |

REA pode orientar uma adaptação mais funcional, mas não gera sozinho uma
versão autônoma comprovadamente superior. Esta é uma camada original do Core,
não uma nova edição oficial/relicenciada do ITS-FINE.

Treino real exige intenção/domínio, dados licenciados, política manual, modelo,
ambiente, holdout por documento/grupo, baseline e régua de aceite antes de
autorizar receita/processos. Sem isso, entregar plano e pendências.
Recibos: `outputs/core-r923/itsfine-plan.json` e `itsfine-diagnostics.json`;
contrato/testes: SPEC-935-R923 e `tests/test_r923_itsfine_core.py`.
