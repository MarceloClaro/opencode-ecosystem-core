from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from . import research, review, evidence

def _research(argv):
    ap=argparse.ArgumentParser(prog='scientific_lab research'); sub=ap.add_subparsers(dest='sub',required=True)
    for name in ('search','harvest'):
        p=sub.add_parser(name); p.add_argument('query'); p.add_argument('--workspace',type=Path,default=Path.cwd()); p.add_argument('--limit',type=int,default=30); p.add_argument('--per-platform',type=int,default=5); p.add_argument('--platforms'); p.add_argument('--max-downloads',type=int,default=10)
    project=sub.add_parser('project')
    project.add_argument('--theme',required=True); project.add_argument('--out',type=Path,required=True); project.add_argument('--question'); project.add_argument('--sources'); project.add_argument('--limit',type=int,default=30); project.add_argument('--per-platform',type=int,default=5); project.add_argument('--timeout',type=int,default=90); project.add_argument('--dry-run',action='store_true'); project.add_argument('--corpus',type=Path)
    project.add_argument('--fulltext-dir',type=Path); project.add_argument('--fulltext-approval',type=Path); project.add_argument('--allow-open-access',action='store_true'); project.add_argument('--max-downloads',type=int,default=5); project.add_argument('--check-integrity',action='store_true'); project.add_argument('--max-integrity-checks',type=int,default=20); project.add_argument('--quantitative-data',type=Path); project.add_argument('--submission',action='store_true'); project.add_argument('--journal'); project.add_argument('--journal-profile'); project.add_argument('--figures-dir',type=Path); project.add_argument('--tables-dir',type=Path)
    refresh=sub.add_parser('refresh')
    refresh.add_argument('--out',type=Path,required=True); refresh.add_argument('--fulltext-dir',type=Path); refresh.add_argument('--fulltext-approval',type=Path); refresh.add_argument('--allow-open-access',action='store_true'); refresh.add_argument('--max-downloads',type=int,default=5); refresh.add_argument('--check-integrity',action='store_true'); refresh.add_argument('--max-integrity-checks',type=int,default=20); refresh.add_argument('--quantitative-data',type=Path); refresh.add_argument('--submission',action='store_true'); refresh.add_argument('--journal'); refresh.add_argument('--journal-profile'); refresh.add_argument('--figures-dir',type=Path); refresh.add_argument('--tables-dir',type=Path)
    submission_cmd=sub.add_parser('submission')
    submission_cmd.add_argument('--out',type=Path,required=True); submission_cmd.add_argument('--journal'); submission_cmd.add_argument('--journal-profile'); submission_cmd.add_argument('--figures-dir',type=Path); submission_cmd.add_argument('--tables-dir',type=Path)
    benchmark=sub.add_parser('benchmark-meta')
    benchmark.add_argument('--data',type=Path,required=True); benchmark.add_argument('--reference',type=Path,required=True); benchmark.add_argument('--out',type=Path)
    extract=sub.add_parser('extract-effects')
    extract.add_argument('--out',type=Path,required=True); extract.add_argument('--fulltext-dir',type=Path,required=True); extract.add_argument('--reviewer',required=True); extract.add_argument('--confirm',action='store_true')
    auto=sub.add_parser('auto-rob-grade')
    auto.add_argument('--out',type=Path,required=True); auto.add_argument('--data',type=Path,required=True); auto.add_argument('--fulltext-dir',type=Path,required=True); auto.add_argument('--reviewer',required=True); auto.add_argument('--confirm',action='store_true')
    pub=sub.add_parser('publication-gate')
    pub.add_argument('--out',type=Path,required=True); pub.add_argument('--attach-external',type=Path); pub.add_argument('--attach-acceptance',type=Path); pub.add_argument('--attach-authorization',type=Path)
    submit_cmd=sub.add_parser('submit')
    submit_cmd.add_argument('--out',type=Path,required=True); submit_cmd.add_argument('--profile'); submit_cmd.add_argument('--confirm',action='store_true')
    a=ap.parse_args(argv)
    def project_data(out):
        source=json.loads((out/'01_sources/source-records.json').read_text(encoding='utf-8'))
        studies=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((out/'01_sources/systematic_review/studies').glob('*.json'))]
        return studies, source.get('records', [])
    if a.sub=='benchmark-meta':
        from scientific_lab import real_benchmark
        result=real_benchmark.run(a.data,a.reference,out=a.out)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']=='pass' else 4
    if a.sub=='extract-effects':
        if not a.confirm:
            print(json.dumps({'status':'blocked','reason':'explicit_confirmation_required'},ensure_ascii=False,indent=2)); return 4
        from scientific_lab import effect_extraction
        studies,records=project_data(a.out)
        result=effect_extraction.run(a.out,a.fulltext_dir,studies,records,reviewer=a.reviewer,human_confirmation=True)
        print(json.dumps({'status':result['draft']['status'],'candidates':result['candidates']['count'],'draft_studies':len(result['draft']['studies']),'truth_claim':False,'human_review_required':True},ensure_ascii=False,indent=2)); return 0
    if a.sub=='auto-rob-grade':
        if not a.confirm:
            print(json.dumps({'status':'blocked','reason':'explicit_confirmation_required'},ensure_ascii=False,indent=2)); return 4
        from scientific_lab import rob_grade_auto
        studies,records=project_data(a.out)
        data=json.loads(a.data.read_text(encoding='utf-8'))
        texts=rob_grade_auto.texts_by_study(a.fulltext_dir,studies,records)
        result=rob_grade_auto.enrich(data,texts,reviewer=a.reviewer,human_confirmation=True,out=a.out)
        print(json.dumps({'status':result['report']['status'],'grade':result['report']['grade']['final_level_preview'],'k':result['final_meta']['k'],'truth_claim':False,'human_review_required':True},ensure_ascii=False,indent=2)); return 0
    if a.sub=='publication-gate':
        from scientific_lab import external_validation
        if a.attach_external: external_validation.attach_external_validation(a.out,a.attach_external)
        if a.attach_acceptance: external_validation.attach_acceptance(a.out,a.attach_acceptance)
        if a.attach_authorization: external_validation.attach_authorization(a.out,a.attach_authorization)
        result=external_validation.publication_gate(a.out)
        external_validation.write_gate(a.out,result)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']=='cleared_for_publication' else 4
    if a.sub=='submit':
        from scientific_lab import submission_portal
        result=submission_portal.submit(a.out,profile_id=a.profile,confirm=a.confirm)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']=='submitted' else 4
    if a.sub=='project':
        from scientific_lab import research_project
        selected=[x.strip() for x in a.sources.split(',') if x.strip()] if a.sources else None
        result=research_project.run(a.theme,a.out,question=a.question,sources=selected,dry_run=a.dry_run,limit=a.limit,per_platform=a.per_platform,timeout_seconds=a.timeout,corpus_path=a.corpus,fulltext_dir=a.fulltext_dir,fulltext_approval=a.fulltext_approval,allow_open_access=a.allow_open_access,max_downloads=a.max_downloads,check_integrity=a.check_integrity,max_integrity_checks=a.max_integrity_checks,quantitative_data=a.quantitative_data,submission_package=a.submission,journal=a.journal,journal_profile_id=a.journal_profile,figures_dir=a.figures_dir,tables_dir=a.tables_dir)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']!='blocked' else 4
    if a.sub=='refresh':
        from scientific_lab import research_project
        result=research_project.refresh_project(a.out,fulltext_dir=a.fulltext_dir,fulltext_approval=a.fulltext_approval,allow_open_access=a.allow_open_access,max_downloads=a.max_downloads,check_integrity=a.check_integrity,max_integrity_checks=a.max_integrity_checks,quantitative_data=a.quantitative_data,submission_package=a.submission,journal=a.journal,journal_profile_id=a.journal_profile,figures_dir=a.figures_dir,tables_dir=a.tables_dir)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']!='blocked' else 4
    if a.sub=='submission':
        from scientific_lab import research_project
        result=research_project.refresh_project(a.out,submission_package=True,journal=a.journal,journal_profile_id=a.journal_profile,figures_dir=a.figures_dir,tables_dir=a.tables_dir)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['status']!='blocked' else 4
    platforms=[x.strip() for x in a.platforms.split(',') if x.strip()] if a.platforms else None
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
