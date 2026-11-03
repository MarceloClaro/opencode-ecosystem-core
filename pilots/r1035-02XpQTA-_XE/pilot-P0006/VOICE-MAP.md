# Personagens, gênero, idade e vozes — P0006

Cada personagem tem **uma referência clonada** do original; a marcação de
gênero/idade é descritiva e vinculada ao hash da referência. O registro está
em `../voices/voices.json`; os perfis em `../voices/voice-profiles.json`;
o recibo em `voice-profiles-receipt.json`.

| Personagem | Gênero | Faixa | Perfil | Turnos | Referência | Hash (12) |
|---|---|---|---|---|---|---:|
| `char_male_a` | masculino | adulto / adulto jovem | `adult_male_01` | 4 | `references-clean/char_male_a.wav` | `0ac827341717` |
| `char_cagla` | feminino | adulto / adulto jovem | `adult_female_01` | 11 | `references-clean/char_cagla-compact.wav` | `58213f205e3f` |
| `char_ruya` | feminino | adulto / adulto jovem | `adult_female_02` | 5 | `references-clean/char_ruya.wav` | `1e09ae9a55ea` |
| `char_mother` | feminino | adulto / meia-idade | `adult_female_03` | 5 | `references-clean/char_mother.wav` | `957ef8aa8330` |

- `registry_sha256 = d49c9ba6a8ff71d822e1dd49b6ed1c05fecfad1dd7ea7afac3205a87b594ec90`.
- 25 turnos. O antigo “25/25” foi **retirado**: usava gate permissivo. A
  reauditoria R1041 encontrou 14 divergências lexicais e 4 overruns; montagem
  bloqueada até correção e escuta.
- Clonagem: XTTS v2 CPU; referências reconstruídas do stem vocal Demucs
  (Çağla em versão compacta). Nenhuma voz genérica foi usada.
- **Criança/idoso:** não há personagem criança ou idoso identificado neste
  piloto. O esquema aceita `crianca`, `adulto`, `idoso` e
  `nao_identificado`; um novo personagem exige referência própria e revisão.
- Gênero não é simulado por pitch artificial: o timbre vem da referência
  clonada; a marcação serve para distinguir e auditar.
- Regras: um personagem = uma referência; dois personagens não compartilham
  voz; dois locutores não apontam para o mesmo personagem sem fusão.
- `age_hint` e gênero são inferências visuais/dialogais, não biometria.
