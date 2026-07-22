# SPEC-917 — Molambudos Fase 1E: terror visceral/frenético e modulação de ecos

## Objetivo
Executar uma passada estilística cirúrgica nos fragmentos narrativos mais saturados por ecos de `criatura`, `cheiro`, `vala`, `fome`, `ciclo`, `olho amarelo` e fórmulas como `disse a criatura` / `a criatura dentro de mim`, preservando e intensificando o terror visceral e frenético da obra.

## Diretriz criativa
A obra é destinada a leitores maiores de 18 anos. A revisão pode manter imagens perturbadoras, corporais, sensoriais e claustrofóbicas, desde que sirvam à experiência literária. A “manipulação psicológica” deve ser empregada exclusivamente como técnica narrativa ficcional — por exemplo: falsa segurança, narrador instável, repetição quebrada, lacunas, contradições, ritmo de perseguição, intrusão sensorial e captura de atenção por suspense — nunca como instrução prática para manipular pessoas reais.

## Escopo
- Projeto: `projetos/molambudos/Molambudos_VictoriaRegia`.
- Alvos a localizar por busca textual:
  - `a criatura dentro de mim`;
  - `disse a criatura`;
  - `cala a boca`;
  - ocorrências concentradas de `cheiro adocicado`, `olho amarelo`, `ciclo` e `vala`.
- Reescrever apenas os trechos em que a repetição pareça mecânica ou explicativa.
- Preservar os links finais de todos os fragmentos alterados.

## Técnicas literárias permitidas nesta fase
1. **Falsa segurança:** abrir um parágrafo como se o perigo tivesse cessado e quebrar a segurança no mesmo bloco.
2. **Ancoragem sensorial:** substituir explicação por resposta corporal — saliva, dente, garganta, pele, ruído, calor, pressão.
3. **Repetição quebrada:** manter refrão quando necessário, mas interrompê-lo antes do esperado ou deslocá-lo para outro sujeito.
4. **Lacuna sugestiva:** deixar que o leitor complete o horror por ausência documental, frase cortada ou gesto incompleto.
5. **Ritmo frenético controlado:** alternar frases curtas, cortes bruscos e parágrafos comprimidos sem comprometer legibilidade.
6. **Dissonância clínica/narrativa:** contrastar linguagem burocrática com consequência visceral.

## Critérios de aceitação
1. Reduzir ocorrências mecânicas das fórmulas `a criatura dentro de mim` e `disse a criatura` em trechos narrativos.
2. Preservar a sensação de perseguição, fome e contaminação, aumentando a variação sensorial.
3. Não transformar a obra em manual de manipulação real; toda técnica deve permanecer claramente literária/ficcional.
4. Não suavizar o horror a ponto de perder a classificação adulta pretendida.
5. Não introduzir violência sexual explícita ou erotização de sofrimento.
6. Links finais preservados.
7. Criar relatório da Fase 1E com arquivos alterados, técnicas aplicadas e métricas finais.
8. PDF deve compilar em duas passagens sem erro fatal, sem destinos duplicados, sem font warnings e sem regressão de `overfull hbox`.

## Verificação
- Busca antes/depois das fórmulas-alvo.
- Leitura manual dos fragmentos alterados.
- Revisão linguística por agente corretor.
- Compilação dupla: `pdflatex -interaction=nonstopmode main.tex`.
- Contagem em `main.log`: `LaTeX Error`, `Fatal error`, `Overfull \hbox`, `Overfull \vbox`, `destination with the same identifier`, `Font Warning`.
