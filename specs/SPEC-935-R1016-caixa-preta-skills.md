---
spec_id: SPEC-935-R1016
title: Pacote de skills audiovisuais (sete cp-* e três meia-*)
component: .claude/skills
status: implemented
test_file: tests/test_r1016_cp_skills.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1016-1:
      - "tests/test_r1016_cp_skills.py::test_cp_package_structure"
    R1016-2:
      - "tests/test_r1016_cp_skills.py::test_meia_package_structure"
    R1016-3:
      - "tests/test_r1016_cp_skills.py::test_cp_skill_contract"
      - "tests/test_r1016_cp_skills.py::test_meia_skill_contract"
    R1016-4:
      - "tests/test_r1016_cp_skills.py::test_shared_safety_contract"
    R1016-5:
      - "tests/test_r1016_cp_skills.py::test_text_only_and_no_personal_data"
---

# SPEC-935-R1016 — Pacote de skills audiovisuais

**Estado:** implementado e testado localmente; revisão independente pendente.
**Escopo autorizado:** dez skills de projeto em `.claude/skills/`, conforme pedido do usuário.

## Objetivo

Instalar e manter um pacote de skills de projeto para direção e edição
audiovisual assistida por IA:

- sete skills `cp-*`, com o pacote oficial de referência fornecido pelo usuário;
- três skills `meia-*`, derivadas do método do segundo livro e escritas como
  instruções originais.

As skills são texto instrutivo. Elas não executam edição, renderização,
exportação, instalação ou chamadas externas por si mesmas.

## Fontes e direitos

1. `biblioteca ai/livro-digital-caixa-preta-da-edicao182438063 (1).pdf`
   (SHA-256 `b905dfbd032547ae7bc250c322d1a234899d6009c9fcb7db0744ac1164c40f01`),
   que descreve as sete skills `cp-*`.
2. `biblioteca ai/skills (1).zip` (SHA-256 registrado no recibo de importação),
   pacote de referência com `SKILL.md`, `references/` e `agents/openai.yaml` das
   sete skills `cp-*`.
3. `biblioteca ai/download-livro-digital-cofre-da-edicao-com-ia.pdf`, cujo
   conteúdo é “Máquina de Edição IA” e cujo Apêndice C descreve as três skills
   `meia-*`.
4. Documentação oficial do Remotion fornecida pelo usuário em 1º/11/2026:
   `https://www.remotion.dev/docs`, `https://www.remotion.dev/docs/api`,
   `https://github.com/remotion-dev/remotion` e o exemplo de CLI. O endereço
   `/docs/cli/` retornou 404; os comandos foram conferidos em páginas oficiais
   equivalentes e registrados em
   `.claude/skills/cp-direcao-de-edicao/references/remotion-cli-e-api.md`.
5. Repositório Hypit `https://github.com/hypit-ai/hypit` e sua licença
   pública, consultados em 1º/11/2026. Hypit é registrado apenas como caminho
   externo opcional em
   `.claude/skills/cp-direcao-de-edicao/references/ecossistema-hypit.md`; não
   foi instalado, autenticado ou executado.

Os dois livros declaram que o leitor pode copiar e adaptar comandos, modelos e
skills para seus próprios projetos. A instalação preserva a autoria e não
redistribui o PDF. As três skills `meia-*` foram redigidas de forma original a
partir das funções descritas no livro; não reproduzem páginas, imagens ou dados
pessoais.

## Escopo

Instalar em `.claude/skills/`:

1. `cp-extratora-de-referencia`
2. `cp-estilo-por-referencia`
3. `cp-direcao-de-edicao`
4. `cp-apresentador-em-cena`
5. `cp-lettering-com-hierarquia`
6. `cp-motion-explicativo`
7. `cp-variacoes-controladas`
8. `meia-briefing-de-edicao`
9. `meia-legendas-e-enquadramento`
10. `meia-revisao-economia`

As sete `cp-*` incluem os arquivos de referência e o `agents/openai.yaml` do
pacote fornecido, com uma linha adicional de direitos/consentimento onde o texto
original não a explicitava. As três `meia-*` contêm `SKILL.md` auto-contido.
Não instalar no perfil global do usuário, não alterar configurações do Claude e
não executar instaladores do pacote.

## Contratos

### Sete skills `cp-*`

- **Extratora de referência:** inventariar a mídia realmente acessível, separar
  `observado`, `inferido` e `nao_verificavel`, e produzir relatório, mapa de
  cenas, receita visual e prompt de recriação sem copiar a obra.
- **Estilo por referência:** transferir gramática visual para a fala, materiais e
  identidade do usuário, sem importar conteúdo, oferta ou assets de terceiros.
- **Direção de edição:** dividir a fala em unidades de sentido e definir foco,
  mudança e continuidade de cada cena.
- **Apresentador em cena:** preservar rosto, cabeça e gestos em recortes e
  molduras; não gerar avatar, trocar identidade ou presumir recorte alfa.
- **Lettering com hierarquia:** ordenar texto de tela, preservar legenda e
  licença de fontes, mantendo sentido, números e condições.
- **Motion explicativo:** representar estado inicial, ação e estado final sem
  fabricar dados, medida ou causalidade.
- **Variações controladas:** partir de base aprovada, mudar uma variável por
  hipótese, preservar originais e registrar matriz/manifesto; não alegar
  desempenho sem métricas reais.

### Três skills `meia-*`

- **Briefing de edição:** converter pedido e materiais em briefing executável,
  sem repetir perguntas já respondidas, sem inventar oferta e sem ampliar escopo.
- **Legendas e enquadramento:** sincronizar legendas pela fala real e compor para
  o destino, preservando rosto, gestos, leitura e proporção; não reescrever a
  mensagem nem remover fundo automaticamente.
- **Revisão econômica:** corrigir por intervalo, diagnosticar causa de erro
  repetido, reutilizar trabalho aprovado e distinguir custo observado de
  estimativa; não reabrir a direção criativa.

## Adaptações em relação ao pacote fornecido

- Os sete `SKILL.md` do ZIP foram importados como fonte principal. Foram
  acrescentadas, quando ausentes, uma linha de direitos/consentimento e uma
  seção final “Salvaguardas adicionais” com preservação de originais, proibição
  de sobrescrita e limite explícito para transferência a serviços externos.
- Foi acrescentada a referência `remotion-cli-e-api.md` em
  `cp-direcao-de-edicao`, com comandos oficiais conferidos e a ressalva de que
  documentação não prova execução.
- As três skills `meia-*` são redação original baseada no Apêndice C do segundo
  livro; não são cópia literal do texto das skills do livro.

## Salvaguardas transversais

1. Preservar originais; não sobrescrever, renderizar ou exportar mídia sem
   autorização explícita.
2. Respeitar direitos, licença, consentimento e privacidade de pessoas, vozes,
   imagens, fontes e materiais de terceiros.
3. Não usar serviços pagos, APIs adicionais ou transferência externa de mídia sem
   autorização correspondente.
4. Antes de lote ou exportação, apresentar amostra representativa e aguardar
   aprovação explícita, salvo quando a execução completa já tiver sido autorizada
   com critérios suficientes.
5. Distinguir observação, inferência, proposta e desconhecido. Não declarar
   execução, análise completa, métrica ou custo sem evidência observada.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1016-1` — Pacote `cp-*`: as sete pastas existem, cada `SKILL.md` tem
  frontmatter com `name` igual ao slug, `agents/openai.yaml` existe, há pelo menos
  um `references/*.md` e os links relativos de referência resolvem.
- `R1016-2` — Pacote `meia-*`: as três pastas existem, cada `SKILL.md` tem
  frontmatter válido e seção de salvaguardas.
- `R1016-3` — Contratos distintos: cada skill cobre os conceitos que a
  distinguem, sem ser mero alias de outra.
- `R1016-4` — Segurança e direitos: todas as dez skills explicitam autorização,
  preservação de original, revisão por amostra/aprovação, limite de serviço
  externo e direitos/licença.
- `R1016-5` — Texto e privacidade: os diretórios contêm apenas `.md`/`.yaml` e
  nenhum dado pessoal do PDF ou credencial.

## Plano de teste

1. Manter `tests/test_r1016_cp_skills.py` como oráculo determinístico, sem rede,
   LLM ou relógio.
2. Executar o histórico RED/GREEN em worktree isolada, porque o checkout
   principal contém dependências locais que excedem o limite de fontes do
   `TDDHistory`.
3. Comparar os hashes dos artefatos entre a worktree e o checkout antes de
   aceitar o gate.
4. Rodar `python3 -m pytest -q tests/test_r1016_cp_skills.py` e
   `python3 -m marceloclaro.cli doctor` no checkout.

## Evidência observada

- O pacote oficial foi importado do ZIP fornecido; a árvore instalada tem
  **25 arquivos** nas sete pastas `cp-*` (sete `SKILL.md`, sete
  `agents/openai.yaml` e onze referências `.md`, incluindo Remotion e Hypit).
- As três skills `meia-*` foram criadas como Markdown original e somam três
  `SKILL.md`.
- A suíte local `tests/test_r1016_cp_skills.py` passou com **23 testes**.
- O histórico RED/GREEN e o `SpecVerifier` foram reexecutados em worktree
  isolada para esta versão expandida: par válido, **5/5 critérios** no gate
  `software_delivery_gate` e RED/GREEN aceitos. Os **28 arquivos** de skill
  (25 do pacote `cp-*` e 3 `meia-*`), a spec e o teste foram comparados byte a
  byte entre a worktree e o checkout, sem divergência.
- A revisão independente por executor externo ainda não foi concluída nesta
  rodada; qualquer falha de provedor será registrada como indisponibilidade, não
  como parecer.

## Limites

Os testes verificam estrutura, sintaxe YAML, resolução de links relativos,
conteúdo textual e salvaguardas declaradas. As buscas de contrato são lexicais:
presença de termos não prova que a instrução seja semanticamente correta nem que
duas skills não se sobreponham em um caso concreto. Os testes não comprovam que
Claude Code ou OpenCode carregaram as skills em runtime, que um editor de vídeo
executou uma tarefa, que as escolhas são juridicamente suficientes ou que a
edição resultante é boa. A validação é local e não substitui revisão humana,
teste em produção ou parecer jurídico.
