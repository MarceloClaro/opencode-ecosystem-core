"""R928: AI Edge Quantizer por composição, ambiente próprio e demo sintética.

Não importa TensorFlow no processo Core. Fonte/lock/worker são vinculados aos
planos; não aceita modelo/receita/URL livres. Não faz conversão genérica de LLMs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import time
import urllib.parse
import urllib.request

from academic.adversarial_research.service import _write_json
from integrations.itsfine_core import ItsFineCore, _canonical, _json, _read, _sha
from integrations.itsfine_lifecycle import run_bounded, _public_process, _positive_timeout, _python312

REPO = 'MarceloClaro/ai-edge-quantizer'
COMMIT = '87cda53576a55a71114a4945b3ff18e27c2fa42b'
CACHE = '.ai-edge-quantizer'
LOCK = 'integrations/ai-edge-quantizer-locks/py312.txt'
WORKER = 'integrations/ai_edge_quantizer_worker.py'
ARTIFACTS = {'float.tflite','quantized.tflite','recipe.json','evaluation.json','metrics.json'}


def _flags():
    return {'training_executed':False,'external_checkpoint_downloaded':False,
            'user_data_read':False,'policy_modified':False,'externally_validated':False,
            'confidence_promoted':False}


def _seal(value, key='plan_sha256'):
    return {**value,key:_sha(_canonical(value))}


def _relative(value):
    if (not isinstance(value,str) or not value or '\\' in value or ':' in value or
        any(ord(c)<32 for c in value) or any(p in {'','.','..'} for p in value.split('/')) or
        PurePosixPath(value).is_absolute()):
        raise ValueError('unsafe_edge_path')
    return value


def _run_id(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',value):
        raise ValueError('invalid_edge_run_id')
    return value


def _blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def _source_file(path):
    if path in {'LICENSE','setup.py','requirements.txt'}: return True
    parts=PurePosixPath(path).parts
    return (path.startswith('ai_edge_quantizer/') and not any(p in {'tests','colabs','__pycache__'} for p in parts)
        and not path.endswith('_test.py') and parts[-1]!='test_utils.py'
        and PurePosixPath(path).suffix in {'.py','.json'})


def _download(url, limit=1024*1024, timeout=20):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in {'api.github.com','raw.githubusercontent.com'}:
        raise ValueError('untrusted_edge_source_url')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*_a,**_kw): raise ValueError('edge_source_redirect_refused')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    request=urllib.request.Request(url,headers={'User-Agent':'OpenCode-Core-R928','Accept':'application/vnd.github+json'})
    with opener.open(request,timeout=timeout) as response:
        raw=response.read(limit+1)
    if len(raw)>limit: raise ValueError('edge_source_size_limit')
    return raw


def validate_config(config):
    fields={'status':set(),'source_plan':set(),'acquire_source':{'plan','confirm','timeout_seconds'},
        'environment_plan':set(),'prepare':{'plan','confirm','timeout_seconds'},
        'demo_plan':{'run_id'},'demo':{'plan','confirm','timeout_seconds'},'report':{'run_id'}}
    if (not isinstance(config,dict) or config.get('operation') not in fields or
        set(config)-fields[config['operation']]-{'operation'}):
        raise ValueError('unknown_edge_operation_or_fields')
    if config['operation'] in {'acquire_source','prepare','demo'} and not isinstance(config.get('plan'),dict):
        raise ValueError('edge_plan_required')
    if config['operation']=='report' and not isinstance(config.get('run_id'),str):
        raise ValueError('edge_run_id_required')
    return dict(config)


def validate_metrics(data):
    if not isinstance(data,dict): raise ValueError('invalid_edge_metrics')
    for key in ('conversion_max_abs','quantized_mse','quantized_max_abs','float_bytes','quantized_bytes','int8_tensor_count','samples'):
        value=data.get(key)
        if type(value) not in (int,float) or not math.isfinite(value) or value<0:
            raise ValueError('nonfinite_or_invalid_edge_metrics')
    if (data['conversion_max_abs']>1e-4 or data['quantized_mse']>1e-3 or data['quantized_max_abs']>0.1 or
        type(data['int8_tensor_count']) is not int or data['int8_tensor_count']<1 or
        data['samples']!=16 or not 8<=data['float_bytes']<=4*1024*1024 or
        not 8<=data['quantized_bytes']<=4*1024*1024):
        raise ValueError('edge_numeric_smoke_gate_failed')
    return True


class EdgeQuantizerCore:
    def __init__(self,root):
        self.paths=ItsFineCore(root); self.root=self.paths.root
        self.cache=self.paths._path(CACHE)

    def _path(self,relative): return self.paths._path(relative)

    def _policy(self):
        path=self._path('.its-fine/policy.json')
        return _sha(_read(path,131072)) if path.exists() else None

    def _source_state(self):
        raw=_read(self._path(CACHE+'/source-manifest.json'),2*1024*1024); manifest=_json(raw)
        if (not isinstance(manifest,dict) or manifest.get('repo')!=REPO or manifest.get('commit')!=COMMIT
            or not isinstance(manifest.get('files'),dict) or not 1<=len(manifest['files'])<=256):
            raise ValueError('invalid_edge_source_manifest')
        required={'LICENSE','setup.py','ai_edge_quantizer/__init__.py','ai_edge_quantizer/quantizer.py','ai_edge_quantizer/recipe.py'}
        if not required<=set(manifest['files']): raise ValueError('incomplete_edge_source')
        total=0
        for relative,row in manifest['files'].items():
            _relative(relative)
            if not _source_file(relative) or not isinstance(row,dict): raise ValueError('unsafe_edge_source_manifest')
            data=_read(self._path(CACHE+'/source/'+relative),1024*1024); total+=len(data)
            if total>8*1024*1024 or len(data)!=row.get('bytes') or _sha(data)!=row.get('sha256') or _blob(data)!=row.get('git_blob_sha1'):
                raise ValueError('edge_source_integrity_failed')
        return {'manifest':manifest,'source_manifest_sha256':_sha(raw)}

    def _lock_state(self):
        raw=_read(self._path(LOCK),2*1024*1024)
        text=raw.decode('utf-8')
        if '--hash=sha256:' not in text or '==' not in text: raise ValueError('unhashed_edge_lock')
        for url in re.findall(r'https?://[^\s\\]+',text):
            if urllib.parse.urlsplit(url).hostname not in {'pypi.org','files.pythonhosted.org'}:
                raise ValueError('untrusted_edge_dependency_index')
        return _sha(raw)

    def _environment_receipt(self):
        raw=_read(self._path(CACHE+'/environment.json'),2*1024*1024); receipt=_json(raw)
        if not isinstance(receipt,dict) or receipt.get('receipt_sha256')!=_sha(_canonical({k:v for k,v in receipt.items() if k!='receipt_sha256'})):
            raise ValueError('invalid_edge_environment_receipt')
        expected=self.environment_plan()
        if any(receipt.get(k)!=expected[k] for k in ('source_manifest_sha256','lock_sha256','worker_sha256','environment','commit')):
            raise ValueError('stale_edge_environment')
        if receipt.get('status')!='imports_verified_cpu': raise ValueError('edge_environment_not_prepared')
        python=Path(expected['environment'])/'bin/python'
        if not python.is_file(): raise ValueError('edge_environment_missing')
        if (receipt.get('python_fingerprint')!=_sha(_read(python.resolve(strict=True),32*1024*1024)) or
            receipt.get('pyvenv_sha256')!=_sha(_read(self._path(CACHE+'/venv/pyvenv.cfg'),65536))):
            raise ValueError('edge_python_identity_changed')
        marker=_json(_read(self._path(CACHE+'/venv/core-environment.json'),65536))
        if marker.get('kind')!='core_edge_quantizer_environment_v1' or marker.get('root')!=str(self.root):
            raise ValueError('foreign_edge_environment')
        return {**receipt,'python':str(python)}

    def status(self):
        source=environment=False
        try: self._source_state(); source=True
        except (ValueError,OSError): pass
        if source:
            try: self._environment_receipt(); environment=True
            except (ValueError,OSError): pass
        return {'repo':REPO,'commit':COMMIT,'source_ready':source,'environment_ready':environment,
            'verification':'local_receipts_not_quantization_execution','synthetic_inference_executed':False,**_flags()}

    def source_plan(self):
        return _seal({'kind':'edge_source','repo':REPO,'commit':COMMIT,'root':str(self.root),
            'policy_sha256':self._policy(),'execution_started':False,**_flags()})

    def acquire_source(self,plan,confirm=False,timeout_seconds=300):
        _positive_timeout(timeout_seconds,600)
        if confirm is not True or _canonical(plan)!=_canonical(self.source_plan()):
            raise ValueError('edge_source_confirmation_or_plan_invalid')
        if self._path(CACHE+'/source').exists():
            state=self._source_state()
            return {'status':'source_verified',**state,**_flags()}
        deadline=time.monotonic()+timeout_seconds
        tree=_json(_download(f'https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1',timeout=min(timeout_seconds,30)))
        if not isinstance(tree,dict) or tree.get('truncated') is not False or not isinstance(tree.get('tree'),list) or len(tree['tree'])>2048:
            raise ValueError('invalid_or_truncated_edge_tree')
        selected=[]; seen=set(); total=0
        for row in tree['tree']:
            if not isinstance(row,dict) or not isinstance(row.get('path'),str): raise ValueError('invalid_edge_tree_entry')
            name=row['path']
            if not _source_file(name): continue
            _relative(name)
            if (name in seen or row.get('type')!='blob' or row.get('mode')!='100644' or
                type(row.get('size')) is not int or not 0<=row['size']<=1024*1024 or
                not re.fullmatch(r'[a-f0-9]{40}',str(row.get('sha','')))):
                raise ValueError('unsafe_edge_source_entry')
            seen.add(name); selected.append(row); total+=row['size']
            if len(selected)>256 or total>8*1024*1024: raise ValueError('edge_source_limit')
        self.cache.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(dir=self.cache,prefix='.source-'))
        files={}
        try:
            for row in sorted(selected,key=lambda r:r['path']):
                remaining=deadline-time.monotonic()
                if remaining<=0: raise ValueError('edge_source_timeout')
                raw=_download(f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/'+urllib.parse.quote(row['path'],safe='/'),
                              limit=1024*1024,timeout=min(remaining,30))
                if len(raw)!=row['size'] or _blob(raw)!=row['sha']: raise ValueError('edge_git_blob_mismatch')
                raw.decode('utf-8')
                if b'\0' in raw: raise ValueError('binary_edge_source_refused')
                path=stage/row['path']; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
                files[row['path']]={'sha256':_sha(raw),'git_blob_sha1':row['sha'],'bytes':len(raw)}
            if not {'LICENSE','setup.py','ai_edge_quantizer/quantizer.py','ai_edge_quantizer/recipe.py'}<=set(files):
                raise ValueError('edge_source_required_files_missing')
            license_text=(stage/'LICENSE').read_text()
            if 'Apache License' not in license_text or 'Version 2.0' not in license_text: raise ValueError('edge_license_unconfirmed')
            if self._policy()!=plan['policy_sha256']: raise ValueError('policy_changed_during_edge_acquisition')
            target=self._path(CACHE+'/source')
            if target.exists(): raise ValueError('edge_source_conflict')
            os.rename(stage,target)
            manifest={'schema_version':1,'repo':REPO,'commit':COMMIT,'files':files}
            _write_json(self._path(CACHE+'/source-manifest.json'),manifest)
        finally:
            if stage.exists(): shutil.rmtree(stage)
        return {'status':'source_verified','source_manifest_sha256':self._source_state()['source_manifest_sha256'],
                'source_files':len(files),**_flags()}

    def environment_plan(self):
        state=self._source_state()
        return _seal({'kind':'edge_environment','root':str(self.root),'commit':COMMIT,
            'environment':str(self._path(CACHE+'/venv')),'python_base':_python312(),'uv':shutil.which('uv'),
            'source_manifest_sha256':state['source_manifest_sha256'],'lock_sha256':self._lock_state(),
            'worker_sha256':_sha(_read(self._path(WORKER),1024*1024)),
            'policy_sha256':self._policy(),'execution_started':False,**_flags()})

    def _runtime_prefix(self,python):
        binary=Path(python).resolve(strict=True); prefix=binary.parent.parent
        if not (prefix/'lib/python3.12').is_dir(): raise ValueError('unsupported_edge_python_layout')
        return prefix

    def _sandbox_argv(self,runtime,environment,work,operation):
        runtime,environment,work=Path(runtime),Path(environment),Path(work)
        if runtime==self.root or self.root.is_relative_to(runtime): raise ValueError('edge_runtime_mount_too_broad')
        if operation not in {'probe','demo'}: raise ValueError('unknown_edge_worker_operation')
        argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv']
        for path in ('/usr','/lib','/lib64'):
            if Path(path).exists(): argv+=['--ro-bind',path,path]
        if not runtime.is_relative_to('/usr'): argv+=['--ro-bind',str(runtime),str(runtime)]
        config=environment/'pyvenv.cfg'
        if config.is_file():
            text=_read(config,65536).decode('utf-8')
            home=re.search(r'(?m)^home\s*=\s*(.+?)\s*$',text)
            if not home: raise ValueError('edge_python_home_missing')
            declared=Path(home[1]).parent
            if declared!=runtime:
                # uv pode usar um alias versionless; montar só o mesmo prefixo
                # Python nesse alias, nunca ~/.local/bin ou workspace completos.
                if (not declared.is_absolute() or declared.parent!=runtime.parent or
                    not re.fullmatch(r'cpython-3\.12-[A-Za-z0-9_-]+',declared.name)):
                    raise ValueError('untrusted_edge_python_alias')
                argv+=['--ro-bind',str(runtime),str(declared)]
        argv+=['--ro-bind',str(environment),str(environment),
            '--ro-bind',str(self._path(CACHE+'/source')),'/source',
            '--ro-bind',str(self._path(WORKER)),'/worker.py','--bind',str(work),'/work',
            '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','HOME','/tmp',
            '--setenv','PATH','/usr/bin:/bin','--setenv','CUDA_VISIBLE_DEVICES','-1',
            '--setenv','OMP_NUM_THREADS','1','--setenv','TF_NUM_INTEROP_THREADS','1',
            '--setenv','TF_NUM_INTRAOP_THREADS','1','--setenv','TF_CPP_MIN_LOG_LEVEL','2',
            '--chdir','/work',str(environment/'bin/python'),'-I','-B','/worker.py',operation,'--directory','/work']
        return argv

    def prepare(self,plan,confirm=False,timeout_seconds=900):
        _positive_timeout(timeout_seconds)
        if confirm is not True or _canonical(plan)!=_canonical(self.environment_plan()):
            raise ValueError('edge_environment_confirmation_or_plan_invalid')
        environment=self._path(CACHE+'/venv'); marker=environment/'core-environment.json'
        if environment.exists() and not marker.is_file(): raise ValueError('foreign_edge_environment_preserved')
        if marker.exists() and _json(_read(marker,65536)).get('root')!=str(self.root): raise ValueError('foreign_edge_environment_preserved')
        if not plan['uv']: raise ValueError('uv_required')
        deadline=time.monotonic()+timeout_seconds; receipts=[]
        if not environment.exists():
            remaining=deadline-time.monotonic()
            if remaining<=0: return {'status':'preparation_failed','reason':'timeout',**_flags()}
            result=run_bounded([plan['uv'],'--no-config','venv','--python',plan['python_base'],str(environment)],
                               cwd=self.root,timeout_seconds=remaining)
            receipts.append(_public_process(result))
            if result['status']!='completed' or result['returncode']!=0: return {'status':'preparation_failed','processes':receipts,**_flags()}
            _write_json(marker,{'kind':'core_edge_quantizer_environment_v1','root':str(self.root),'group':'edge-quantizer'})
        python=environment/'bin/python'
        commands=[[plan['uv'],'--no-config','pip','sync','--python',str(python),'--require-hashes','--only-binary',':all:',str(self._path(LOCK))],
                  [plan['uv'],'--no-config','pip','check','--python',str(python)]]
        for argv in commands:
            if self._policy()!=plan['policy_sha256'] or self._lock_state()!=plan['lock_sha256']: raise ValueError('edge_inputs_changed')
            remaining=deadline-time.monotonic()
            if remaining<=0: return {'status':'preparation_failed','reason':'timeout',**_flags()}
            result=run_bounded(argv,cwd=self.root,timeout_seconds=remaining)
            receipts.append(_public_process(result))
            if result['status']!='completed' or result['returncode']!=0: return {'status':'preparation_failed','processes':receipts,**_flags()}
        remaining=deadline-time.monotonic()
        if remaining<=0: return {'status':'preparation_failed','reason':'timeout',**_flags()}
        with tempfile.TemporaryDirectory(dir=self.cache,prefix='.probe-') as work:
            result=run_bounded(self._sandbox_argv(self._runtime_prefix(python),environment,Path(work),'probe'),
                cwd=self.root,timeout_seconds=remaining)
        receipts.append(_public_process(result))
        if result['status']!='completed' or result['returncode']!=0:
            return {'status':'preparation_failed','processes':receipts,**_flags()}
        probe=self._worker_message(result['stdout'])
        if (probe.get('status')!='imports_verified_cpu' or not str(probe.get('python','')).startswith('3.12.')
            or self._policy()!=plan['policy_sha256']):
            raise ValueError('edge_probe_identity_or_policy_changed')
        receipt={key:plan[key] for key in ('commit','environment','source_manifest_sha256','lock_sha256','worker_sha256')}
        receipt.update(status='imports_verified_cpu',probe=probe,processes=receipts,
            python_fingerprint=_sha(_read(python.resolve(strict=True),32*1024*1024)),
            pyvenv_sha256=_sha(_read(self._path(CACHE+'/venv/pyvenv.cfg'),65536)),
            synthetic_inference_executed=False,**_flags())
        receipt=_seal(receipt,'receipt_sha256'); _write_json(self._path(CACHE+'/environment.json'),receipt)
        return receipt

    @staticmethod
    def _worker_message(stdout):
        for line in reversed(stdout.splitlines()):
            if line.startswith(b'EDGE_QUANTIZER_RESULT='):
                value=_json(line.split(b'=',1)[1])
                if isinstance(value,dict): return value
        raise ValueError('invalid_edge_worker_response')

    def demo_plan(self,run_id='synthetic-int8'):
        _run_id(run_id); environment=self._environment_receipt(); state=self._source_state()
        return _seal({'kind':'edge_synthetic_demo','root':str(self.root),'run_id':run_id,'commit':COMMIT,
            'environment_sha256':environment['receipt_sha256'],'source_manifest_sha256':state['source_manifest_sha256'],
            'lock_sha256':self._lock_state(),'worker_sha256':_sha(_read(self._path(WORKER),1024*1024)),
            'policy_sha256':self._policy(),'recipe':'dynamic_wi8_afp32','seed':42,'samples':16,
            'input_width':32,'output_width':64,'execution_started':False,'synthetic_inference_executed':False,**_flags()})

    def _artifacts(self,directory):
        rows={}
        for name in ARTIFACTS:
            path=directory/name
            raw=_read(path,4*1024*1024)
            if name.endswith('.tflite') and (len(raw)<8 or raw[4:8]!=b'TFL3'):
                raise ValueError('invalid_edge_flatbuffer')
            rows[name]={'sha256':_sha(raw),'bytes':len(raw)}
        return rows

    def _metrics(self,directory,artifacts):
        metrics=_json(_read(directory/'metrics.json',1024*1024)); validate_metrics(metrics)
        data=_json(_read(directory/'evaluation.json',1024*1024))
        vectors=[]
        for key in ('float','quantized','reference'):
            rows=data.get(key) if isinstance(data,dict) else None
            if not isinstance(rows,list) or len(rows)!=16 or any(not isinstance(r,list) or len(r)!=64 for r in rows):
                raise ValueError('invalid_edge_evaluation_shape')
            flat=[v for row in rows for v in row]
            if any(type(v) not in (int,float) or not math.isfinite(v) for v in flat): raise ValueError('invalid_edge_evaluation_value')
            vectors.append(flat)
        fp,quant,reference=vectors
        actual={'conversion_max_abs':max(abs(a-b) for a,b in zip(fp,reference)),
            'quantized_mse':math.fsum((a-b)**2 for a,b in zip(fp,quant))/len(fp),
            'quantized_max_abs':max(abs(a-b) for a,b in zip(fp,quant))}
        if any(abs(metrics[k]-v)>1e-10 for k,v in actual.items()): raise ValueError('edge_metrics_not_reproduced')
        if metrics['float_bytes']!=artifacts['float.tflite']['bytes'] or metrics['quantized_bytes']!=artifacts['quantized.tflite']['bytes']:
            raise ValueError('edge_model_size_mismatch')
        return {**metrics,**actual,'numeric_gate_scope':'synthetic_not_task_quality'}

    def demo(self,plan,confirm=False,timeout_seconds=180):
        _positive_timeout(timeout_seconds,600)
        if confirm is not True or not isinstance(plan,dict) or _canonical(plan)!=_canonical(self.demo_plan(plan.get('run_id'))):
            raise ValueError('edge_demo_confirmation_or_plan_invalid')
        target=self._path(CACHE+'/runs/'+plan['run_id'])
        if target.exists():
            report=self.report(plan['run_id'])
            if report.get('plan_sha256')!=plan['plan_sha256']: raise ValueError('edge_run_conflict')
            return report
        target.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(dir=target.parent,prefix='.stage-edgeq-'))
        try:
            environment=self._environment_receipt(); env_path=self._path(CACHE+'/venv')
            result=run_bounded(self._sandbox_argv(self._runtime_prefix(environment['python']),env_path,stage,'demo'),
                               cwd=self.root,timeout_seconds=timeout_seconds)
            if result['status']!='completed' or result['returncode']!=0:
                return {'status':'worker_failed','run_id':plan['run_id'],'process':_public_process(result),
                        'synthetic_inference_executed':None,**_flags()}
            self._worker_message(result['stdout'])
            artifacts=self._artifacts(stage); metrics=self._metrics(stage,artifacts)
            if self._policy()!=plan['policy_sha256']: raise ValueError('edge_policy_changed')
            report=_seal({'status':'synthetic_smoke_passed','run_id':plan['run_id'],'plan_sha256':plan['plan_sha256'],
                'commit':COMMIT,'artifacts':artifacts,'metrics':metrics,'process':_public_process(result),
                'synthetic_inference_executed':True,'quantization_executed':True,**_flags()},'report_sha256')
            _write_json(stage/'manifest.json',report)
            if target.exists(): raise ValueError('edge_run_conflict')
            os.rename(stage,target)
            return report
        finally:
            if stage.exists(): shutil.rmtree(stage)

    def report(self,run_id):
        _run_id(run_id); directory=self._path(CACHE+'/runs/'+run_id)
        if not directory.is_dir(): raise ValueError('edge_run_not_found')
        report=_json(_read(directory/'manifest.json',2*1024*1024))
        if (not isinstance(report,dict) or report.get('report_sha256')!=_sha(_canonical({k:v for k,v in report.items() if k!='report_sha256'}))
            or report.get('run_id')!=run_id or report.get('status')!='synthetic_smoke_passed'
            or report.get('commit')!=COMMIT
            or any(report.get(key) is not value for key,value in _flags().items())
            or report.get('synthetic_inference_executed') is not True or report.get('quantization_executed') is not True
            or not isinstance(report.get('artifacts'),dict) or set(report['artifacts'])!=ARTIFACTS):
            raise ValueError('invalid_edge_report')
        if report['artifacts']!=self._artifacts(directory): raise ValueError('edge_artifact_integrity_failed')
        if _canonical(report.get('metrics'))!=_canonical(self._metrics(directory,report['artifacts'])):
            raise ValueError('edge_report_numeric_drift')
        return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=('status','source-plan','acquire-source','environment-plan','prepare','demo-plan','demo','report'))
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--confirm',action='store_true'); parser.add_argument('--run-id',default='synthetic-int8')
    parser.add_argument('--timeout',type=float)
    args=parser.parse_args(argv); core=EdgeQuantizerCore(args.root)
    try:
        op=args.operation.replace('-','_')
        if op in {'status','source_plan','environment_plan'}: result=getattr(core,op)()
        elif op=='acquire_source': result=core.acquire_source(core.source_plan(),args.confirm,args.timeout if args.timeout is not None else 300)
        elif op=='prepare': result=core.prepare(core.environment_plan(),args.confirm,args.timeout if args.timeout is not None else 900)
        elif op=='demo_plan': result=core.demo_plan(args.run_id)
        elif op=='demo': result=core.demo(core.demo_plan(args.run_id),args.confirm,args.timeout if args.timeout is not None else 180)
        else: result=core.report(args.run_id)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 1 if result.get('status') in {'worker_failed','preparation_failed'} else 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'status':'blocked','reason':str(exc)[:160],**_flags()})); return 2


if __name__=='__main__': raise SystemExit(main())
