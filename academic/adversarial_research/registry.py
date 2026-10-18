"""Definições auditáveis; perfil registrado não equivale a inferência executada."""
import json
from pathlib import Path

SPECIALISTS=json.loads((Path(__file__).with_name('specialists.json')).read_text(encoding='utf-8'))
BY_ID={row['agent_id']:row for row in SPECIALISTS}
BY_NUMBER={row['number']:row for row in SPECIALISTS}
PILOT_NUMBERS=('A03','A05','A08','A10','A13','A18','A24','A32')
FAMILIES={
 'originalidade':('A05','Qual lacuna permanece diante da literatura recuperada?','Comparação documentada com fontes pertinentes, incluindo resultados contrários.'),
 'epistemologia':('A08','Os conceitos foram operacionalizados sem erro de categoria?','Definições, indicadores e justificativa da relação entre construto e medida.'),
 'amostragem':('A10','Quais unidades e critérios sustentam as inferências propostas?','Plano de seleção, unidades efetivas, repetições e limites adequados ao desenho.'),
 'validade':('A13','Que evidência distingue mudança, associação e causalidade?','Estratégia de identificação ou linguagem proporcional ao desenho observado.'),
 'etica':('A18','Quem pode participar, consentir e autorizar o uso do conhecimento?','Contexto, consentimentos, governança pertinente e encaminhamento institucional quando aplicável.'),
 'integridade':('A24','Quais resultados foram observados, simulados ou apenas propostos?','Fontes, versões, execuções e limites das métricas relatadas.'),
 'viabilidade':('A28','Que recursos, dependências e contingências estão efetivamente disponíveis?','Comprovação de acesso, recursos e precedências; cronograma não comprova disponibilidade.'),
 'aderencia':('A30','Como o projeto atende aos critérios institucionais documentados?','Edital ou rubrica com origem/localizador e mapeamento explícito do projeto.'),
}

def specialist(number): return BY_NUMBER[number]
