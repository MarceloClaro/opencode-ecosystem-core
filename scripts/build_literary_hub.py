from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / 'projetos/literarios'
HUB.mkdir(parents=True, exist_ok=True)

def pdf_info(path: Path):
    if not path.is_file():
        return {}
    try:
        out = subprocess.run(['pdfinfo', str(path)], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return {}
    rows = {}
    for line in out.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            rows[k.strip()] = v.strip()
    return {
        'pages': int(rows.get('Pages', '0') or 0),
        'page_size': rows.get('Page size'),
        'title': rows.get('Title') or None,
        'author': rows.get('Author') or None,
        'producer': rows.get('Producer') or None,
    }

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def link(rel: str, target: str):
    target_abs = (ROOT / target).resolve()
    if not target_abs.exists():
        return {'path': rel, 'target': target, 'status': 'missing'}
    dest = HUB / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    rel_target = os.path.relpath(target_abs, dest.parent.resolve())
    if dest.is_symlink():
        current = os.readlink(dest)
        if current == rel_target:
            return {'path': rel, 'target': target, 'status': 'ok'}
        dest.unlink()
    elif dest.exists():
        return {'path': rel, 'target': target, 'status': 'conflict'}
    os.symlink(rel_target, dest)
    return {'path': rel, 'target': target, 'status': 'ok'}

WORKS = [
    {
        'id': 'molambudos-victoria-regia',
        'title': 'Molambudos — O Diário do Paciente 1.260 (KDP PT-BR)',
        'category': 'livro', 'scope': 'literario', 'canonical': True,
        'status': 'canônico KDP PT-BR; 435 pp; 160×230 mm',
        'source': 'projetos/molambudos/Molambudos_VictoriaRegia',
        'compiled': 'projetos/molambudos/Molambudos_VictoriaRegia',
        'pdf': 'projetos/molambudos/Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf',
        'links': [('molambudos/victoria-regia', 'projetos/molambudos/Molambudos_VictoriaRegia')],
        'audit': 'reports/r1071',
        'notes': 'Book Studio: book.json, engine latex, source main_kdp_pt_160x230mm.tex; metadados e aspas corrigidos localmente.',
    },
    {
        'id': 'molambudos-v2',
        'title': 'Molambudos v2.0 — O Prontuário 1.263 (esboço)',
        'category': 'livro', 'scope': 'literario', 'canonical': False,
        'status': 'esboço v0.1; 57 pp; 6×9 in; 112 testes',
        'source': 'projetos/molambudos/Molambudos_v2',
        'compiled': 'projetos/molambudos/Molambudos_v2',
        'pdf': 'projetos/molambudos/Molambudos_v2/Molambudos_O-Prontuario-1263_v2.0-esboco_2026-07-13.pdf',
        'links': [('molambudos/v2', 'projetos/molambudos/Molambudos_v2')],
        'audit': 'projetos/molambudos/Molambudos_v2/misc/avaliacao_honesta_v2.0.md',
        'notes': 'Sete degraus lineares; projeto distinto da edição VictoriaRegia.',
    },
    {
        'id': 'molambudos-diario',
        'title': 'Molambudos — Diário 1.260 v2 (Partes I–II)',
        'category': 'livro', 'scope': 'literario', 'canonical': False,
        'status': '49 pp; 6×9 in; versão ilustrada',
        'source': 'projetos/molambudos/Molambudos_v2_Diario',
        'compiled': 'projetos/molambudos/Molambudos_v2_Diario',
        'pdf': 'projetos/molambudos/Molambudos_v2_Diario/Molambudos_Diario-1260_v2-visceral_PartesI-II-ilustrada_2026-07-13.pdf',
        'links': [('molambudos/diario', 'projetos/molambudos/Molambudos_v2_Diario')],
        'audit': None,
        'notes': 'Derivação visual do Diário; não substitui a edição VictoriaRegia.',
    },
    {
        'id': 'molambudos-template-antigo',
        'title': 'Molambudos — template LaTeX antigo (4 capítulos)',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': '25 pp; A4; template incompleto',
        'source': 'templates/livro/molambudos',
        'compiled': 'templates/livro/molambudos',
        'pdf': 'templates/livro/molambudos/main.pdf',
        'links': [('molambudos/template-antigo', 'templates/livro/molambudos')],
        'audit': 'REVISAO_MOLAMBUDOS.md',
        'notes': 'Objeto do parecer antigo; NÃO representa a edição VictoriaRegia. Ver nota de escopo.',
    },
    {
        'id': 'livro-opencode',
        'title': 'Engenharia de Ecossistemas Cognitivos: OpenCode Ecosystem',
        'category': 'livro', 'scope': 'literario', 'canonical': True,
        'status': '478 pp; A4; compilado em template/projects',
        'source': 'projetos/02_Livro_OpenCode',
        'compiled': 'templates/projects/livro-opencode',
        'pdf': 'templates/projects/livro-opencode/livro-dark.pdf',
        'links': [('livros/livro-opencode-fonte', 'projetos/02_Livro_OpenCode'),
                  ('livros/livro-opencode-compilado', 'templates/projects/livro-opencode')],
        'audit': None,
        'notes': 'Fonte em projetos/02; PDF em templates/projects/livro-opencode.',
    },
    {
        'id': 'livro-volume2',
        'title': 'Volume 2 — Gêmeos Digitais Periodontais: O Framework SUS-Twin',
        'category': 'livro', 'scope': 'literario', 'canonical': True,
        'status': '184 pp; A4; compilado em template/projects',
        'source': 'projetos/03_Livro_Volume2',
        'compiled': 'templates/projects/livro-volume2',
        'pdf': 'templates/projects/livro-volume2/dark.pdf',
        'links': [('livros/livro-volume2-fonte', 'projetos/03_Livro_Volume2'),
                  ('livros/livro-volume2-compilado', 'templates/projects/livro-volume2')],
        'audit': None,
        'notes': 'Fonte em projetos/03; PDF em templates/projects/livro-volume2.',
    },
    {
        'id': 'livro-gemeos-odontologia',
        'title': 'Gêmeos Digitais Periodontais: O Framework SUS-Twin',
        'category': 'livro', 'scope': 'literario', 'canonical': True,
        'status': '180 pp; A4; compilado em template/projects',
        'source': 'projetos/04_Livro_Gemeos_Odontologia',
        'compiled': 'templates/projects/livro-gemeos-odontologia',
        'pdf': 'templates/projects/livro-gemeos-odontologia/dark.pdf',
        'links': [('livros/livro-gemeos-fonte', 'projetos/04_Livro_Gemeos_Odontologia'),
                  ('livros/livro-gemeos-compilado', 'templates/projects/livro-gemeos-odontologia')],
        'audit': None,
        'notes': 'Fonte em projetos/04; PDF em templates/projects/livro-gemeos-odontologia.',
    },
    {
        'id': 'ia-em-odontologia',
        'title': 'IA em Odontologia — livro/template',
        'category': 'livro', 'scope': 'literario', 'canonical': False,
        'status': 'fonte e template; sem PDF compilado no diretório',
        'source': 'projetos/ia-em-odontologia',
        'compiled': 'templates/livro/ia-em-odontologia',
        'pdf': None,
        'links': [('livros/ia-odontologia-fonte', 'projetos/ia-em-odontologia'),
                  ('livros/ia-odontologia-template', 'templates/livro/ia-em-odontologia')],
        'audit': None,
        'notes': 'Fonte em projetos/ia-em-odontologia; template em templates/livro.',
    },
    {
        'id': 'template-victoria-regia',
        'title': 'Victoria Regia — template clássico LaTeX',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'template; sem PDF compilado',
        'source': 'projetos/36_Victoria_Regia',
        'compiled': None, 'pdf': None,
        'links': [('templates/victoria-regia', 'projetos/36_Victoria_Regia')],
        'audit': None,
        'notes': 'Template base; duplicatas em 23_Template_Livros e na raiz.',
    },
    {
        'id': 'template-livros',
        'title': '23_Template_Livros — coleção de templates',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'coleção de templates; sem PDF único',
        'source': 'projetos/23_Template_Livros',
        'compiled': None, 'pdf': None,
        'links': [('templates/template-livros', 'projetos/23_Template_Livros')],
        'audit': None,
        'notes': 'Contém Victoria Regia e template Springer Nature.',
    },
    {
        'id': 'template-livro-opencode',
        'title': 'Template — Livro OpenCode',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'template com PDF compilado',
        'source': 'templates/projects/livro-opencode',
        'compiled': 'templates/projects/livro-opencode',
        'pdf': 'templates/projects/livro-opencode/livro-dark.pdf',
        'links': [('templates/livro-opencode', 'templates/projects/livro-opencode')],
        'audit': None, 'notes': 'Template e PDF do livro OpenCode.',
    },
    {
        'id': 'template-livro-volume2',
        'title': 'Template — Livro Volume 2',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'template com PDF compilado',
        'source': 'templates/projects/livro-volume2',
        'compiled': 'templates/projects/livro-volume2',
        'pdf': 'templates/projects/livro-volume2/dark.pdf',
        'links': [('templates/livro-volume2', 'templates/projects/livro-volume2')],
        'audit': None, 'notes': 'Template e PDF do Volume 2.',
    },
    {
        'id': 'template-livro-gemeos',
        'title': 'Template — Livro Gêmeos Odontologia',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'template com PDF compilado',
        'source': 'templates/projects/livro-gemeos-odontologia',
        'compiled': 'templates/projects/livro-gemeos-odontologia',
        'pdf': 'templates/projects/livro-gemeos-odontologia/dark.pdf',
        'links': [('templates/livro-gemeos', 'templates/projects/livro-gemeos-odontologia')],
        'audit': None, 'notes': 'Template e PDF do livro Gêmeos.',
    },
    {
        'id': 'template-livro-odontologia-ia',
        'title': 'Template — Livro Odontologia IA',
        'category': 'template', 'scope': 'literario', 'canonical': False,
        'status': 'template; sem PDF compilado',
        'source': 'templates/projects/livro-odontologia-ia',
        'compiled': None, 'pdf': None,
        'links': [('templates/livro-odontologia-ia', 'templates/projects/livro-odontologia-ia')],
        'audit': None, 'notes': 'Template de livro; compilar antes de auditar.',
    },
]

# Academic context
ACADEMIC = [
    ('01_Dissertacao_OpenCode', 'Dissertação OpenCode'),
    ('05_Artigo_MIT_IA', 'Artigo MIT/IA'),
    ('06_Artigos', 'Artigos'),
    ('07_Criador_Artigo', 'Criador de Artigo'),
    ('08_Docs_Dissertacao', 'Docs da Dissertação'),
    ('09_MD_Dissertacao_LaTeX', 'Dissertação LaTeX'),
    ('10_Dados_Entrada_Mestrado', 'Dados de Entrada do Mestrado'),
    ('11_Evolve_Artigos', 'Evolução de Artigos'),
    ('31_Template_Ensaio_Fichamento', 'Template de Ensaio/Fichamento'),
    ('32_Documentos', 'Documentos'),
    ('33_Nano', 'Nano'),
    ('34_Orchestration', 'Orchestration'),
    ('35_ZRM_Master', 'ZRM Master'),
]
for dirname, title in ACADEMIC:
    WORKS.append({
        'id': 'academico-' + dirname.casefold().replace('_','-'),
        'title': title, 'category': 'academico', 'scope': 'academico',
        'canonical': False, 'status': 'contexto acadêmico; fora do escopo literário',
        'source': f'projetos/{dirname}', 'compiled': None, 'pdf': None,
        'links': [(f'academicos/{dirname.casefold()}', f'projetos/{dirname}')],
        'audit': None, 'notes': 'Mantido para contexto; não é obra literária.',
    })

# Academic templates 12..30
for n in range(12, 31):
    if n == 23:
        continue
    matches = sorted(ROOT.glob(f'projetos/{n}_*'))
    for match in matches:
        if not match.is_dir(): continue
        WORKS.append({
            'id': 'template-academico-' + match.name.casefold().replace('_','-'),
            'title': match.name.replace('_',' '),
            'category': 'template-academico', 'scope': 'academico',
            'canonical': False, 'status': 'template acadêmico; contexto',
            'source': f'projetos/{match.name}', 'compiled': None, 'pdf': None,
            'links': [(f'templates-academicos/{match.name.casefold()}', f'projetos/{match.name}')],
            'audit': None, 'notes': 'Template acadêmico; fora do escopo literário.',
        })

# Remove a duplicated academic link: 23_Template_Livros is literary template.
stale = HUB / 'templates-academicos/23_template_livros'
if stale.is_symlink():
    stale.unlink()

# Create links and catalog rows
rows = []
for work in WORKS:
    pdf = ROOT / work['pdf'] if work.get('pdf') else None
    info = pdf_info(pdf) if pdf else {}
    row = dict(work)
    row['pdf'] = work.get('pdf')
    row['pdf_pages'] = info.get('pages')
    row['pdf_page_size'] = info.get('page_size')
    row['pdf_title'] = info.get('title')
    row['pdf_sha256'] = sha256(pdf) if pdf and pdf.is_file() else None
    row['pdf_bytes'] = pdf.stat().st_size if pdf and pdf.is_file() else None
    row['links'] = [link(rel, target) for rel, target in work.get('links', [])]
    rows.append(row)

catalog = {
    'schema_version': 1,
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'root': 'projetos/literarios',
    'policy': 'symlinks; nenhum original foi movido; projetos/ é gitignored',
    'count': len(rows),
    'works': rows,
}
(HUB / 'catalogo.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def table(scope):
    lines = ['| ID | Título | Canônico | Estado | Páginas | PDF |', '|---|---|:---:|---|---:|---|']
    for row in rows:
        if row['scope'] != scope or row['category'].startswith('template'):
            continue
        pdf = f"`{row['pdf']}`" if row.get('pdf') else '—'
        canon = 'sim' if row.get('canonical') else '—'
        lines.append(f"| `{row['id']}` | {row['title']} | {canon} | {row['status']} | {row.get('pdf_pages') or '—'} | {pdf} |")
    return '\n'.join(lines)

def template_table(scope):
    lines = ['| ID | Título | Estado | PDF |', '|---|---|---|---|']
    for row in rows:
        if row['scope'] != scope or not row['category'].startswith('template'):
            continue
        pdf = f"`{row['pdf']}`" if row.get('pdf') else '—'
        lines.append(f"| `{row['id']}` | {row['title']} | {row['status']} | {pdf} |")
    return '\n'.join(lines)

readme = f'''# Hub dos projetos literários

**Gerado:** {catalog['generated_at']}  
**Política:** symlinks; nenhum original foi movido. `projetos/` é gitignored.

## Como usar

```bash
cd projetos/literarios
cat catalogo.json | python3 -m json.tool | less
cd molambudos/victoria-regia
python3 -m marceloclaro.book_studio status .
python3 -m marceloclaro.book_studio build . --engine latex --timeout 300
```

## Literatura

{table('literario')}

## Templates literários

{template_table('literario')}

## Acadêmicos (contexto, fora do escopo literário)

{table('academico')}

## Templates acadêmicos

{template_table('academico')}

## Auditoria

- Molambudos: `reports/r1071/README.md` e `molambudos/victoria-regia/BOOK_STUDIO_AUDIT.md`.
- O parecer antigo `REVISAO_MOLAMBUDOS.md` descreve a versão de 4 capítulos; não usar para a edição VictoriaRegia.
- Checklist mínimo por obra: metadados, trim, fontes embutidas, TOC/bookmarks, duplicações, aspas/dashes, capa/lombada, EPUB e KDP preflight.

## Limites

- O hub não duplica conteúdo; se um symlink quebrar, o projeto original pode ter sido movido.
- Não há validação editorial automática; QA técnico não substitui leitura humana.
- Nada foi publicado ou enviado à KDP.
'''
(HUB / 'README.md').write_text(readme, encoding='utf-8')
checklist = '''# Checklist de auditoria editorial

Para cada obra do hub:

1. **Identidade**: título, autor, edição, ISBN e editora corretos no PDF.
2. **Trim e páginas**: tamanho físico e contagem batem com o destino (KDP/gráfica).
3. **Fontes**: todas embutidas; nenhuma fonte ausente ou substituída.
4. **Estrutura**: sumário, bookmarks, partes e capítulos navegáveis.
5. **Texto**: duplicações, aspas/dashes, espaços antes de pontuação, viúvas/órfãs.
6. **Imagens**: resolução, sangria, cor e legendas.
7. **Capa**: frente, contracapa, lombada, bleed, barcode e ISBN.
8. **EPUB**: navegação, metadados, imagens e acessibilidade.
9. **Preflight**: PDF/X quando exigido, fontes, transparência e página final.
10. **Revisão humana**: leitura de galerada e parecer independente.

Nenhum item é aprovado apenas por QA automático.
'''
(HUB / 'CHECKLIST_AUDITORIA.md').write_text(checklist, encoding='utf-8')
print(json.dumps({
    'status': 'completed',
    'works': len(rows),
    'canonical': [row['id'] for row in rows if row.get('canonical')],
    'hub': str(HUB),
    'catalog': str(HUB / 'catalogo.json'),
}, ensure_ascii=False, indent=2))
