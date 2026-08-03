---
spec_id: SPEC-935-R385
title: Scanners de imersão psicológica (indução, ritmo frenético, sensorialidade, manipulação narrativa) + correção MSTTR
component: scanners/psychological_immersion_scanners.py
status: verified
test_file: tests/test_r385_psychological_immersion_scanners.py
---

# SPEC-935-R385 — Scanners de Imersão Psicológica + Correção MSTTR

**Data:** 2026-08-03
**Motivação:** o usuário pediu revisão da obra Molambudos com diagnóstico
via scanners, avaliando se ela é "hipnótica, terror psicológico visceral
e frenético/dinâmico, imersiva, sensorial", usando "técnicas avançadas de
mentalismo e indução e manipulação psicológica através da narração",
sendo "disruptiva a nível literário". Reconhecimento prévio (agente
Explore) confirmou: os 8 scanners de `scanners/literary_scanners.py`
cobrem estrutura, personagem, estilo, símbolo, intertexto, resposta do
leitor, ética e inovação — mas **nenhum mede especificamente indução
hipnótica, dinâmica de ritmo (aceleração/desaceleração), densidade
sensorial detalhada ou técnicas de manipulação narrativa do leitor**. O
único artefato que promete isso (`literary-neurolinguistic-engineering-
phd.md`) é um prompt de persona para LLM, sem nenhum código por trás.
Em seguida, o usuário pediu explicitamente: "melhore os scanners e gere
outros para melhorar a qualidade de qualquer obra e do Molambudos".

## 1. Novo módulo: `scanners/psychological_immersion_scanners.py`

Segue exatamente o padrão de `LiteraryScannerBase` já estabelecido em
`scanners/literary_scanners.py` (mesmas funções auxiliares reaproveitadas
via import, mesmo contrato de saída: `score`/`grade`/`dimensions`/
`evidence`/`warnings`/`recommendations`/`overclaim_guard`). 4 scanners
novos:

1. **`HypnoticInductionScanner`** — repetição rítmica/anáfora (detecção de
   frases que reabrem com o mesmo bigrama ≥3x), pressuposição linguística
   ("você já sabe que...", "sem perceber"), comando incorporado (verbos
   imperativos dirigidos ao leitor: "sinta", "perceba", "respire"),
   ancoragem temporal (marcadores de presente contínuo/recorrência
   ritualizada: "agora", "3:14", "de novo").
2. **`FreneticPacingScanner`** — dinâmica de ritmo ao longo do texto (não
   só agregado): aceleração sentencial via médias móveis não sobrepostas
   (compara 1ª metade vs 2ª metade do comprimento médio de frase),
   fragmentação visceral (% de frases com ≤4 palavras — rajadas curtas),
   escalada de pontuação expressiva (! / ... / —), variância de
   comprimento de parágrafo (respiração dinâmica).
3. **`SensoryImmersionScanner`** — densidade multissensorial por 1000
   palavras, **interocepção corporal** (coração, pulso, respiração,
   náusea — núcleo do horror visceral, dimensão ausente do scanner
   `symbolic_imagery` original), **cruzamento sensorial** (% de frases
   que combinam ≥2 canais sensoriais na mesma unidade — proxy de
   imersão composta), amplitude de canais (de 6 possíveis: visual,
   sonoro, olfativo, tátil, gustativo, interoceptivo).
4. **`PsychologicalManipulationScanner`** — comando direto em 2ª pessoa
   no início de frase, cumplicidade/culpa atribuída ao leitor, **dupla
   vinculação** (enquadramento de impossibilidade de escape/reversão —
   ver correção de recall na Seção 3), quebra explícita da quarta
   parede (referências ao livro/página como objeto dentro da ficção).

Função de entrada: `run_psychological_immersion_scanner_suite(text,
metadata=None)`, mesmo formato de agregação e `overclaim_guard` do
módulo irmão — reforçando que contagem de marcadores **não prova**
efeito psicológico real, estado de transe ou manipulação efetiva sobre
pessoas reais (isso exige estudo empírico com leitores).

## 2. Correção metodológica: TTR global → MSTTR

`StyleVoiceScanner.riqueza_lexical` usava TTR (Type-Token Ratio) global
dividido por uma constante fixa (0.42) calibrada para textos curtos. Pela
lei de Heaps/Herdan, TTR bruto **cai estruturalmente** conforme o texto
cresce, mesmo com vocabulário rico e estável — penalizando injustamente
textos longos. Achado real: `molambudos.md` (~40 mil palavras) recebia
score 30.27 ("frágil") nessa dimensão apesar de nenhuma outra evidência de
pobreza vocabular.

Corrigido com **MSTTR (Mean Segmental Type-Token Ratio)**: TTR calculado
em janelas fixas (1000 palavras) e depois médio entre as janelas — métrica
padrão em linguística de corpus para comparar riqueza lexical entre
textos de tamanhos diferentes, pois não é sensível ao comprimento total.
Resultado sobre `molambudos.md`: score sobe de 30.27 para 100.0 (MSTTR
bruto = 0.423, essencialmente no valor de referência).

## 3. Achado e correção de recall durante a validação

Ao validar `PsychologicalManipulationScanner` contra `molambudos.md`, a
dimensão `dupla_vinculacao` deu **0** apesar de o texto conter, já
verificado por leitura direta (fragmento CONT-07): *"Não há tratamento.
Não há cura. Não há como fechar o livro e esquecer."* — dupla vinculação
textual inequívoca. Causa: a lista de frases exatas (`DOUBLE_BIND`) era
estreita demais para capturar variações do mesmo padrão. Corrigido com
regex complementar (`não há (?:tratamento|cura|escape|saída|jeito|volta|
como)`, `impossível (?:fechar|parar|escapar|voltar|esquecer)`) somado à
lista de frases originais. Resultado: 5 ocorrências reais capturadas
sobre `molambudos.md` (antes: 0).

## 4. Critérios de aceitação

1. 4 scanners novos seguem o contrato `LiteraryScannerBase` (score 0-100,
   `dimensions`, `evidence`, `warnings`, `recommendations`).
2. `run_psychological_immersion_scanner_suite` agrega os 4 e carrega
   `overclaim_guard` específico (efeito psicológico real requer estudo
   empírico).
3. Texto vazio retorna grade "insuficiente" sem exceção (mesmo padrão do
   módulo irmão).
4. `dupla_vinculacao` captura o padrão "não há {cura/tratamento/...}" via
   regex, não só frases exatas (regressão de recall corrigida antes do
   commit, não depois).
5. `riqueza_lexical` (MSTTR) não penaliza textos longos com vocabulário
   estável — verificado com texto sintético de 40 janelas e com
   `molambudos.md` real (score ≥70, sem warning de dimensão frágil).
6. Zero regressão em `tests/test_r267_literary_scanners.py` (8/8) — a
   suíte que já cobria `scanners/literary_scanners.py`.
7. 17 testes TDD novos (`tests/test_r385_psychological_immersion_scanners.py`).

## 5. Fora de escopo (documentado, não corrigido aqui)

A pendência de infraestrutura achada no reconhecimento (relatórios
R270-R276 movidos de `Molambudos_VictoriaRegia/relatorios/` para
`_archive/relatorios/`, quebrando 5 suítes de teste por `FileNotFoundError`)
não foi corrigida neste ciclo — é uma correção de caminho de arquivo, não
relacionada aos scanners em si, documentada para triagem futura.
