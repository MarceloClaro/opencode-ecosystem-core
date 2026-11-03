from .registry import BY_NUMBER

def route(project):
    numbers={'A01','A02','A03','A04','A05','A06','A07','A08','A09','A10','A11','A13','A18','A22','A23','A24','A25','A26','A27','A28','A29','A30','A32','A33','A34'}
    c=project['context']; kind=project['study_type']
    if kind in {'computational','experimental','quantitative','mixed'} or c.get('uses_ai') is True: numbers|={'A12','A17'}
    if kind in {'qualitative','mixed'} or c.get('humans') is True: numbers|={'A14','A15','A16','A17'}
    if c.get('indigenous_knowledge') is True: numbers|={'A19','A21'}
    if c.get('personal_data') is True: numbers.add('A20')
    if kind=='mixed' or len(c.get('disciplines',[]))>1: numbers.add('A31')
    return [BY_NUMBER[n] for n in sorted(numbers)]
