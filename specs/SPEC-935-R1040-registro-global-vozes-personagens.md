---
spec_id: SPEC-935-R1040
title: Registro global de vozes e consistência de personagem
component: integrations.video_voice_registry
status: implemented
test_file: tests/test_r1040_video_voice_registry.py
depends_on:
  - SPEC-935-R1038
---

# SPEC-935-R1040

## Objetivo

Impedir que o mesmo personagem receba duas vozes diferentes e que dois
personagens recebam a mesma referência por acidente. Cada fala aponta para um
`character_id` global; o TTS resolve a voz **somente** pelo registro global.

## Regras

- O registro tem personagens com `reference`, `sha256`, `consent_declared`,
  `engine`, `display_hint` e `identity_verified`.
- Referência precisa existir, ser arquivo regular e ter SHA-256 conferido.
  Consentimento é declaração do usuário; documentos não são verificados.
- Dois personagens não podem compartilhar a mesma referência/hash. Se forem a
  mesma pessoa, devem ser o mesmo `character_id`; se forem pessoas diferentes,
  precisam de referências distintas.
- O mapa da parte associa cada locutor local (`spk1`, `spk2`, ...) a exatamente
  um personagem global. Dois locutores locais não podem apontar para o mesmo
  personagem: isso exige fusão/revisão, não duas vozes.
- Toda fala precisa de `speaker` mapeado; `character_id` explícito, se houver,
  precisa concordar com o mapa. Personagem desconhecido bloqueia o TTS.
- O recibo vincula hash do registro, do mapa e do diálogo. Não é aprovação
  humana, identidade biométrica ou autorização jurídica.
- Personagem novo ou locutor não mapeado bloqueia a dublagem daquela parte.

## Aceites

Testes antes do código: registro válido; referência ausente; hash divergente;
consentimento ausente; duas referências iguais; personagem desconhecido; dois
locutores para o mesmo personagem; fala com locutor desconhecido; múltiplas
falas do mesmo personagem usando uma única referência; recibo muda com o
registro; CLI sem sobrescrita. Fixtures são sintéticas.

## Limites

O registro garante consistência de **referência**, não identidade real do
personagem. Nomes são pistas; a revisão humana decide se dois clusters são a
mesma pessoa. Clonagem continua dependendo de referência limpa e do XTTS;
qualidade vocal e sincronia não são certificadas por este gate.

## Estado implementado

`integrations/video_voice_registry.py` implementa o registro, o mapa local,
o gate de diálogo e o recibo com hashes. Dez testes R1040 passam.

O piloto foi marcado com quatro personagens globais:

- `char_male_a` — 4 falas; referência limpa do clube;
- `char_cagla` — 11 falas;
- `char_ruya` — 5 falas;
- `char_mother` — 6 falas.

`pilot-P0006/voice-receipt.json` confirma uma referência única por personagem,
com `registry_sha256 = 214d4c87…52bd`. O mesmo personagem reutiliza o mesmo
hash em todas as falas. Personagens novos ou locutores não mapeados bloqueiam
o TTS da parte; não há criação automática de segunda voz para o mesmo papel.

