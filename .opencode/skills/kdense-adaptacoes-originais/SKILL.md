---
name: kdense-adaptacoes-originais
description: Oferece nove adaptações originais para as skills K-Dense em license_hold,
  cobrindo conectores biológicos, filogenia, glicobiologia, cenários, transcriptômica
  espacial, modelos metabólicos, grafo de medicina de precisão e química em nuvem.
  Use apenas com dependências e termos verificados; não copia texto, código ou scripts
  restritos.
metadata:
  round: R1049
  source: https://github.com/K-Dense-AI/scientific-agent-skills
  license: MIT
  adaptation: Texto original do Core, escrito a partir de metadados públicos e conhecimento
    de domínio; não é derivado do texto restrito.
---

# Adaptações originais para license_hold

Estas nove notas são **originais do Core**. Elas não copiam o `SKILL.md`
restrito, não reproduzem scripts e não mudam a licença do original. Cada nota
descreve um protocolo mínimo, dependências externas e gates.

| Adaptação | Substitui a referência restrita | Licença original |
|---|---|---|
| Conectores biológicos | bioservices | GPLv3 |
| Árvores e taxonomia | etetoolkit | GPL-3.0-or-later |
| Glicobiologia | glycoengineering | desconhecida |
| Filogenia | phylogenetics | desconhecida |
| Cenários contrafactuais | what-if-oracle | CC BY-NC-SA |
| Transcriptômica espacial | deepspot-m | PolyForm-NC |
| Modelos metabólicos | cobrapy | GPL-2.0 |
| Grafo de medicina de precisão | primekg | desconhecida |
| Química em nuvem | rowan | proprietária |

## Regras

- Leia os termos do original antes de instalar/usar.
- Nenhuma dependência é instalada por esta skill.
- Nenhum código de terceiro é executado.
- Dados sensíveis, clínicos ou proprietários exigem autorização e destino nomeado.
- Predição não é medição; associação não é causalidade; árvore não é verdade.
- Toda saída exige revisão humana e provenance.

## Uso

Abra a referência específica, confirme dependências/licença e execute o passo
com o operador. O Core não chama API, não baixa modelo e não publica.
