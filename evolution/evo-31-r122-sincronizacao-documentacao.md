# R122 — Sincronização de Documentação (README, ARCHITECTURE, Mapa 3D)

## Objetivo

Atualizar `README.md`, `ARCHITECTURE.md` e o mapa interativo 3D
(`docs/architecture_map.html`) para cobrir os ciclos R117–R121 e
corrigir números defasados que ainda refletiam o estado do projeto em
torno do R107.

## Mudanças Entregues

1. **Números corrigidos** em `README.md` e `docs/architecture_map.html`:
   testes (1062→1288), ciclos de evolução (65→79, faixa R47–R107→R47–
   R121), especificações formais (35→40 em `ARCHITECTURE.md`/mapa 3D),
   score médio recalculado (9.4→9.23, valor real de
   `evolution_registry.average_score()`).

2. **Bullets de feature adicionados ao `README.md`** para os 5 ciclos
   sem nenhuma menção na lista principal de recursos: R117 (mapa 3D),
   R118 (fix handshake MCP), R119 (templates literários), R120 (CLI
   `pesquisa`), R121 (isolamento real de testes).

3. **Tabela de especificações formais em `ARCHITECTURE.md`** ganhou as
   3 linhas faltantes: SPEC-935-R119/R120/R121.

4. **Paridade real entre os dois diagramas Mermaid restaurada**: o nó
   `Publishing` existia apenas em `ARCHITECTURE.md` — adicionado
   também ao diagrama do `README.md`, com a mesma anotação de R119
   (templates literários) em ambos. Nós `MCPSec`/`CICD` em ambos os
   diagramas passaram a mencionar as correções de R118/R121
   respectivamente. Nó "Research Hub" do mapa 3D e "CLI marceloclaro"
   atualizados com a opção `[9] Pesquisa` (R120).

## Verificação

- `node --check` no JS extraído de `docs/architecture_map.html` → OK
- Balanceamento de colchetes/parênteses dos 2 blocos Mermaid (README:
  78/78 colchetes, 20/20 parênteses; ARCHITECTURE: 74/74 colchetes,
  38/38 parênteses) → OK
- `python3 -m pytest tests/test_r104b_pip_packages.py
  tests/test_r110_doctor_corrigendum.py
  tests/test_r116_installer_platform_upgrade.py -q` → 70 passed, 3
  skipped (nenhuma asserção de conteúdo de README/ARCHITECTURE/MANUAL
  quebrada)
- `python3 -m pytest tests/ -q` completo

## Lições

1. Documentação que menciona números "vivos" (contagem de testes,
   ciclos, specs) decai rápido — vale considerar, num ciclo futuro,
   gerar esses números automaticamente a partir de
   `evolution/cycles.json`/`pytest --collect-only`/`specs/` em vez de
   hardcodá-los em múltiplos arquivos.
2. A disciplina de "dupla-registro" instituída pelo R117 (dois
   diagramas Mermaid mantidos em paridade) precisa de verificação
   ativa — o nó `Publishing` divergiu silenciosamente entre os dois
   arquivos até esta auditoria pontual encontrá-lo. Um teste
   automatizado comparando os identificadores de nó entre os dois
   diagramas seria uma forma barata de blindar essa invariante no
   futuro.

## Score

**8.5/10**

- Corrige uma lacuna documental real e mensurável (números defasados,
  5 ciclos sem menção, divergência de nó entre diagramas), não apenas
  cosmética
- Verificação estrutural adequada ao tipo de mudança (sintaxe JS,
  balanceamento Mermaid, testes de conteúdo existentes), seguindo o
  mesmo padrão já usado no R117
- Não propõe automatizar a geração desses números a partir da fonte
  real (fica como lição para ciclo futuro) — a correção pontual atual
  ainda vai decair com o tempo se repetida manualmente
