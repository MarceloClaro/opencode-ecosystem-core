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
        forbidden=r'\b(sorry|sorryAx|admit|axiom|unsafe|elab|macro|syntax|initialize|run_tac|run_elab|implemented_by|extern)\b|#\s*(eval|exit|run)|\bIO\s*\.'
        theorem=re.search(r'\b(?:theorem|lemma)\s+([A-Za-z][A-Za-z0-9_]*)\s',code)
        declarations=re.findall(r'\b(?:theorem|lemma)\s+',code)
        if re.search(forbidden,code) or not theorem or len(declarations)!=1:
            return {**base,'status':'source_rejected','reason':'Fonte fora da interface de provas: declaração incompleta, admissão, axioma ou comando de execução/metaprogramação.'}
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
                source.write_text(code+'\n#print axioms '+theorem[1]+'\n',encoding='utf-8')
                argv+=['--ro-bind',str(source),'/tmp/Proof.lean','/opt/lean/bin/lean','-j','1','-M','2048','/tmp/Proof.lean']
                # R923: Lean 4.34.1 não conseguiu criar thread sob 4 GiB de
                # espaço virtual neste host. 6 GiB passaram na prova positiva;
                # heap (-M2048), CPU, arquivos e isolamento continuam limitados.
                command=['/usr/bin/prlimit',f'--cpu={int(timeout_seconds)+1}','--as=6442450944','--fsize=2097152','--nofile=256','--',*argv]
                with (work/'compiler.log').open('w+b') as log:
                    process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=timeout_seconds,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
                    log.seek(0); output=log.read(2097152).decode('utf-8',errors='replace')
                # Um processo Lean com exit=0 pode ter usado sorryAx. Só a
                # presença da palavra axioms não constitui evidência aceitável.
                reports=[line.strip() for line in output.splitlines() if line.startswith("'"+theorem[1]+"'")]
                no_axioms="'"+theorem[1]+"' does not depend on any axioms" in reports
                names=[]; reported=no_axioms
                for line in reports:
                    match=re.fullmatch(re.escape("'"+theorem[1]+"'")+r' depends on axioms: \[([^\]]*)\]',line)
                    if match:
                        names=[name.strip() for name in match[1].split(',') if name.strip()]
                        reported=True
                allowed={'propext','Classical.choice','Quot.sound'}
                rejected_axioms=sorted(set(names)-allowed)
                valid=(process.returncode==0 and reported and not rejected_axioms
                       and not re.search(r'\bsorryAx\b|uses [\'\"]sorry[\'\"]',output))
                resource=bool(process.returncode and re.search(r'failed to create thread|out of memory|cannot allocate memory|memory exhausted',output,re.I))
                status='machine_checked' if valid else 'resource_exhausted' if resource else 'compiler_rejected'
                return {**base,'status':status,'is_valid':valid,'compiler_executed':True,'exit_code':process.returncode,'network_isolated':True,'theorem_name':theorem[1],'axioms':names,'rejected_axioms':rejected_axioms,'resource_failure':resource,'output_log':output,'output_sha256':hashlib.sha256(output.encode()).hexdigest(),'compiler':str(prefix/'bin/lean'),'use_mathlib':use_mathlib}
        except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
            return {**base,'status':'unavailable','reason':str(exc)}
