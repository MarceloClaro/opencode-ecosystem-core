# Backup do OpenCode Ecosystem Core — R1045

Data: 2026-11-03. Este repositório é o backup **versionado** de código,
documentação, specs, testes, skills e recibos leves. Mídia pesada, modelos,
biblioteca local e repositórios aninhados ficam fora do Git de propósito.

## O que está no Git

- código em `integrations/`, `marceloclaro/`, `mci/`, `sdd/`, `scanners/`,
  `academic/`, `agents/`, `.opencode/`;
- specs, testes e recibos;
- README, ARCHITECTURE, MANUAL, docs, PROGRESS e STATUS;
- skills `.claude/` e `.opencode/skills/`;
- instalador one-click `install.sh` e `installer/oneclick/`;
- relatórios leves de R1033–R1045 (sem mídia).

## O que está fora do Git

| Caminho | Tamanho aprox. | Motivo |
|---|---:|---|
| `pilots/` | 8,2 GB | vídeo fonte, partes, stems, TTS, renders |
| `Panoramica_AI_OdontoCA_2_0_SDD_TDD_CASE117/` | 7,7 GB | projeto local com mídia/modelos |
| `editor-workspace/` | 472 MB | `node_modules`, renders, projetos locais |
| `biblioteca ai/` | 108 MB | PDFs e material local de estudo |
| `~/.cache/opencode-pilot/` | — | venvs, modelos XTTS/Whisper/M2M/Nemotron |

O manifesto de tamanhos está em
`reports/r1045/backup-manifest.json`.

## Restaurar

```bash
git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git
cd opencode-ecosystem-core
git checkout backup-r1045-2026-11-03
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./install.sh --check
.venv/bin/python -m marceloclaro.cli doctor
```

A mídia do episódio não é reconstruída pelo Git. Preserve `pilots/` e
`~/.cache/opencode-pilot/` separadamente; os manifests e hashes locais
identificam os arquivos.

## Segurança

- Nenhuma chave, cookie ou token foi incluído no commit.
- `opencode.json` usa referências `{env:...}`; segredos ficam no ambiente.
- O commit exclui repositórios aninhados (`AO/`,
  `opencode-ecosystem-core/`) e artefatos acidentais.
- Testes verdes e `doctor` 22/22 são estruturais; não certificam mídia,
  autenticação ou qualidade editorial.

## Estado

O backup preserva a **infraestrutura** de vídeo/dublagem, não uma dublagem
final. No momento do snapshot: 107 partes preparadas, 106 com OCR, 107
diarizadas, ASR large-v3 em execução, TTS 0, mix 0, montagem 0 e publicação 0.
Ver `pilots/r1035-02XpQTA-_XE/STATUS.md`.
