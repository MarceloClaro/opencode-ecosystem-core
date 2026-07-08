# SPEC-910 — Polimento Literário de Molambudos

## Descrição
Aplicar as 5 recomendações da análise crítica para polir a obra *Molambudos — O Diário do Paciente 1.260*, preservando o núcleo forte (fome, vala, Colônia, contaminação narrativa) e eliminando redundâncias, inconsistências e excesso de explicação.

## Critérios de Aceitação

### P1 — Bíblia de Continuidade
- [ ] Criar `biblia-cronologica.md` no diretório do projeto com todos os marcos definitivos
- [ ] Resolver inconsistência: MEM-08 (1917) vs DOC-02 (1919) para chegada ao Colônia
- [ ] Resolver "64 anos" em CONT-01 — definir se é 64 anos da vala (1915-1979) ou erro
- [ ] Definir cadeia de transmissão completa: Paciente 1 → ... → 1.259 → 1.260 (Joaquim) → 1.261 (Oliveira) → 1.262 (Lúcia) → 1.263 (leitor)
- [ ] Verificar idades de Joaquim em cada homicídio (MEM-34): 1922 (~15), 1937 (~30), 1948 (~41)
- [ ] Corrigir anos conflitantes nos fragmentos

### P2 — Corte de Redundância nos CONT
- [ ] CONT-08 (Déjà Vu): temas duplicados com CONT-06 e CONT-09 — fundir ou cortar
- [ ] CONT-11 (Número 1260): duplicado com CONT-15 — fundir ou cortar
- [ ] CONT-12 (3:14/Relógio): duplicado com CONT-04 — reduzir a 1/3 ou cortar
- [ ] CONT-13 (A Fila): duplicado com CONT-07 (ciclo) — cortar
- [ ] CONT-14 (Dia Seguinte): redundante com CONT-07 e CONT-19 — cortar
- [ ] CONT-15 (Coincidência): duplicado com CONT-11 — fundir ou cortar
- [ ] CONT-16 (Último Teste): redundante com CONT-07 — cortar
- [ ] CONT-17 (Sétima Noite): duplicado com CONT-04 e CONT-12 — cortar
- [ ] CONT-19 (Silêncio Depois): redundante com CONT-07 — cortar
- [ ] CONT-20 (Carta): repete "você é o próximo" — cortar
- [ ] CONT-21 (Diagnóstico Final): título conflita com CONT-07 — fundir conteúdo em CONT-07 ou cortar
- [ ] CONT-22 (Teste do Leitor): duplicado com CONT-08 — cortar
- [ ] CONT-18 (Livro Físico): manter (único meta-texto sobre suporte físico)
- [ ] CONT-24 (Nota do Arquivista): manter (voz diferenciada)
- [ ] CONT-25 (Pergunta Final): manter (fechamento filosófico)

### P3 — Diferenciação de Vozes
- [ ] **Joaquim (MEM)**: voz seca, sensorial, oral, frases curtas, léxico do sertão. Já OK.
- [ ] **Oliveira (DOC)**: evolução de clínico formal → deteriorado. Reforçar contraste.
- [ ] **Lúcia (LUC)**: voz analítica, forense, cita CID/DSM, mantém distanciamento profissional mesmo quando se deteriora
- [ ] **Documentos (DOC)**: frios, burocráticos, sem emoção — o horror está no contraste entre forma fria e conteúdo absurdo
- [ ] **CONT**: invasivo mas cirúrgico — reduzir tom explicativo ("você está contaminado porque...") e aumentar sugestão

### P4 — Criatura: Menos Explicação, Mais Presença
- [ ] CONT-03: cortar parágrafos que explicam mecanismo psicológico ("para o corpo, imaginar é sentir...")
- [ ] CONT-05: cortar parágrafos que explicam por que o diagnóstico se aplica ("a reatividade é a prova...")
- [ ] CONT-06: cortar explicação de criptomnésia; deixar só a experiência
- [ ] CONT-07: cortar seções II e III (revisão de critérios e revelação já implícita)
- [ ] MEM-15: criatura fala demais — cortar explicações ("sou um acúmulo... a terra fermenta")
- [ ] Em geral: substituir "A criatura é X" por mostração sensorial

### P5 — Lúcia Investigadora
- [ ] LUC-05: reduzir sonho passivo; adicionar ação de Lúcia cruzando dados
- [ ] LUC-07 (O Rastro de Oliveira): expandir com investigação concreta — registros, telefonemas, confronto com fontes
- [ ] LUC-08: fortalecer cena da consulta psiquiátrica — Lúcia deve argumentar clinicamente contra o diagnóstico de Regina
- [ ] LUC-10: transformar em laudo verdadeiramente forense (não só relato de sintomas, mas análise de padrão)
- [ ] LUC-13: expandir dossiê com evidências concretas (datas, fotos, documentos)

### Critérios de Verificação
- [ ] Nenhum fragmento perde sua identidade temática
- [ ] O ciclo de contaminação permanece intacto (narrativamente)
- [ ] Nenhum Overfull hbox ou erro LaTeX após as edições
- [ ] A obra reduz em pelo menos 5% o número de palavras dos CONTs
- [ ] Lúcia tem pelo menos 2 momentos de investigação ativa (não apenas reação)
- [ ] A criatura é mencionada 30% menos em termos conceituais ("a criatura é...", "ela representa...")

## Roteiro de Execução

1. Criar bíblia de continuidade
2. Editar CONT fragments (cortar redundâncias)
3. Editar LUC fragments (fortalecer Lúcia)
4. Editar MEM/DOC (vozes, criatura)
5. Atualizar manifest.json se necessário
6. Re-compilar LaTeX
7. Verificar resultado (scanner, páginas, erros)
