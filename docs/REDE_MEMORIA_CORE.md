# Rede de memória do Core

O terminal e a nona aba do painel usam a mesma projeção de registros existentes
do MetaBus, EvidenceGraph e Blackboard. As cores distinguem consultas, memória,
contexto, agentes, evidências e respostas. Atividade corresponde a um evento
com timestamp nos últimos cinco segundos. Não representa atenção interna de um
LLM, execução de um agente apenas disponível ou probabilidade calibrada.

No ambiente Python do projeto:

```bash
python -m webapp.memory_network_visualizer
python -m webapp.memory_network_visualizer --once --json
python -m webapp.memory_network_visualizer --frames 20 --interval 0.5
python -m webapp.memory_network_visualizer --demo --frames 20
```

Em terminal interativo, a projeção se atualiza até Ctrl+C. Sem terminal
interativo, a execução padrão imprime um quadro e termina. `--demo` identifica
explicitamente dados fictícios e não modifica a memória.

Para o painel, instale `requirements-webapp.txt` no ambiente do projeto e abra:

```bash
python -m streamlit run webapp/app.py --server.address 127.0.0.1
```

Selecione **Rede de memória**. A consulta opcional realiza busca lexical real
nos registros locais; eventos correlacionados mostram o fluxo de recuperação.
Não chama um LLM. A atualização automática, animação, filtros por tipo e
seletor de detalhes são independentes. Para inspecionar um nó sem troca de
quadro, desative a atualização automática. Preferência de movimento reduzido
do navegador é respeitada. Dados e demonstração permanecem identificados.

A seleção contém até 100 nós e 200 arestas, priorizando eventos e evidências;
o canvas exibe até oito nós por tipo. O seletor permite acessar nós não
desenhados inicialmente. A leitura JSON é limitada a 8 MiB por fonte; eventos
usam janela final de 256 KiB e até 200 linhas. Fontes inválidas ou parciais
aparecem nos avisos. Pesos são os valores registrados; relevância ausente
permanece não registrada. Não existe promessa de cobertura integral.

Especificação: `specs/SPEC-935-R829-rede-memoria-observada.md`.
Testes e sondagem real do navegador: `outputs/core-r829/`.
