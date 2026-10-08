"""Renderiza a versão em português da Figura 1 a partir do código vetorial original.

As coordenadas, cores e caminhos são os mesmos do diagrama em inglês. Apenas
os textos e o nome dos arquivos de saída são substituídos antes da plotagem.
"""

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "render_pipeline_v2_compact.py"
code = SOURCE.read_text(encoding="utf-8")

translations = {
    'STEM = HERE / "Figure_1_pipeline_v2_compact"':
        'STEM = HERE / "Figure_1_pipeline_v2_compact_pt"',
    "OdontoCA | Research workflow and evidence gates":
        "OdontoCA | Fluxo de pesquisa e critérios de evidência",
    "Solid blue: executed analysis    Dashed amber: proposed / not run":
        "Azul contínuo: executado    Âmbar tracejado: proposto / não executado",
    '"EXECUTED"': '"EXECUTADO"',
    '"INTERNAL ONLY"': '"APENAS INTERNO"',
    '"NOT RUN"': '"NÃO EXECUTADO"',
    '"B  CLINICAL"': '"B  CLÍNICO"',
    '"C  MICROBIOME"': '"C  MICROBIOMA"',
    '"D  IMAGE"': '"D  IMAGENS"',
    r"Synthetic\ntooth + ASV data": r"Dados sintéticos:\ndentes + ASVs",
    r"Consecutive\nH → C transitions": r"Transições H → C\nconsecutivas",
    r"Child-grouped\nnested CV": r"Validação aninhada\npor criança",
    r"OOF metrics:\ntechnical only": r"Métricas OOF:\napenas técnicas",
    r"Public Table S1\nsource + checksum": r"Tabela S1 pública:\nfonte + hash",
    r"Reproduce cohort\nand onset counts": r"Reproduzir coorte\ne novos casos",
    r"Corrected child\nnested CV": r"Validação aninhada\ncorrigida por criança",
    r"Train-only calibration;\nOOF + child CI": r"Calibração só no treino;\nOOF + IC por criança",
    r"Qiita / BIOM\nsource + mapping": r"Fonte Qiita/BIOM\n+ pareamento",
    r"Exact SampleID\nand library QC": r"Parear SampleID;\nrevisar bibliotecas",
    r"Train-fold ASV,\nCLR, scaling, PCA": r"ASV e CLR no treino;\nescala e PCA",
    r"Real OOF model\nand uncertainty": r"Modelo OOF real\ne incerteza",
    r"Images, labels\nand provenance": r"Imagens, rótulos\ne proveniência",
    r"Patient split +\nduplicate audit": r"Separar pacientes;\nchecar duplicatas",
    r"Validation tuning;\nheld-out test": r"Ajuste na validação;\nteste reservado",
    r"FDI mapping +\nclinician review": r"Mapeamento FDI\n+ revisão clínica",
    "GATES BEFORE MULTIMODAL OR CLINICAL CLAIMS":
        "CRITÉRIOS ANTES DE ALEGAÇÕES MULTIMODAIS OU CLÍNICAS",
    r"Fusion only for the same cohort\nand patient + visit + tooth":
        r"Fusão só na mesma coorte:\npaciente + visita + dente",
    r"Independent external validation\nand measured calibration":
        r"Validação externa independente\ne calibração medida",
    r"Manuscript labels synthetic,\ninternal and external evidence":
        r"Artigo distingue evidências\nsintéticas, internas e externas",
    "Synthetic results do not estimate clinical performance; unmatched datasets remain separate.":
        "OOF = fora da dobra. Dados sintéticos não estimam desempenho clínico; bases sem pareamento ficam separadas.",
}

for original, translated in translations.items():
    count = code.count(original)
    expected = 2 if original == '"NOT RUN"' else 1
    if count != expected:
        raise AssertionError(f"Esperadas {expected} ocorrências, encontradas {count}: {original!r}")
    code = code.replace(original, translated, expected)

exec(compile(code, str(SOURCE), "exec"), {"__file__": str(SOURCE), "__name__": "__translated_figure__"})
