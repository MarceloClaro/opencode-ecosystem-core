# Referências de arquitetura e limites de integração — v3.0

Leitura de fontes realizada em 24 set. 2026. Usar os projetos abaixo como referência de organização de tarefas, memória e evidências. Esta atualização acrescenta protocolos ao plugin; não instala os repositórios, executa seus motores ou cria um servidor clínico. Relatar separadamente o que foi lido, adaptado, configurado e efetivamente executado.

## MiroFish-Offline

Fonte: https://github.com/MarceloClaro/MiroFish-Offline

- `README.md`, blob `a457030b779fd2e7572caab50c8085bfb5bed10c`: descreve simulação de opinião pública e dinâmicas sociais, com personas, memória em grafo e stack Neo4j/Ollama local.
- `backend/app/storage/graph_storage.py`, blob `ecdffe880403b6b56887377480941e68b2b41e73`: interface de episódios, nós, arestas, ontologia e busca.

Adaptação conceitual: registrar acontecimentos e fontes, manter entidades separadas, explicitar relações e recuperar documentos pertinentes. Não importar personas sociais, vieses de opinião, votos ou popularidade para produzir diagnósticos. A descrição e o código lidos não apresentam validação clínica para simular a evolução biológica de um paciente.

Extração automática de entidades/relações e busca vetorial podem errar nomes, negações e datas. Submeter as saídas à conferência documental. Não converter relevância de busca em força de evidência médica. Não copiar regras clínicas de um motor social.

## OpenCode Ecosystem Core

Fonte: https://github.com/MarceloClaro/opencode-ecosystem-core

- `README.md`, blob `9fe833a49533728d67ca0daa342b975e822b8fde`: orquestração, Blackboard/MetaBus, SDD/TDD e revisão metacognitiva.
- `ARCHITECTURE.md`, blob `23b701ec120adee5b62ca764464e152d09212789`: diferencia configuração, execução observada e validação externa.
- `mci/orchestration.py`, blob `1d88edb87b5af394ca7cd298f6a581913a3e43b8`: ciclo de hipóteses, revisão adversarial e registro de evidências; a exceção na validação de schema é ignorada nesse arquivo.
- `integrations/medical/clinical_orchestrator_bridge.py`, blob `50903eba6324f400fc96fb368709f15feacaf6d4`, trecho inicial inspecionado: contém valores predefinidos para gravidade, hipóteses, probabilidades e desempenho de testes quando faltam entradas.
- `integrations/medical/clinical_verifier.py`, blob `69a4355f3785c77972b697d3932ecc5922c37e99`: usa defaults de função renal/gestação e busca textual de alarmes; há um rótulo de verificação simbólica atribuído antes da condição de execução do solver.

Adaptação: coordenador, pacote comum de fatos, pareceres por área, contraditório, registro de conflitos e verificação do resultado. Não reutilizar os defaults clínicos, regras farmacológicas simplificadas, pontuações internas ou rótulos de verificação como prova de adequação individual. O verificador não cobre todas as contraindicações. Correspondência de palavras não determina sozinha se um alarme está presente, negado, antigo ou atribuído a terceiro.

Esses achados são da leitura dos arquivos identificados, não resultado de execução nem auditoria exaustiva do repositório. Revisar a versão atual antes de qualquer integração futura. Não inferir que toda a arquitetura tem as mesmas limitações de um arquivo, nem que documentação comprova funcionamento.

## Contrato para eventual integração real

Somente ativar integração quando houver pedido que a autorize, ferramenta disponível e implantação verificável. Preservar o modo de análise por texto quando essas condições não existirem.

Antes de enviar dados clínicos, verificar destino/provedor, minimização, segregação de casos, permissões, finalidade e autorização aplicável. Preferir dados sintéticos nos testes; não subir prontuários para GitHub ou logs gerais. “Local/offline” depende da configuração completa, inclusive embeddings, APIs, telemetria e rede; não é garantia automática.

Receber fontes com ID, versão, paciente/episódio, data do evento e estado de informação. Cada conclusão deve retornar referências resolvíveis, dúvidas e registro de execução real. Rejeitar na etapa dependente: paciente divergente; fonte inexistente; schema inválido; dado crítico preenchido por default; probabilidade sem método; tarefa não executada apresentada como concluída; falha ocultada. Erro técnico bloqueia a conclusão dependente, sem impedir orientação urgente ou explicação geral segura.

Na avaliação, distinguir: estrutura dos dados; comportamento em casos sintéticos; execução dos conectores; validação clínica externa com população, desfechos e supervisão apropriados. Sucesso nas primeiras etapas não demonstra a última. Não alegar sensibilidade, especificidade, calibração, superioridade médica, aprovação regulatória ou equivalência a especialistas sem estudo pertinente.

## Fonte de governança consultada

WORLD HEALTH ORGANIZATION. **WHO releases AI ethics and governance guidance for large multi-modal models**. Geneva: WHO, 18 jan. 2024. Seções “Potential benefits and risks” e “Key recommendations”. Disponível em: https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models. Acesso em: 24 set. 2026.

A OMS descreve riscos de respostas falsas, vieses e confiança excessiva na automação, além da necessidade de participação de usuários e avaliação. Esses princípios fundamentam a transparência adotada aqui; não certificam este plugin. Página sem DOI/paginação estável: não inventar esses campos.

## Verificação operacional em revisões futuras

Avaliar pelo menos: urgência antes de debate; falta de dados mantida como desconhecida; pacientes não misturados; datas do evento e documento separadas; causalidade não inferida só pela sequência; discordâncias preservadas; tratamento apresentado condicionalmente; fontes não inventadas; ausência de ferramenta declarada; teste técnico não chamado de validação clínica. Registrar entrada, saída observada, critério, falha/limitação e ação corretiva. Não registrar como aprovado um teste somente planejado.
