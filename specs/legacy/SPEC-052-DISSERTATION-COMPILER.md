# SPEC-052: Autonomous Academic Production Pipeline v1.0
## Spec-Driven Development (SDD) + Test-Driven Development (TDD)

**Status:** ACTIVE
**Created:** 2026-06-24
**Author:** Marcelo Claro (Orchestrator) + OpenCode Ecosystem
**Cycle:** R27 (Post-Dissertation Autoevolution)

---

## 1. VISÃO GERAL

Pipeline autônomo para produção acadêmica completa:
**Tema → Outline → Capítulos LaTeX → PDF → Áudio MP3 → DOCX**

### 1.1 Contexto
O ciclo R26 (dissertação "Metodologias Ativas") revelou 7 gargalos manuais:
1. Escrita capítulo-a-capítulo (5 arquivos .tex)
2. Gerenciamento de citações (51 entradas .bib)
3. Compilação LaTeX com erros de encoding
4. Scanner anti-AI com thresholds inadequados
5. Conversão áudio (edge-tts + chunking + concatenação)
6. Conversão DOCX (pandoc + citeproc + APA CSL)
7. Validação final (0 undefined refs, 0 errors)

### 1.2 Objetivo
Automatizar 90% do pipeline, mantendo qualidade Qualis A1 (≥85/100).

---

## 2. ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-052: AAPP v1.0                          │
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │ OUTLINE_   │   │ CHAPTER_   │   │ COMPILE_   │              │
│  │ ANALYZER   │──▶│ WRITER     │──▶│ ENGINE     │              │
│  │ (Phase 1)  │   │ (Phase 2)  │   │ (Phase 3)  │              │
│  └────────────┘   └────────────┘   └────────────┘              │
│        │                │                │                       │
│        ▼                ▼                ▼                       │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │ OUTPUT_    │   │ QUALITY_   │   │ META_      │              │
│  │ PACKAGER   │◀──│ GATE       │◀──│ COGNITIVE  │              │
│  │ (Phase 4)  │   │ (Phase 5)  │   │ (Loop)     │              │
│  └────────────┘   └────────────┘   └────────────┘              │
│        │                │                │                       │
│        ▼                ▼                ▼                       │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │ PDF        │   │ Anti-AI    │   │ Anomaly    │              │
│  │ Audio MP3  │   │ Anti-Plag  │   │ Detection  │              │
│  │ DOCX       │   │ Score ≥85  │   │ Auto-Fix   │              │
│  └────────────┘   └────────────┘   └────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPONENTES

### 3.1 DissertationCompiler (dissertation_compiler.py)
**Responsabilidade:** Orquestrar pipeline completo de compilação.

**Classes:**
- `LaTeXCompiler` — pdflatex → biber → pdflatex → pdflatex
- `AudioGenerator` — PDF → texto → edge-tts → MP3
- `DOCXConverter` — LaTeX → pandoc → DOCX
- `DissertationCompiler` — Orquestrador principal

**Interfaces:**
```python
class DissertationCompiler:
    def __init__(self, input_path: Path, formats: list[str])
    def run(self) -> list[CompileResult]

class LaTeXCompiler:
    def compile(self, tex_file: Path, timeout: int = 300) -> CompileResult

class AudioGenerator:
    async def generate(self, pdf_path: Path, output_dir: Path) -> CompileResult

class DOCXConverter:
    def convert(self, tex_file: Path, bib_file: Optional[Path]) -> CompileResult
```

### 3.2 DissertationGenerator (SKILL.md)
**Responsabilidade:** Gerar conteúdo acadêmico a partir de outline.

**Fases:**
1. OUTLINE_ANALYSIS — Estrutura + escopo + fontes
2. CHAPTER_WRITING — LaTeX + BibTeX + figuras
3. COMPILE_ENGINE — pdflatex + biber
4. OUTPUT_PACKAGER — PDF + áudio + DOCX
5. QUALITY_GATE — Anti-AI + anti-plágio + score

### 3.3 MetacognitiveLoop (metacognitive_loop.py)
**Responsabilidade:** Auto-observação e auto-correção.

**Componentes:**
- `ExecutionTrace` — Registro imutável de cada execução
- `AnomalyDetector` — Detecta padrões anômalos
- `ConfidenceEstimator` — Estima confiança por dimensão
- `CorrectionEngine` — Dispara correções automáticas

---

## 4. CASOS DE TESTE (CTs)

### CT-052.01: LaTeXCompiler initialization
**Dado:** Caminhos pdflatex e biber
**Quando:** LaTeXCompiler é instanciado
**Então:** Executáveis são encontrados

### CT-052.02: LaTeXCompiler._find_executable
**Dado:** Nome de executável "pdflatex"
**Quando:** _find_executable é chamado
**Então:** Caminho válido é retornado

### CT-052.03: LaTeXCompiler.compile success
**Dado:** Arquivo .tex válido com \documentclass{article}
**Quando:** compile é chamado
**Então:** CompileResult.success == True e PDF existe

### CT-052.04: LaTeXCompiler.compile failure
**Dado:** Arquivo .tex com erro de sintaxe
**Quando:** compile é chamado
**Então:** CompileResult.success == False

### CT-052.05: AudioGenerator initialization
**Dado:** Voz "pt-BR-FranciscaNeural" e rate "-5%"
**Quando:** AudioGenerator é instanciado
**Então:** voice e rate estão configurados

### CT-052.06: AudioGenerator._clean_text
**Dado:** Texto com URLs, emails, page numbers
**Quando:** _clean_text é chamado
**Então:** URLs removidas, emails removidos, page numbers removidos

### CT-052.07: AudioGenerator._split_chunks
**Dado:** Texto de 10.000 caracteres
**Quando:** _split_chunks é chamado com max_chars=3500
**Então:** 3-4 chunks gerados, cada um ≤ 3500 chars

### CT-052.08: AudioGenerator._split_chunks respects sentences
**Dado:** Texto com frases terminadas em ponto
**Quando:** _split_chunks é chamado
**Então:** Nenhum chunk corta frase ao meio

### CT-052.09: AudioGenerator.generate (mock)
**Dado:** PDF mock com texto extraído
**Quando:** generate é chamado
**Então:** CompileResult.success == True e MP3 existe

### CT-052.10: DOCXConverter initialization
**Dado:** pandoc instalado
**Quando:** DOCXConverter é instanciado
**Então:** pandoc path encontrado

### CT-052.11: DOCXConverter.convert
**Dado:** Arquivo .tex válido
**Quando:** convert é chamado
**Então:** CompileResult.success == True e DOCX existe

### CT-052.12: DissertationCompiler initialization
**Dado:** Input path e formats ["pdf", "audio", "docx"]
**Quando:** DissertationCompiler é instanciado
**Então:** input_path e formats estão configurados

### CT-052.13: DissertationCompiler._find_pdf
**Dado:** Input path com .tex existente
**Quando:** _find_pdf é chamado
**Então:** PDF correspondente é retornado (ou None)

### CT-052.14: DissertationCompiler._find_tex
**Dado:** Input path com .pdf existente
**Quando:** _find_tex é chamado
**Então:** .tex correspondente é retornado (ou None)

### CT-052.15: CompileResult dataclass
**Dado:** stage="latex", success=True
**Quando:** CompileResult é criado
**Então:** Campos estão preenchidos corretamente

### CT-052.16: DissertationStats dataclass
**Dado:** Estatísticas da dissertação
**Quando:** DissertationStats é criado
**Então:** Todos os campos têm valores default

---

## 5. DEPENDÊNCIAS

### 5.1 Python Packages
- `edge-tts` — Text-to-speech (Microsoft Edge)
- `pdfplumber` — Extração de texto de PDF
- `python-docx` — Criação/modificação de DOCX
- `pydub` — Manipulação de áudio (opcional, sem ffmpeg)

### 5.2 System Tools
- `pdflatex` — Compilação LaTeX (MiKTeX ou TeX Live)
- `biber` — Processamento de bibliografia
- `pandoc` — Conversão de documentos

### 5.3 Ecosystem Integration
- **MCPs:** sura-papers, arxiv-mcp, latest-science, scihub
- **Skills:** anti-ai-scanner, anti-plagiarism-scanner
- **Agents:** marceloclaro, master-orchestrator

---

## 6. MÉTRICAS DE SUCESSO

| Métrica | Target | Método de Medição |
|---------|--------|-------------------|
| CTs passando | 16/16 (100%) | pytest |
| Compile success | ≥95% | CompileResult.success |
| Anti-AI score | ≥85 | anti_ai_scanner.py |
| Anti-Plagiarism score | ≥85 (A) | anti_plagiarism_scanner.py |
| Audio quality | 0 errors | edge-tts output |
| DOCX structure | ≥3 headings | python-docx analysis |
| Undefined refs | 0 | pdflatex log |

---

## 7. HISTÓRICO

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2026-06-24 | Criação inicial pós-R26 |

---

## 8. ADRs

### ADR-052.01: edge-tts over gTTS
**Decisão:** Usar edge-tts (Microsoft) em vez de gTTS (Google)
**Razão:** Vozes mais naturais, sem limite de caracteres por request, gratuito
**Consequência:** Requer internet, mas qualidade significativamente superior

### ADR-052.02: biblatex+biber over natbib+apalike
**Decisão:** biblatex com backend biber
**Razão:** URLs nas referências, suporte a UTF-8, sorting=none
**Consequência:** Pipeline de compilação 4 passos (pdflatex→biber→pdflatex→pdflatex)

### ADR-052.03: pandoc for DOCX
**Decisão:** Usar pandoc com citeproc em vez de python-docx manual
**Razão:** Preserva estrutura LaTeX, processa citações automaticamente
**Consequência:** Requer pandoc instalado (~60MB)

### ADR-052.04: Chunk-based audio generation
**Decisão:** Dividir texto em chunks de 3500 chars antes de TTS
**Razão:** edge-tts pode falhar com textos muito longos
**Consequência:** Necessário concatenar chunks no final
