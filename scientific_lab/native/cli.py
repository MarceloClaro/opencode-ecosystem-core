from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from . import research, review, evidence

def _research(argv):
    ap=argparse.ArgumentParser(prog='scientific_lab research'); sub=ap.add_subparsers(dest='sub',required=True)
    for name in ('search','harvest'):
        p=sub.add_parser(name); p.add_argument('query'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--limit',type=int,default=30); p.add_argument('--per-platform',type=int,default=5); p.add_argument('--platforms'); p.add_argument('--max-downloads',type=int,default=10)
    a=ap.parse_args(argv); platforms=[x.strip() for x in a.platforms.split(',') if x.strip()] if a.platforms else None
    if a.sub=='search':
        path,_,manifest=research.search(a.query,a.workspace,limit=a.limit,per_platform=a.per_platform,platforms=platforms); print(json.dumps({'manifest':str(path),'results':len(manifest['results'])},ensure_ascii=False,indent=2)); return 0
    print(json.dumps(research.harvest(a.query,a.workspace,limit=a.limit,per_platform=a.per_platform,max_downloads=a.max_downloads,platforms=platforms),ensure_ascii=False,indent=2)); return 0

def _review(argv):
    ap=argparse.ArgumentParser(prog='scientific_lab review'); sub=ap.add_subparsers(dest='sub',required=True)
    p=sub.add_parser('init'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--project-id',required=True); p.add_argument('--title',required=True); p.add_argument('--question',required=True); p.add_argument('--approved-by'); p.add_argument('--human',action='store_true')
    p=sub.add_parser('ingest'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--manifest',type=Path,required=True)
    p=sub.add_parser('screen'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--protocol-id',required=True); p.add_argument('--study',required=True); p.add_argument('--stage',choices=['title_abstract','full_text'],required=True); p.add_argument('--reviewer',required=True); p.add_argument('--decision',choices=['include','exclude','uncertain'],required=True); p.add_argument('--reason',required=True); p.add_argument('--human',action='store_true')
    p=sub.add_parser('prisma'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--protocol-id',required=True); p.add_argument('--human-verified',action='store_true')
    a=ap.parse_args(argv)
    if a.sub=='init': print(review.init_protocol(a.workspace,a.project_id,a.title,a.question,approved_by=a.approved_by,human=a.human)); return 0
    if a.sub=='ingest': print(json.dumps(review.ingest(a.workspace,a.manifest),ensure_ascii=False,indent=2)); return 0
    if a.sub=='screen': print(review.screen(a.workspace,a.protocol_id,a.study,a.stage,a.reviewer,a.decision,a.reason,human=a.human)); return 0
    print(review.prisma(a.workspace,a.protocol_id,human_verified=a.human_verified)); return 0

def _evidence(argv):
    ap=argparse.ArgumentParser(prog='scientific_lab evidence'); sub=ap.add_subparsers(dest='sub',required=True)
    p=sub.add_parser('annotate'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--project-id',required=True); p.add_argument('--claim-id',required=True); p.add_argument('--claim-text'); p.add_argument('--study-id',required=True); p.add_argument('--relation',required=True); p.add_argument('--locator',required=True); p.add_argument('--text',required=True); p.add_argument('--annotator',required=True); p.add_argument('--status',choices=['candidate','verified','rejected'],default='candidate'); p.add_argument('--source-file',type=Path); p.add_argument('--human',action='store_true'); p.add_argument('--verbatim',action='store_true')
    p=sub.add_parser('build'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--project-id',required=True)
    a=ap.parse_args(argv)
    if a.sub=='annotate': print(evidence.annotate(a.workspace,a.project_id,a.claim_id,a.study_id,a.relation,a.locator,a.text,a.annotator,claim_text=a.claim_text,status=a.status,source_file=a.source_file,human=a.human,verbatim=a.verbatim)); return 0
    print(evidence.build(a.workspace,a.project_id)); return 0

def dispatch(command: str, argv: list[str]) -> int:
    if command in {'research','articles'}: return _research(argv)
    if command=='review': return _review(argv)
    if command=='evidence': return _evidence(argv)
    print(f'comando nativo desconhecido: {command}',file=sys.stderr); return 2
