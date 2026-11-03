---
name: superpowers-sdd-tdd
description: Aplique SDD/TDD com planos pequenos, debugging sistemático, revisão e
  verificação antes de concluir. Use quando a tarefa exigir implementação disciplinada;
  não copia o framework Superpowers, não instala hooks e não substitui o runner de
  testes do projeto.
metadata:
  round: R1049
  source: https://github.com/obra/superpowers
  license: MIT
  adaptation: Adaptação textual original do Core inspirada no método Superpowers (obra/superpowers,
    commit 22f0b463e7a5e579904dd6211a520321035526f7); nenhum código foi copiado.
---

# Superpowers SDD/TDD — adaptação seletiva

## Princípio

Nenhuma implementação começa sem uma especificação verificável. O ciclo é
**RED → GREEN → REFACTOR**, e a conclusão exige evidência, não entusiasmo.

Esta skill adapta o *método* do Superpowers (MIT), sem copiar seu código,
hooks, marketplace ou instalador. O dono do ciclo continua sendo o orquestrador
do Core.

## Fluxo

1. **Especificar** — objetivo, entradas, saídas, critérios de aceitação,
   limites e o que não será feito.
2. **RED** — escrever um teste que falha pelo motivo correto; registrar a
   saída. Teste que passa de primeira não prova a mudança.
3. **GREEN** — implementação mínima para o teste passar; sem refatoração
   criativa ainda.
4. **REFACTOR** — melhorar nomes, duplicação e acoplamento com testes verdes.
5. **REVISAR** — procurar regressões, caminhos de erro, segurança, permissões e
   dependências novas.
6. **VERIFICAR** — rodar o teste focal, a regressão relevante, o diagnóstico e
   conferir o diff. "Feito" só existe com saída observada.
7. **REGISTRAR** — hashes, comandos, limitações e lições no MetaBus/Evolution.

## Planos pequenos

- Uma tarefa deve caber em uma sessão e produzir um artefato verificável.
- Cada tarefa declara arquivos, testes, dependências e critério de parada.
- Não misture refatoração ampla com correção urgente.
- Se o plano tiver mais de 7 passos, divida antes de executar.
- Não peça a outro agente para "resolver tudo"; dê contexto, contrato e saída.

## Debugging sistemático

1. Reproduza o menor caso.
2. Reduza a causa por bissecção, logs e hipóteses rivais.
3. Corrija a causa, não o sintoma.
4. Adicione um teste que falharia antes da correção.
5. Verifique se a correção não criou outro caminho quebrado.

## Verificação antes de concluir

- O teste novo falhou antes? Há registro?
- O teste novo passa agora?
- A regressão relevante passa?
- O diff contém apenas o escopo autorizado?
- Há dependência, permissão ou mídia não declarada?
- O que continua não verificado?

## Limites

- Testes não provam qualidade estética, científica ou editorial.
- A skill não instala o framework original nem ativa hooks.
- Não use subagentes para contornar revisão, orçamento ou permissões.
- Não declare "superpowers" ou "super-humano": é um método, não uma garantia.
