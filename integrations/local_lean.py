"""R913: compilação Lean local delimitada, sem aprovação sintática de fallback."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

class LocalLeanVerifier:
    def __init__(self):
        self.root=Path(__file__).resolve().parents[1]
        self.project=self.root/'livro-core/lean'
        self.lean=shutil.which('lean') or str(Path.home()/'.elan/bin/lean')

    def _runtime(self):
        if not Path(self.lean).is_file() or not Path('/usr/bin/bwrap').is_file() or not Path('/usr/bin/prlimit').is_file(): raise RuntimeError('Lean/bwrap/prlimit ausente')
        cwd=self.project if self.project.is_dir() else self.root
        result=subprocess.run([self.lean,'--print-prefix'],cwd=cwd,capture_output=True,text=True,timeout=15,check=True)
        prefix=Path(result.stdout.strip()).resolve(strict=True)
        if not (prefix/'bin/lean').is_file(): raise RuntimeError('Prefixo Lean incompleto')
        return prefix

    def _namespace(self,prefix):
        argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv']
        for path in ('/usr','/lib','/lib64'):
            if Path(path).exists(): argv+=['--ro-bind',path,path]
        return argv+['--ro-bind',str(prefix),'/opt/lean','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','HOME','/tmp','--setenv','PATH','/opt/lean/bin:/usr/bin','--chdir','/tmp']

    def status(self):
        try:
            prefix=self._runtime()
            probe=subprocess.run(self._namespace(prefix)+['/opt/lean/bin/lean','--version'],capture_output=True,text=True,timeout=15,check=True)
            return {'status':'ready','available':True,'verification':'compiler_and_namespace_probe','compiler':str(prefix/'bin/lean'),'version':probe.stdout.strip(),'network_isolated':True,'proof_executed':False}
        except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
            return {'status':'unavailable','available':False,'proof_executed':False,'reason':str(exc)}

    def verify(self,code,use_mathlib=False,timeout_seconds=30):
        from integrations.component_actions import validate_component_request
        validate_component_request('lean4',{'operation':'verify','code':code,'use_mathlib':use_mathlib,'timeout_seconds':timeout_seconds})
        base={'is_valid':False,'compiler_executed':False,'source_sha256':hashlib.sha256(code.encode()).hexdigest(),'externally_validated':False}
        # Interface para provas, não um console Lean de IO/metaprogramação.
        forbidden=r'\b(sorry|admit|axiom|unsafe|elab|macro|syntax|initialize|run_tac|run_elab|implemented_by|extern)\b|#\s*(eval|exit|run)|\bIO\s*\.'
        theorem_names=list(dict.fromkeys(re.findall(r'\b(?:theorem|lemma)\s+([A-Za-z][A-Za-z0-9_]*)(?=[\s:({\[])',code)))
        if re.search(forbidden,code) or not theorem_names:
            return {**base,'status':'source_rejected','reason':'Fonte fora da interface de provas: declaração incompleta, admissão, axioma ou comando de execução/metaprogramação.'}
        compiler_attempted=False
        try:
            prefix=self._runtime()
            argv=self._namespace(prefix)
            if use_mathlib:
                lake=Path(self.lean).parent/'lake'
                env=subprocess.run([str(lake),'env','printenv','LEAN_PATH'],cwd=self.project,capture_output=True,text=True,timeout=20,check=True).stdout.strip()
                paths=[]
                for value in env.split(':'):
                    if not value: continue
                    path=Path(value)
                    path=(path if path.is_absolute() else self.project/path).resolve()
                    if not path.is_dir(): continue
                    # Somente bibliotecas compiladas indicadas pelo projeto conhecido.
                    if path.name!='lean' or 'lib' not in path.parts: raise RuntimeError('Biblioteca Lean fora do contrato')
                    paths.append(str(path)); argv+=['--ro-bind',str(path),str(path)]
                argv+=['--setenv','LEAN_PATH',':'.join(paths)]
            with tempfile.TemporaryDirectory(prefix='core-lean-') as temp:
                work=Path(temp); source=work/'Proof.lean'
                source.write_text(code+'\n'+''.join('#print axioms '+name+'\n' for name in theorem_names),encoding='utf-8')
                argv+=['--ro-bind',str(source),'/tmp/Proof.lean','/opt/lean/bin/lean','-j','1','-M','2048','/tmp/Proof.lean']
                command=['/usr/bin/prlimit',f'--cpu={int(timeout_seconds)+1}','--as=17179869184','--fsize=2097152','--nofile=256','--',*argv]
                with (work/'compiler.log').open('w+b') as log:
                    compiler_attempted=True
                    process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=timeout_seconds,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
                    log.seek(0); output=log.read(2097152).decode('utf-8',errors='replace')
                reports=[{'theorem_name':name,'report':line} for name in theorem_names for line in output.splitlines() if line.startswith("'"+name+"'") and 'axioms' in line]
                axioms=all(any(r['theorem_name']==name for r in reports) for name in theorem_names)
                valid=process.returncode==0 and axioms and 'uses \'sorry\'' not in output
                return {**base,'status':'machine_checked' if valid else 'compiler_rejected','is_valid':valid,'compiler_executed':True,'exit_code':process.returncode,'network_isolated':True,'theorem_name':theorem_names[0],'theorem_names':theorem_names,'axiom_reports':reports,'output_log':output,'output_sha256':hashlib.sha256(output.encode()).hexdigest(),'compiler':str(prefix/'bin/lean'),'use_mathlib':use_mathlib}
        except subprocess.TimeoutExpired as exc:
            return {**base,'status':'timeout' if compiler_attempted else 'unavailable','compiler_executed':compiler_attempted,'reason':str(exc)}
        except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
            return {**base,'status':'unavailable','reason':str(exc)}
