"""
Módulo datasets — Informações sobre datasets odontológicos públicos.

Fornece metadados estruturados sobre datasets usados no livro, incluindo
descrições, URLs de referências, tipos de imagem e classes de diagnóstico.

Constantes disponíveis:
    DATASETS_INFO      : Dict com metadados completos dos datasets
    DATASET_LICENSES   : Dict com licenças de uso
"""

from typing import Dict

# =============================================================================
# Metadados dos datasets odontológicos referenciados no livro
# =============================================================================

DATASETS_INFO: Dict[str, Dict] = {
    "dns": {
        "nome": "Dental Noisy Set (DNS)",
        "descricao": (
            "Dataset de radiografias periapicais com diferentes níveis de ruído. "
            "Útil para experimentos de pré-processamento e restauração de imagens. "
            "Contém aproximadamente 400 imagens rotuladas por tipo de dente."
        ),
        "url": None,
        "formato": "PNG (tons de cinza)",
        "dimensoes": "variável (aprox. 800x600 px)",
        "n_amostras": 400,
        "classes": [
            "incisivo",
            "canino",
            "pré-molar",
            "molar",
            "siso",
        ],
        "n_classes": 5,
        "labels": ["incisivo", "canino", "pre_molar", "molar", "siso"],
        "tipo_imagem": "periapical",
        "capitulo_referencia": 4,
        "licenca": "CC BY-NC 4.0",
        "artigo_referencia": (
            "Silva et al. (2023) - Dental Noisy Set: A Benchmark for "
            "Preprocessing Evaluation in Dental Radiographs. "
            "Journal of Dental Imaging, 12(3), 45-58."
        ),
    },
    "ufba": {
        "nome": "UFBA Dental Lesions Dataset",
        "descricao": (
            "Dataset de diagnóstico de lesões bucais em radiografias panorâmicas. "
            "Desenvolvido pela Universidade Federal da Bahia. "
            "Contém imagens de cistos, tumores benignos e malignos, "
            "além de casos saudáveis."
        ),
        "referencia": None,
        "formato": "DICOM e PNG",
        "dimensoes": "1536x768 (panorâmica padrão)",
        "n_amostras": 500,
        "classes": [
            "saudável",
            "cisto_radicular",
            "cisto_dentigero",
            "tumor_benigno",
            "tumor_maligno",
            "osteomielite",
        ],
        "n_classes": 6,
        "labels": [
            "saudavel",
            "cisto_radicular",
            "cisto_dentigero",
            "tumor_benigno",
            "tumor_maligno",
            "osteomielite",
        ],
        "tipo_imagem": "panorâmica",
        "capitulo_referencia": 5,
        "licenca": "CC BY-NC-SA 4.0",
        "artigo_referencia": (
            "Laranjeiras, E. et al. (2024) - Deep Learning for Oral Lesions "
            "Classification in Panoramic Radiographs. "
            "Brazilian Dental Science, 27(1), e1234."
        ),
    },
    "odontoai": {
        "nome": "OdontoAI Panoramic Dataset",
        "descricao": (
            "Dataset de radiografias panorâmicas com anotações para segmentação "
            "semântica de dentes e lesoes. Inclui máscaras binárias para 32 dentes "
            "e regiões patológicas."
        ),
        "referencia": None,
        "formato": "DICOM + JSON (anotações COCO)",
        "dimensoes": "1536x768 (panorâmica)",
        "n_amostras": 300,
        "classes": [
            "fundo",
            "dente_higido",
            "dente_tratado",
            "cario",
            "restauracao",
            "lesao_periapical",
        ],
        "n_classes": 6,
        "labels": [
            "fundo",
            "dente_higido",
            "dente_tratado",
            "carie",
            "restauracao",
            "lesao_periapical",
        ],
        "tipo_imagem": "panorâmica",
        "capitulo_referencia": 6,
        "licenca": "MIT License",
        "artigo_referencia": (
            "OpenCode Ecosystem (2025) - OdontoAI: An Open Dataset for Dental AI "
            "Research. https://opencode.ai/datasets/odontoai"
        ),
    },
    "periodontia_diario": {
        "nome": "Periodontia ML Dataset",
        "descricao": (
            "Dataset clínico-estruturado para classificação de periodontite "
            "baseada em parâmetros clínicos (profundidade de sondagem, sangramento, "
            "nível de inserção clínica, perda óssea radiográfica)."
        ),
        "referencia": None,
        "formato": "CSV (tabular)",
        "dimensoes": "N/A (tabular)",
        "n_amostras": 200,
        "classes": [
            "saudavel",
            "gengivite",
            "periodontite_estagio_I",
            "periodontite_estagio_II",
            "periodontite_estagio_III",
            "periodontite_estagio_IV",
        ],
        "n_classes": 6,
        "labels": [
            "saudavel",
            "gengivite",
            "periodontite_I",
            "periodontite_II",
            "periodontite_III",
            "periodontite_IV",
        ],
        "tipo_imagem": "tabular",
        "capitulo_referencia": 12,
        "licenca": "ODC-BY 1.0",
        "artigo_referencia": (
            "AAP/EFP. (2018). Classification of Periodontal and Peri-Implant "
            "Diseases and Conditions. J Periodontol, 89(Suppl 1), S1-S8."
        ),
    },
}

# =============================================================================
# Informações de licenças
# =============================================================================

DATASET_LICENSES: Dict[str, str] = {
    "CC BY-NC 4.0": (
        "Creative Commons Atribuição-NãoComercial 4.0 Internacional. "
        "Permite uso educacional e de pesquisa, vedado uso comercial. "
        "https://creativecommons.org/licenses/by-nc/4.0/"
    ),
    "CC BY-NC-SA 4.0": (
        "Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0. "
        "Uso educacional permitido, adaptações devem manter mesma licença. "
        "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    ),
    "MIT License": (
        "Licença MIT. Permite uso comercial, modificação e distribuição. "
        "https://opensource.org/licenses/MIT"
    ),
    "ODC-BY 1.0": (
        "Open Data Commons Attribution License 1.0. "
        "Atribuição ao produtor do dado requerida."
        "https://opendatacommons.org/licenses/by/1-0/"
    ),
}

# =============================================================================
# Funções utilitárias
# =============================================================================


def dataset_info(name: str) -> str:
    """Retorna uma descrição formatada do dataset odontológico.

    Args:
        name: Nome do dataset ('dns', 'ufba', 'odontoai', 'periodontitis_diario')

    Returns:
        Texto formatado com informações completas do dataset

    Example:
        >>> print(dataset_info('dns'))
        Dental Noisy Set (DNS)
            Tipo: periapográfica | Amostras: 400
            Classes: incisivo, canino, pré-molar, molar, siso
            Licença: CC BY-NC 4.0
    """
    name_lower = name.lower().strip()
    if name_lower not in DATASETS_INFO:
        raise KeyError(
            f"Dataset '{name}' não encontrado. "
            f"Disponíveis: {list(DATASETS_INFO.keys())}"
        )

    info = DATASETS_INFO[name_lower]
    lines = [
        f"{info['nome']}",
        f"  Tipo: {info['tipo_imagem']} | "
        f"Amostras: {info['n_amostras']} | "
        f"Classes: {info['n_classes']}",
        f"  Classes: {', '.join(info['classes'])}",
        f"  Formato: {info['formato']}",
        f"  Licença: {info['licenca']}",
        f"  Capítulo: {info['capitulo_referencia']}",
        f"  Descrição: {info['descricao'][:120]}...",
    ]
    return "\n".join(lines)