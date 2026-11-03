# SPEC-935-R913 — REA, MiroFish Offline e Lean 4 como plugins locais

## Escopo autorizado

Repetir a instalação privada R912 para três componentes existentes, sob o
primário MarceloClaro. Interpretar “Learn 4” como Lean 4. OpenCode Go foi
identificado pelo usuário somente como ambiente, sem configurar outro provedor.
Não presumir instalação, inferência, aprovação científica ou ativação da conversa.

## Contratos

1. Três pacotes locais independentes, cinco arquivos delimitados por pacote,
   reutilizando o gerador e o arquivo exclusivo R912. Identidades distintas:
   opencode-rea, opencode-mirofish-offline e opencode-lean4. Não copiar runtimes,
   modelos, fontes externas, .env ou credenciais para os pacotes.
2. Um entrypoint MCP parametrizado por componente com catálogo fechado de duas
   ferramentas por componente. Chamadas passam por MarceloClaro; sem segundo
   coordenador. Registrar observações sem promover confiança por disponibilidade.
3. REA reutiliza rea_action/ReaBridge. Inventário não equivale a handshake ou
   análise. Análises permanecem estáticas, com evidência e limites.
4. MiroFish reutiliza LiveScientificRuntime e checkout AGPL externo por composição.
   Status do checkout não significa inferência. Execução usa exclusivamente
   runtime=mirofish e endpoint de modelo loopback, com artefatos e tokens auditados.
   Simulação sintética não é previsão validada nem observação de população real.
5. Lean 4 usa compilador real em namespace local com rede isolada e filesystem
   delimitado. Sem sandbox/compilador não há fallback para prova sintática.
   Limitar fonte, prazo e recursos. Recusar sorry/admit/axiom e comandos de
   metaprogramação/IO da interface; rejeitar prova falsa. Mathlib, quando
   solicitado, usa somente o projeto local conhecido livro-core/lean.
   Prova formal limita-se ao enunciado e às dependências declaradas; não valida
   fatos empíricos nem substitui revisão humana.
6. Instalador conserva o plugin Core e demais entradas. Origem local e hashes
   precisam corresponder. Nunca editar cache do host ou substituir fonte divergente.
7. Sonda Windows inicia o comando efetivamente instalado, descobre as duas
   ferramentas e chama status e uma operação funcional de cada componente.
   Guardar retornos e hashes. Separar instalação, transporte e ativação na conversa.

## Aceitação e sequência

RED em tests/test_r913_component_plugins.py antes da implementação. GREEN inclui
pacotes/launchers, catálogo de ferramentas, validação negativa e roteamento pelo
primário. Verificar regressões R912 e interfaces existentes. Sondas físicas:
análise REA de fixture JavaScript; rodada OASIS sintética com modelo local e banco
próprio; teorema Lean verdadeiro e teorema falso, com sorry bloqueado.

Somente declarar operação concluída quando recibo observar o resultado exigido.
Caso o runtime falhe, corrigir dentro do escopo ou registrar precisamente a
pendência, sem substituir por simulação determinística. Sem certificação externa.
