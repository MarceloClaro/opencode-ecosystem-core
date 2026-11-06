"""
Prática 17.1 — Publicação de Modelo Odontológico no Hugging Face
Com Model Card, Data Card e documentação ABNT
"""
import json
from datetime import datetime

# ============================================================
# MODEL CARD — Documentação do modelo treinado
# ============================================================

def generate_model_card(
    model_name: str,
    task: str,
    architecture: str,
    dataset: str,
    performance: dict,
    limitations: list,
    license_type: str,
) -> dict:
    """
    Gera um Model Card estruturado para publicação.
    
    Segue o template proposto por Mitchell et al. (2019)
    'Model Cards for Model Reporting' (10.1145/3287560.3287596)
    """
    model_card = {
        "model_details": {
            "name": model_name,
            "version": "1.0.0",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "task": task,
            "architecture": architecture,
            "framework": "TensorFlow 2.15 / PyTorch 2.2",
        },
        "intended_use": {
            "primary_use": f"Auxílio diagnóstico para {task}",
            "clinical_setting": "Consultório odontológico e clínicas de radiologia",
            "out_of_scope": [
                "Substituição do diagnóstico clínico profissional",
                "Uso em populações pediátricas não validadas",
                "Diagnóstico de condições não incluídas no treinamento",
            ],
        },
        "training_data": {
            "dataset_name": dataset,
            "n_samples": performance.get("n_train", "N/A"),
            "n_classes": performance.get("n_classes", "N/A"),
            "demographic_info": "Pacientes brasileiros, 18-80 anos, ambos os sexos",
            "data_split": "80% treino, 10% validação, 10% teste (estratificado)",
        },
        "performance_metrics": performance,
        "limitations": limitations,
        "license": license_type,
        "citation": generate_abnt_citation(model_name),
    }
    return model_card


def generate_data_card(
    dataset_name: str,
    modality: str,
    n_samples: int,
    n_classes: int,
    collection_period: str,
    ethical_approval: str,
) -> dict:
    """
    Gera um Data Card (Data Sheet) para datasets odontológicos.
    
    Inspirado em Gebru et al. (2021)
    'Datasheets for Datasets' (10.1145/3458723)
    """
    return {
        "dataset_name": dataset_name,
        "modality": modality,
        "n_samples": n_samples,
        "n_classes": n_classes,
        "collection_period": collection_period,
        "institution": ethical_approval,
        "anonymization": "Remoção de metadados DICOM e blur de regiões identificáveis",
        "data_format": "DICOM / PNG 16-bit",
        "preprocessing": "CLAHE, resize 512x512, normalização [-1, 1]",
        "ethical_approval": "Comitê de Ética em Pesquisa — CAAE aprovado",
    }


def generate_abnt_citation(model_name: str) -> str:
    """
    Gera citação ABNT NBR 6023 para modelo publicado.
    
    Formato:
    SOBRENOME, Nome. Título do modelo [software]. Versão. 
    Plataforma, Ano. DOI: 10.xxxx/xxxxx.
    """
    return (
        f"LARANJEIRAS, Edson. {model_name} [software]. "
        f"v1.0.0. Hugging Face Model Hub, {datetime.now().year}. "
        f"Disponível em: https://huggingface.co/odontologia/. "
        f"Acesso em: {datetime.now().strftime('%d %b. %Y')}."
    )


# ============================================================
# COMPARAÇÃO DE LICENÇAS
# ============================================================

LICENSES_COMPARISON = {
    "MIT": {
        "uso_comercial": True,
        "distribuicao": True,
        "modificacao": True,
        "patente": "Não",
        "copyleft": "Não",
        "recomendado_para": "Código aberto com máxima flexibilidade",
    },
    "Apache 2.0": {
        "uso_comercial": True,
        "distribuicao": True,
        "modificacao": True,
        "patente": "Sim (explícita)",
        "copyleft": "Não",
        "recomendado_para": "Código com proteção de patentes",
    },
    "GPLv3": {
        "uso_comercial": True,
        "distribuicao": True,
        "modificacao": True,
        "patente": "Sim",
        "copyleft": "Sim (forte)",
        "recomendado_para": "Software que deve permanecer livre",
    },
    "CC BY 4.0": {
        "uso_comercial": True,
        "distribuicao": True,
        "modificacao": True,
        "patente": "N/A",
        "copyleft": "Não",
        "recomendado_para": "Datasets, artigos, documentação",
    },
    "CC BY-NC-SA 4.0": {
        "uso_comercial": False,
        "distribuicao": True,
        "modificacao": True,
        "patente": "N/A",
        "copyleft": "Sim (ShareAlike)",
        "recomendado_para": "Uso acadêmico e educacional apenas",
    },
}


if __name__ == "__main__":
    print("=" * 70)
    print("REPRODUTIBILIDADE E PUBLICAÇÃO DE MODELOS")
    print("=" * 70)
    
    # Model Card para Classificador de Cáries
    print("\n📋 MODEL CARD — CariesICDAS Classifier")
    print("-" * 50)
    
    model_card = generate_model_card(
        model_name="CariesICDAS-EfficientNetB3",
        task="Classificação de cáries (ICDAS 0-6)",
        architecture="EfficientNet-B3 com GlobalAveragePooling + Dense(256) + Dropout(0.3)",
        dataset="ICDAS-Brasil-2024 (n=3,400 radiografias bitewing)",
        performance={
            "accuracy": 0.912,
            "sensitivity": 0.887,
            "specificity": 0.893,
            "kappa_cohen": 0.834,
            "auc": 0.947,
            "n_train": 3400,
            "n_classes": 7,
        },
        limitations=[
            "Validado apenas em radiografias bitewing digitais",
            "População brasileira adulta (18-80 anos)",
            "Não validado para dentes decíduos",
            "Requer imagens com resolução ≥ 300 DPI",
        ],
        license_type="MIT",
    )
    
    print(json.dumps(model_card, indent=2, ensure_ascii=False))
    
    # Data Card
    print("\n📊 DATA CARD — ICDAS-Brasil-2024")
    print("-" * 50)
    
    data_card = generate_data_card(
        dataset_name="ICDAS-Brasil-2024",
        modality="Radiografia bitewing digital",
        n_samples=3400,
        n_classes=7,
        collection_period="2023-2024",
        ethical_approval="Comitê de Ética — CAAE: 12345678.9.0000.0000",
    )
    print(json.dumps(data_card, indent=2, ensure_ascii=False))
    
    # Licenças
    print("\n📜 COMPARAÇÃO DE LICENÇAS")
    print("-" * 50)
    for lic, info in LICENSES_COMPARISON.items():
        print(f"\n  {lic}:")
        for key, val in info.items():
            print(f"    {key}: {val}")
    
    # Citação ABNT
    print("\n📝 CITAÇÃO ABNT:")
    print(f"  {generate_abnt_citation('CariesICDAS-EfficientNetB3')}")
    
    print("\n✅ Documentação de reprodutibilidade completa!")
