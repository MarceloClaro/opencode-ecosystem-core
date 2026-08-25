# Como contribuir

Obrigado por melhorar o OpenCode Ecosystem Core. Este repositório usa
especificações formais e testes como contratos de mudança; contribuições devem
ser pequenas, auditáveis e revisáveis.

## Antes de começar

1. Leia [AGENTS.md](AGENTS.md), [MANUAL.md](MANUAL.md) e
   [ARCHITECTURE.md](ARCHITECTURE.md).
2. Execute `python3 -m marceloclaro.cli doctor` e registre avisos relevantes no
   contexto da mudança.
3. Localize uma SPEC existente em `specs/` ou crie uma nova
   `SPEC-935-R<id>.md` com objetivo, critérios executáveis, estratégia TDD e
   não objetivos.
4. Não misture diretórios pessoais, dados externos, segredos ou artefatos
   gerados em uma mudança de código/documentação.

## Fluxo de desenvolvimento

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest caminho/do/teste.py -q
.venv/bin/python -m pytest tests/ -q --tb=short --timeout=120
git diff --check
```

Use RED → GREEN → REFACTOR: escreva ou ajuste o teste para o comportamento
esperado, observe a falha, implemente a menor correção e execute os testes
relevantes. Especificações Markdown são avaliadas pelo `SpecVerifier`; não
trate uma declaração do agente como substituta da evidência de teste emitida
pelo runtime.

## Revisão e commit

Antes de solicitar revisão:

1. leia `git status --short` e o diff completo;
2. confira que arquivos não relacionados, credenciais e dados pessoais não
   serão adicionados;
3. execute os gates definidos na SPEC e, quando aplicável, a suíte integral;
4. atualize documentação afetada sem transformar resultados locais em alegações
   externas;
5. faça commits atômicos com mensagem concisa no estilo do histórico.

Somente envie uma branch após revisão humana ou do responsável pelo repositório
e após confirmar o remoto e a branch de destino. Não use force-push para
contornar uma revisão ou um gate reprovado.

## Relatos de falha e comportamento inesperado

Inclua ambiente, revisão Git, comando executado, saída relevante e um caso
mínimo reproduzível. Para possíveis vulnerabilidades, siga
[SECURITY.md](SECURITY.md) em vez de publicar detalhes exploráveis em issue.
