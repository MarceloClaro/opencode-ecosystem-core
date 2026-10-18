# REA, MiroFish Offline e Lean 4 locais

Os três plugins privados usam o primário MarceloClaro e os motores instalados
neste computador. OpenCode Go é somente o ambiente de uso informado pelo autor.
O plugin Core continua responsável pela coordenação geral.

| Plugin | Ferramentas | Evidência exigida |
| --- | --- | --- |
| REA Local | `rea_status`, `rea_action` | operação concluída, artefatos, limites da análise estática |
| MiroFish Offline | `mirofish_status`, `mirofish_run` | inferência observada, saída OASIS e recibos |
| Lean 4 Local | `lean4_status`, `lean4_verify` | compilador real, código de saída e relatório de axiomas |

## Ativação

Os pacotes são gerados por `integrations.component_plugins` e instalados por
`scripts/install_component_plugins.ps1`, com inventário fechado, hashes e
preservação das entradas existentes do marketplace pessoal. Não incluem modelos,
credenciais, runtimes externos ou cópias completas dos repositórios.

Na interface que admite plugins locais, selecione o plugin correspondente ou
abra uma nova conversa após a instalação. Habilitação registrada não garante
que o catálogo desta conversa tenha sido recarregado. Consulte a ferramenta de
status e só depois execute uma operação. O transporte stdio é verificado por
`scripts/probe_component_plugin.ps1`, a partir do manifesto realmente instalado.

As APIs locais estão documentadas em
[Plugins OpenAI](https://developers.openai.com/plugins/build/plugins) e
[uso em ChatGPT](https://developers.openai.com/plugins/deploy/connect-chatgpt).
Esta instalação não transforma o aplicativo ChatGPT em um executor CLI.

## Exemplos de argumentos

Os exemplos são objetos `config`, enviados à ferramenta de ação indicada.
Use caminhos Linux acessíveis ao WSL e diretórios de saída novos.

```json
{"operation":"analyze","path":"/home/marceloclaro/meu-aplicativo"}
```

```json
{"operation":"run","prompt":"Dois agentes discutem um cenário fictício de aprendizagem.","model":"core-mirofish-local","output_dir":"/home/marceloclaro/outputs/minha-simulacao-nova","timeout_seconds":300}
```

```json
{"operation":"verify","code":"theorem exemplo (n : Nat) : n = n := by rfl","use_mathlib":false,"timeout_seconds":30}
```

O modelo `core-mirofish-local` usa a configuração privada
`~/.local/share/opencode-core/mirofish-local-model.json`. O servidor CPU
llama.cpp é iniciado sob demanda em `127.0.0.1:11436`, serializado e encerrado
após a análise. Reutiliza o arquivo GGUF existente; nenhum modelo é baixado
durante uma simulação. Outro modelo pode ser indicado com endpoint HTTP loopback
explícito, desde que esteja disponível. A configuração não autentica provedores.

## Limites verificáveis

REA não executa o alvo analisado. A presença de Ghidra, Hopper ou IDA no
inventário não demonstra que cada engine concluiu uma análise. Ausências e
interpretações desconhecidas permanecem no relatório.

MiroFish executa o runtime OASIS externo com Hugging Face em modo offline e
chamadas de modelo diretas a loopback, sem proxy de ambiente nem redirecionamento.
Esses controles não equivalem a um sandbox de rede de todo o runtime externo.
Os agentes de teste são sintéticos: suas respostas não validam previsões sociais.
Pesos auxiliares inicializados sem treinamento são uma limitação do runtime.

Lean executa em namespace sem rede e com recursos delimitados. A interface
recusa `sorry`, `admit`, axiomas inseridos e comandos de execução/metaprogramação;
uma prova falsa precisa falhar no compilador. O relatório apresenta os axiomas
utilizados. A prova cobre o enunciado formal submetido, sem certificar pressupostos
empíricos ou todos os capítulos do livro. Indisponibilidade bloqueia a operação.

Arquivos e modelos são processados localmente. Resultados trazidos à conversa
são processados pelo serviço que mantém essa conversa. Não envie dados sigilosos
por presumir que a interface de chat funciona inteiramente offline.

## Prontidão observada nesta máquina

A sonda REA concluiu análise estática de um fixture JavaScript. Lean aceitou
prova válida e rejeitou prova falsa e admissão. MiroFish concluiu anteriormente
uma rodada OASIS com dois agentes e duas gerações locais. Na verificação posterior
com servidor sob demanda, o modelo iniciou e foi encerrado após uso, porém o
OASIS excedeu 300 segundos sem completar a geração. Esse resultado está marcado
como bloqueado, sem substituir a falha pelo sucesso anterior. Havia outros
serviços locais de modelos ativos; não foram encerrados para forçar o teste.

Assim, a instalação não certifica latência, disponibilidade sob carga ou escala.
Consulte os recibos de `docs/verification-component-plugins-r913.json` antes de
classificar uma execução como concluída. O uso simultâneo de modelos depende
de recursos da máquina; o servidor sob demanda possui prazo e encerra seu próprio
processo quando a análise termina ou falha.

## Manutenção

Execute `python3 -m pytest tests/test_r913_component_plugins.py -q` e
`python3 -m marceloclaro.cli doctor`. O diagnóstico descreve saúde estrutural;
as sondas funcionais têm recibos próprios. Para recuperação, preserve recibos,
confira o manifesto e reinstale somente o pacote afetado. Não sobrescreva
checkouts externos modificados nem encerre serviços de modelos de outras tarefas.
