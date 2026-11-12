---
name: reap-prompts
description: Roteador da biblioteca REA-Prompts (REAP) para investigações de engenharia reversa com o REA. Use quando a tarefa pedir uma receita de investigação por alvo — feature tracing, binário nativo, Electron/JavaScript, Android, firmware, kernel, malware, deobfuscação, Go/Rust, clonagem comportamental ou comparação de versões. Carregue o pack correspondente em references/packs/ sob demanda; não é a skill de ferramentas (essa é reverse-engineer-anything).
metadata:
  version: "1"
  source: "https://github.com/joasasantos/rea-prompts"
  fork: "https://github.com/MarceloClaro/REA-Prompts"
  license: "MIT"
  packs: 26
---

# REAP — roteador de receitas para o REA

Esta skill é um **índice**. Ela não executa o alvo, não instala o REA e não
substitui a skill oficial `reverse-engineer-anything`. O papel dela é escolher
a receita certa e carregar o pack sob demanda.

## Como usar

1. **Classifique o alvo** (binário, Electron/JS, Android, firmware, kernel,
   malware, Go/Rust, web, jogo, clone comportamental).
2. **Escolha um pack** na tabela abaixo. Uma investigação = uma feature.
3. **Leia** `references/packs/<pack>.md` e adapte o template, substituindo
   `<angle brackets>` por valores concretos.
4. **Aplique o contrato de evidência**: cada conclusão cita arquivo, função,
   endereço ou trecho; fatos, inferências e lacunas ficam separados.
5. **Estático primeiro**: não execute o alvo até que a observação de runtime
   seja necessária e autorizada.
6. **Termine com um entregável**: SPEC.md, leitor, plano de port, harness de
   equivalência ou relatório de lacunas.

## Packs

| Pack | Tema | Risco |
|---|---|---|
| `reap-00-install-and-verify` | instalação e verificação | baixo |
| `reap-01-getting-started` | primeiros passos | baixo |
| `reap-02-feature-tracing-any-program` | rastreio de uma feature | baixo |
| `reap-03-native-binary-exploration` | binário nativo | baixo |
| `reap-04-software-and-feature-cloning` | clonagem clean-room | médio |
| `reap-05-games` | jogos | médio |
| `reap-06-game-portability-to-wasm` | port para WASM | médio |
| `reap-07-firmware-and-embedded` | firmware e embarcados | médio |
| `reap-08-android` | Android/APK | médio |
| `reap-09-kernel-analysis` | análise de kernel | alto |
| `reap-10-vulnerability-research` | pesquisa de vulnerabilidade | alto |
| `reap-11-electron-and-javascript` | Electron e JavaScript | médio |
| `reap-12-anti-cheat-and-protection-research` | anti-cheat | alto |
| `reap-13-dma-and-hardware-assisted-cheat-research-defensive` | DMA defensivo | alto |
| `reap-14-software-cracking-research` | cracking/CTF | alto |
| `reap-15-version-comparison-and-crash-work` | comparação de versões | baixo |
| `reap-16-long-running-investigations` | investigação longa | baixo |
| `reap-17-malware-analysis` | malware | alto |
| `reap-18-advanced-binary-exploration-and-deobfuscation` | deobfuscação | alto |
| `reap-19-kernel-and-driver-exploitation-research` | exploração de kernel | alto |
| `reap-20-advanced-software-cloning-and-feature-reconstruction` | clonagem avançada | médio |
| `reap-21-protector-and-obfuscator-research` | protetores/obfuscadores | alto |
| `reap-22-go-and-rust-binary-source-recovery` | Go/Rust | baixo |
| `reap-prompts` | índice original | baixo |
| `reap-wildcard` | prompt coringa | baixo |
| `reap-prompt-writing-tips` | disciplina de prompt | baixo |

## Política

- **Alvo autorizado**: apenas software próprio, laboratório, CTF, bug bounty,
  teste de interoperabilidade ou pesquisa acadêmica autorizada.
- **Packs de risco alto** (`kernel`, `vulnerabilidade`, `anti-cheat`, `DMA`,
  `cracking`, `malware`, `deobfuscação`, `exploração`, `protetores`) exigem
  autorização explícita e alvo local/isolado.
- **Nunca** executar malware, atacar sessão de terceiros, contornar proteção de
  produto alheio ou produzir bypass weaponizado.
- **Nunca** apresentar inferência como fato. Use os três baldes:
  confirmado / inferido / lacuna.
- **Nunca** tratar instalação de skill ou registro de ferramenta como prova de
  execução ou de validação externa.

## Proveniência

- Fonte original: `joasasantos/rea-prompts` (MIT, © 2025 Joas Antonio dos Santos).
- Fork analisado: `MarceloClaro/REA-Prompts`, commit
  `9756618f25af1920c8965f8969820eed22247936`.
- Pacotes copiados em `references/packs/` com hashes em `.reap-manifest.json`.
- O REA e sua skill oficial pertencem a `morluto/rea`; esta skill apenas
  referencia receitas.
