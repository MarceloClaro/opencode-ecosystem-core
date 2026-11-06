"""
Prática 12.1 — Especificação SDD para Detector de Cáries
Usa o decorador @spec do pacote odontoia.sdd
"""
from odontoia.sdd.spec import spec, get_spec, validate_spec, list_specs

@spec(
    problem="Detectar cáries proximais em radiografias bitewing",
    input="ndarray (H, W) uint8 — radiografia bitewing",
    output="dict {'has_caries': bool, 'confidence': float, 'location': (x,y,w,h)}",
    criteria=[
        "accuracy > 0.88",
        "sensitivity > 0.85",
        "specificity > 0.85",
        "dice_score > 0.80",
        "inference_time < 200ms",
    ],
    category="classificacao",
)
def detect_caries_bitewing(image):
    """
    Detecta lesões cariosas proximais em radiografias bitewing.
    
    Utiliza CNN pré-treinada com EfficientNet-B3 fine-tunada
    no dataset ICDAS-2024 (n=3,400 radiografias).
    
    Args:
        image: ndarray (H, W) uint8 — radiografia bitewing
    
    Returns:
        dict com has_caries, confidence e localização da lesão
    """
    pass  # Implementação nos capítulos seguintes


@spec(
    problem="Classificar lesões bucais em imagens intraorais",
    input="ndarray (224, 224, 3) uint8 — foto clínica intraoral RGB",
    output="dict {'class': str, 'probabilities': dict, 'heatmap': ndarray}",
    criteria=[
        "accuracy > 0.90",
        "sensitivity > 0.87",
        "specificity > 0.87",
        "num_classes == 5",
        "output_probability_sum == 1.0",
    ],
    category="classificacao",
)
def classify_oral_lesion(image):
    """
    Classifica lesões bucais em 5 categorias clínicas.
    
    Categorias: saudável, leucoplasia, líquen plano,
    carcinoma espinocelular, úlcera aftosa.
    
    Args:
        image: foto clínica intraoral RGB normalizada
    
    Returns:
        dict com classe predita, probabilidades e heatmap Grad-CAM
    """
    pass


@spec(
    problem="Segmentar dentes em radiografias panorâmicas",
    input="ndarray (512, 512) uint8 — radiografia panorâmica",
    output="ndarray (512, 512) uint8 — máscara de segmentação (0=background, 1..32=dentes)",
    criteria=[
        "dice_score > 0.85",
        "iou > 0.78",
        "precision > 0.88",
        "recall > 0.82",
    ],
    category="segmentacao",
)
def segment_teeth_panoramic(image):
    """
    Segmenta dentes individuais em radiografias panorâmicas.
    
    Utiliza arquitetura U-Net com backbone EfficientNet-B3.
    Treinada no dataset UFBA-UESC Dental Images (n=1,500).
    
    Args:
        image: radiografia panorâmica em escala de cinza
    
    Returns:
        máscara de segmentação com 32 instâncias de dentes
    """
    pass


# Demonstração de recuperação de especificação
if __name__ == "__main__":
    print("=== ESPECIFICAÇÕES SDD REGISTRADAS ===")
    print(f"Total de specs: {len(list_specs())}")
    
    for func_name, data in list_specs().items():
        print(f"\n📋 {func_name}")
        print(f"   Problema: {data['problem']}")
        print(f"   Entrada:  {data['input']}")
        print(f"   Saída:    {data['output']}")
        print(f"   Critérios: {data['criteria']}")
    
    # Valida especificações
    from odontoia.sdd.validator import SpecVerifier
    verifier = SpecVerifier()
    
    spec_caries = get_spec(detect_caries_bitewing)
    print(f"\n✅ Especificação do detector de cáries:")
    print(f"   Critério principal: accuracy > 0.88")
    print(f"   Registrada em: {spec_caries['module']}.{spec_caries['function']}")
