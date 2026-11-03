# Registro de descobertas

## Formato

Cada descoberta deve ter:

- **título numerado**;
- **Evidência**: comando, arquivo, hash, frame ou medida;
- **Impacto**: o que muda na produção;
- **Decisão**: o que foi adotado;
- **Limite**: o que não foi provado.

## Exemplo

```markdown
## 1. Wav2Lip em 1080p estoura memória

**Evidência:** RSS 7.128.024 KB no bloco 0; watchdog abortou em 4,5 GB.
**Impacto:** 1080p não é viável neste host; 640×360 é estável.
**Decisão:** reduzir a fonte e sobrepor só o rosto ao original.
**Limite:** qualidade facial continua limitada; não é broadcast.
```

## Metacognição

- Registre no `DISCOVERIES.md` do projeto.
- Publique reflexões no MetaBus com escopo e confiança.
- Registre o ciclo no EvolutionRegistry com lições.
- Diferencie observação local de validação externa.
- Não promova confiança por um sucesso isolado.

## Anti-overclaim

Metadados, frames e níveis de áudio provam presença e formato. Não provam
sincronia labial, inteligibilidade, naturalidade da voz ou qualidade editorial.
Esses pontos exigem reprodução com áudio, escuta e revisão humana.
