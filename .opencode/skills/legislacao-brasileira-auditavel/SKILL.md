---
name: legislacao-brasileira-auditavel
description: Consulta e registra legislação brasileira com jurisdição, data de referência, fonte oficial, versão do texto e hash, distinguindo norma vigente, redação histórica e proposição. Use para localizar dispositivos, montar dossiê de pesquisa ou conferir citações legais; não certifica vigência, não substitui o Diário Oficial e não trata projeto de lei como norma em vigor.
metadata:
  version: "1"
  origem: "R1023 — instrução original; reutiliza o MCP educacao-legislacao existente"
---

# Legislação brasileira auditável

Organize a consulta para que outra pessoa possa refazer o caminho até a fonte
oficial e verificar o que foi realmente lido. O resultado é um registro
rastreável, não um parecer jurídico e não uma certificação de vigência.

## Recorte temporal

Antes de consultar, declare:

- a pergunta e o dispositivo procurado;
- a jurisdição (federal, estadual, distrital ou municipal) e o ente;
- a data de referência `as_of` e o instante de coleta `retrieved_at`, ambos em
  ISO 8601;
- se a análise quer o texto vigente na data, a redação histórica de um período
  ou a evolução entre versões.

Não misture redações de datas diferentes no mesmo registro. Se a pergunta
depende de "o que valia em 2019", não use o texto compilado atual como se
fosse a redação daquele ano. Quando a data não puder ser estabelecida, registre
`nao_verificavel` em vez de inferir.

## Fontes e versões

Priorize a fonte oficial e registre a cadeia:

1. texto oficial no domínio do órgão competente (por exemplo, Planalto para
   leis federais, assembleia legislativa para lei estadual, câmara municipal
   para lei municipal);
2. URL solicitada, URL final após redirecionamentos, status HTTP, data e hash
   do conteúdo recebido;
3. tipo de registro: `enacted_norm`, `historical_text`, `consolidated` ou
   `proposal`;
4. versão do texto e indicação de compilação, quando existir;
5. localizador do dispositivo (artigo, parágrafo, inciso, página).

Use o MCP `educacao-legislacao` já registrado: `list_sources` mostra o catálogo
fechado e `fetch_source` faz GET somente de IDs predefinidos, com allowlist de
hosts oficiais. Não amplie a allowlist por conveniência e não troque a fonte
oficial por um repositório em Markdown, blog, agregador ou espelho não oficial.

Um repositório pode ajudar a localizar ou comparar, mas não é a publicação
oficial. Texto convertido por OCR, Markdown ou script é pista de leitura; a
conferência final vai à fonte oficial indicada.

Valide o registro local, sem rede:

```bash
python3 -m integrations.source_skill_contracts legislation < registro.json
```

`candidate_for_review` significa que o registro tem os campos mínimos. Não
significa que a URL responde, que o hash confere com o conteúdo remoto, que a
norma está vigente ou que a interpretação está correta.

## Consulta e registro

- Trabalhe com um ID ou URL por vez e preserve a resposta original.
- Diferencie status HTTP de existência da norma: 200 não prova vigência e 404
  não prova revogação.
- Diferencie proposição de norma: projeto, requerimento, parecer e emenda não
  são lei em vigor. Registre `proposal` e recuse afirmar eficácia.
- Não funda identificadores por número e ano; a mesma numeração pode existir
  em casas, esferas e anos diferentes.
- Preserve o texto original e registre qualquer limpeza, conversão ou
  normalização com antes/depois e motivo.
- Ao citar, use o dispositivo e a versão conferidos, não apenas o título da
  lei. Uma citação sem localizador é indicação de leitura, não prova.
- Marque `claim_current_validity: false`. Vigência exige análise jurídica
  própria, com fontes de alteração e revogação; o verificador nunca a certifica.

## Limites

- O catálogo do MCP é inicial e não exaustivo; ausência não significa
  inexistência da norma.
- O registro estrutural não autentica a fonte, não detecta revogação tácita,
  não resolve conflito de normas e não interpreta o caso concreto.
- Conversões automáticas e OCR podem omitir ou distorcer dispositivos.
- A publicação oficial e a análise por profissional habilitado prevalecem
  sobre este fluxo. Nenhum resultado aqui é parecer jurídico.
