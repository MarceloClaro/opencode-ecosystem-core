# Evidências R929

`receipt.json` relaciona fontes, hashes, preservação do histórico, revisão por
leitura e limites. `verified.xml` é o resultado da seleção final; não é o
resultado da suíte integral. `baseline.json` e `final.json` documentam tentativas
globais interrompidas pelo prazo, sem aprovação. `doctor.json` é o diagnóstico
estrutural após o registro do ciclo.

Os arquivos `red-*.xml` registram contraprovas anteriores às correções.
Em `red.xml`, três falhas de fixture não contam como RED válido; o teste
corrigido foi novamente executado antes da implementação e está em
`red-context.xml`. Não somar os testes dos vários arquivos: há repetições.

Para repetir a seleção no WSL/Linux, a partir da raiz do repositório e com as
dependências de desenvolvimento já instaladas:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import json, os, shutil, subprocess, sys

root = Path.cwd()
receipt = json.loads((root / 'docs/evidence/r929/verified.json').read_text())
args = receipt['command'][:]
# Remover somente o plugin de relato incremental usado na execução original.
index = args.index('-p')
assert args[index + 1] == 'r929_suite_plugin'
del args[index:index + 2]
args = [a for a in args if not a.startswith('--junitxml=')]
with TemporaryDirectory(prefix='r929-repro-') as temporary:
    state = Path(temporary) / 'cycles.json'
    shutil.copyfile(root / 'evolution/cycles.json', state)
    env = dict(os.environ, EVOLUTION_STATE_PATH=str(state),
               OPENCODE_RUN_EXTERNAL_TESTS='0')
    # tests/conftest.py também isola a memória MCI e a saúde dos executores.
    result = subprocess.run([sys.executable, *args], cwd=root, env=env)
    raise SystemExit(result.returncode)
PY
```

A reprodução executa testes do checkout atual. Não instala ferramentas nem
aprova produção científica. Mudanças posteriores nas fontes, dependências ou
no ambiente podem alterar o resultado; compare os hashes do recibo.
