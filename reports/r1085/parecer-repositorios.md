# R1085 — Triagem de três repositórios para o Core e seus áudios

**Escopo:** documentação pública e código do Core lidos em 2026-11-06;
**não instalado**, **não executado** nenhum dos três projetos. Não foi feita
inferência de áudio nem avaliação auditiva. Revisões HEAD consultadas por
`git ls-remote` abaixo; README/Licença são declarações dos autores, não auditoria
das dependências, segurança de endpoints ou garantia de compatibilidade.

| Projeto e revisão | Ganho potencial | Sobreposição/risco e decisão |
|---|---|---|
| [`digitalsamba/claude-code-video-toolkit`](https://github.com/digitalsamba/claude-code-video-toolkit/tree/f95c82c0062bcfe351108bcf13087e26ba33338c), MIT | Planejamento de cenas, identidade de marca, revisão de cenas/contato visual, narração Qwen3-TTS/ElevenLabs, música e comandos de render. | O Core já tem FFmpeg, adaptação Remotion, direção/QA de vídeo e pipeline de dublagem. Não importar projeto, instalador, hooks ou comandos de upload. A arquitetura Claude/Node 22+, `uv`, provedores de GPU/nuvem e YouTube tem custo, credenciais, licenças transitivas e risco de publicação involuntária. **Referência seletiva para um checklist de revisão por cena; não é melhoria auditiva comprovada.** |
| [`travisvn/chatterbox-tts-api`](https://github.com/travisvn/chatterbox-tts-api/tree/a5f466128e4baa8e4cceb3bba9b7ca9de6f7ec6b), **AGPL-3.0** para o servidor | API FastAPI com **alguns** endpoints TTS no formato OpenAI (não equivalência de todas as opções/formatos), biblioteca de vozes, divisão de texto, streaming e idioma `pt` declarados. Ponto de integração opcional para um ensaio A/B, se tecnicamente viável. | O Core já integra XTTS, cache por unidade/hash, gate de consentimento e registro global de vozes; Chatterbox está apenas **candidato**. A API AGPL não herda a licença MIT do **código ResembleAI/chatterbox**; pesos e dependências exigem conferência própria. Um serviço modificado exposto em rede requer revisão das obrigações AGPL. Vozes armazenadas e endpoint de upload exigem isolamento e controle de acesso. O README do servidor alerta que o multilíngue pode falhar sem CUDA; afirma 22 idiomas na lista, mas 23 na configuração: não inferir suporte/qualidade **pt-BR** do rótulo `pt`. **Piloto isolado condicionado, sem adoção agora.** |
| [`assafkip/claudemy`](https://github.com/assafkip/claudemy/tree/dadf948aafb90d66b554a13df1e47f2509cc1c70), MIT | Formato didático de pílulas de áudio com cartões, contrapontos, links de fonte, uma ação prática e amostra revisada antes do lote. | É fluxo de cursos com Claude Code + busca web, `beautifulsoup4`, FFmpeg e ElevenLabs (envia roteiro ao serviço); fallback de voz é `say` do **macOS**, sem opção Linux comprovada no README. Não é motor TTS para romance, nem substitui podcast literário. **Reaproveitar só a ideia de amostra + trilha de fontes em eventual produção educacional, sem integrar o plugin.** |

## Baseline e proposta de ensaio separado

O catálogo [`integrations/video_toolchain.py`](../../integrations/video_toolchain.py)
registra XTTS-v2 integrado (modelo sujeito aos termos CPML, não assumir uso
comercial), Chatterbox candidato, FFmpeg e Remotion. `integrations/dubbing_xtts.py`
executa o motor XTTS; `integrations/dubbing_synth.py` usa hash/cache e marca
`tts_generated_pending_review`; `integrations/video_voice_registry.py` exige
declaração de **consentimento** por voz/personagem. Essas garantias locais não
fazem controle de acesso automaticamente em um serviço externo.

Se autorizado posteriormente, ensaio offline com texto **não confidencial** em
PT-BR e referências de voz cujo consentimento para síntese/teste esteja
documentado: mesmo roteiro e locutor, baseline XTTS versus candidato Chatterbox
isolado (versão do modelo e do servidor fixadas), amostras curtas hashadas e
sem upload público, revisão de inteligibilidade, pronúncia, continuidade,
artefatos, latência e custo, **revisão auditiva humana** cega à ferramenta.
Rejeitar saída com troca de personagem, ruído, clipping ou não conformidade
de licença/consentimento. Sem métrica ou preferência ouvida não se pode afirmar
que algum projeto melhora os áudios; nada substitui a edição canônica.

## Fontes e limites

- Toolkit: [README na revisão](https://github.com/digitalsamba/claude-code-video-toolkit/blob/f95c82c0062bcfe351108bcf13087e26ba33338c/README.md), [licença](https://github.com/digitalsamba/claude-code-video-toolkit/blob/f95c82c0062bcfe351108bcf13087e26ba33338c/LICENSE).
- API Chatterbox: [README na revisão](https://github.com/travisvn/chatterbox-tts-api/blob/a5f466128e4baa8e4cceb3bba9b7ca9de6f7ec6b/README.md), [licença](https://github.com/travisvn/chatterbox-tts-api/blob/a5f466128e4baa8e4cceb3bba9b7ca9de6f7ec6b/LICENSE). Modelo distinto: [ResembleAI/chatterbox](https://github.com/resemble-ai/chatterbox) e [documentação de `ChatterboxMultilingualTTS.generate`](https://github.com/resemble-ai/chatterbox/blob/master/_autodocs/api-reference/chatterbox-multilingual-tts.md). A documentação do modelo lista pacote brasileiro específico, mas **não** demonstra que a API avaliada o utiliza.
- Claudemy: [README na revisão](https://github.com/assafkip/claudemy/blob/dadf948aafb90d66b554a13df1e47f2509cc1c70/README.md), [licença](https://github.com/assafkip/claudemy/blob/dadf948aafb90d66b554a13df1e47f2509cc1c70/LICENSE).
- Fonte local adicional: [`reports/r1043/toolchain.json`](../r1043/toolchain.json), `integrations/dubbing_synth.py`, `integrations/video_voice_registry.py`. Não se examinou o código integral ou a árvore de dependências dos três projetos; suas alegações de latência/qualidade não foram reproduzidas.
