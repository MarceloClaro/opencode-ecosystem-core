"""R913: endpoint CPU sob demanda, serializado e encerrado após uso."""
from contextlib import contextmanager
import fcntl,hashlib,os,signal,socket,subprocess,time,urllib.request
from pathlib import Path
from integrations.live_scientific_runtime import local_model_opener

@contextmanager
def managed_endpoint(config):
    if config.get('base_url')!='http://127.0.0.1:11436/v1': raise ValueError('Endpoint gerenciado fora do contrato')
    binary=Path(config.get('binary','')).resolve()
    model=Path(config.get('model_path','')).resolve()
    if not binary.is_file() or not model.is_file() or not os.access(binary,os.X_OK): raise ValueError('Servidor/modelo local não instalado')
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=config.get('binary_sha256') or model.stat().st_size!=config.get('model_bytes'): raise ValueError('Identidade do servidor/modelo mudou')
    state=Path.home()/'.local/share/opencode-core/mirofish-model-state'
    state.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (state/'endpoint.lock').open('a') as lock:
        deadline=time.monotonic()+10
        while True:
            try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
            except BlockingIOError:
                if time.monotonic()>=deadline: raise RuntimeError('Modelo local em uso por outra análise')
                time.sleep(.1)
        process=None
        lifecycle={'started_for_this_run':False,'stopped_after_run':False,'model':config['model'],'base_url':config['base_url']}
        try:
            with socket.socket() as available: available.bind(('127.0.0.1',11436))
            environment={k:os.environ[k] for k in ('HOME','PATH','LANG') if k in os.environ}
            environment['LD_LIBRARY_PATH']=str(binary.parent)
            argv=[str(binary),'-m',str(model),'--alias',config['model'],'--host','127.0.0.1','--port','11436','-c','2048','-t','2','-np','1','-ngl','0','--load-mode','none','--no-warmup','--jinja']
            with (state/'server.log').open('ab') as log:
                process=subprocess.Popen(argv,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            lifecycle.update(started_for_this_run=True,pid=process.pid)
            deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                if process.poll() is not None: raise RuntimeError('Servidor CPU encerrou durante inicialização')
                try:
                    with local_model_opener().open('http://127.0.0.1:11436/health',timeout=1) as response:
                        if response.status==200: break
                except OSError: time.sleep(.25)
            else: raise RuntimeError('Servidor CPU não ficou pronto no prazo')
            yield lifecycle
        finally:
            if process is not None:
                if process.poll() is None:
                    os.killpg(process.pid,signal.SIGTERM)
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)
                lifecycle['stopped_after_run']=process.poll() is not None
            fcntl.flock(lock,fcntl.LOCK_UN)
