# R127 — Documentação minuciosa da arquitetura (legendas, elementos e processos, dupla-registro)

## Objetivo

Tornar a documentação da arquitetura minuciosa e completa em
dupla-registro (Leigo + PhD): legenda com a função de cada elemento e
explicação de cada processo, incluindo o subsistema de Apresentações
MIRA (R123–R126) — ausente das legendas/processos e dos diagramas — no
`README.md`, `ARCHITECTURE.md` e mapa 3D. Reconciliar as contagens vivas.

## Motivação

Pedido do usuário: "atualize o readme.md e as documentações e os mapas
Diagrama de Arquitetura, as legendas, função de cada elemento e processo
da arquitetura explicada para leigos e phd de forma minuciosa".

O README já tinha dupla-registro forte (Para Leigos/PhDs, Legenda das 6
camadas, Legenda da Arquitetura, 7 passos da orquestração), mas **não
cobria o MIRA**: sem legenda dos seus elementos, sem explicação do seu
processo, e o agente `mira-presenter` (R126) não aparecia em nenhum
diagrama. As contagens estavam defasadas em R125.

## Mudanças Entregues

1. **`README.md`**:
   - Nova **"Legenda do Subsistema de Apresentações MIRA"**: tabela
     dual-registro (Leigo × PhD) com a função de cada elemento
     (`MiraEngine`, `MiraDeckPipeline`, `MiraPresentationAgent`/
     `mira-presenter`, `present()`×`present_task()`) + as regras do
     método (Regra Zero, título ≤6, formato do card).
   - Nova seção de processo **"Como Funciona a Apresentação MIRA"**: os 6
     estágios (`extract → plan → copywrite → build → animate → validate`)
     explicados um a um em dupla-registro, com exemplo prático e o
     encaixe na arquitetura (análogo ao passo *Verificar*).
   - Nó `mira-presenter` + aresta "encarna o pipeline" no diagrama
     Mermaid; linha 6 da tabela de camadas cita o agente delegável (R126).
   - Contagens reconciliadas: 85 ciclos (R47–R127), 1351 testes, 46 specs,
     score médio 9.18 (recalculado da fonte).
2. **`ARCHITECTURE.md`**: nó `Illus` cita o agente (R126); nova seção
   **"Subsistema de Apresentações MIRA"** (tabela de elementos + processo
   dos 6 estágios + as duas vias de execução); tabela de specs +R126/+R127.
3. **`docs/architecture_map.html`**: novo nó "Apresentações MIRA" com
   legenda dual-registro explícita (Leigo/PhD) e o agente `mira-presenter`;
   stats atualizadas (1351 testes, 85 ciclos R1–R127, 46 specs); resumo
   phd e Evolution Registry reconciliados.
4. **`tests/test_r127_arch_docs_meticulous.py` (novo)**: 10 testes de
   conteúdo (TDD de documentação).

## Verificação

- TDD de documentação: testes escritos antes → vermelho (7 failed) →
  verde (10 passed).
- `node --check` no JS do mapa 3D → OK.
- Balanceamento Mermaid (README/ARCHITECTURE) verificado por teste
  parametrizado (colchetes e parênteses).
- Contagens conferidas contra a fonte real (`cycles.json` = 84 antes do
  append → 85; `ls specs/SPEC-935-R*` = 45 → 46; `pytest --collect-only`
  = 1351).
- `python3 -m pytest tests/ -q` completo.

## Lições

1. Documentar um subsistema pede as duas faces em paralelo: a **legenda**
   (o que cada peça É — função) e o **processo** (como as peças se
   encadeiam — fluxo). O MIRA já tinha código, testes e specs, mas sem
   essas duas faces na documentação ele era, para um leitor novo,
   invisível na arquitetura — o mesmo tipo de lacuna de exposição que o
   R125 corrigiu no CLI, agora na camada de documentação.
2. A dívida das "contagens vivas" (testes/ciclos/specs hardcodados em 3
   arquivos) reincidiu de novo (defasagem em R125 após R126). Reforça,
   pela terceira vez (R122/R125/R127), que o certo é gerar esses números
   da fonte; fica registrado como dívida técnica a pagar com um pequeno
   gerador em ciclo futuro.

## Score

**8.6/10**

- Fecha o pedido direto (legendas + função de cada elemento + processo,
  para leigo e PhD, minucioso), cobrindo o subsistema que faltava e
  verificado por TDD de documentação.
- Reconcilia as contagens contra a fonte e mantém a paridade dos
  diagramas (Mermaid balanceado, JS do mapa válido).
- Não elimina a causa raiz da defasagem recorrente das contagens (gerador
  automático) — deixado explícito como dívida técnica, não escondido.
