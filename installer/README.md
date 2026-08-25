# Instalação local — OpenCode Ecosystem Core

Este guia deliberadamente não oferece comandos que encaminhem conteúdo de rede diretamente para um interpretador. Obtenha o material por canal confiável, revise-o e execute apenas arquivos locais de uma revisão identificada.

> A conferência de versão, commit e SHA-256 reduz o risco de executar bytes
> diferentes dos esperados. Ela não constitui certificação externa nem garantia
> de segurança, funcionamento ou adequação.

## Dados de procedência obrigatórios

Antes da instalação, obtenha de um manifesto de versão revisado e independente do canal de download os dados a seguir.

| Dado | Formato exigido | Uso |
|---|---|---|
| `ECOSYSTEM_VERSION` | Tag ou identificador de versão imutável | Registro da versão selecionada. |
| `ECOSYSTEM_REF` | Commit Git completo com 40 caracteres hexadecimais | Checkout destacado que os scripts exigem. |
| `ECOSYSTEM_SOURCE_SHA256` | SHA-256 com 64 caracteres hexadecimais | Conferência do arquivo de origem criado abaixo. |

Não substitua esses valores por nomes de branch ou por rótulos móveis. Um hash
copiado do mesmo arquivo não é uma fonte independente de procedência.

## Preparar e conferir o checkout

Substitua cada marcador pelos valores da versão que você revisou.

```bash
export ECOSYSTEM_VERSION='<versao-imutavel>'
export ECOSYSTEM_REF='<commit-git-completo-com-40-caracteres>'
export ECOSYSTEM_SOURCE_SHA256='<sha-256-publicado-com-64-caracteres>'

git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git opencode-ecosystem-core
cd opencode-ecosystem-core
git checkout --detach "$ECOSYSTEM_REF"
test "$(git rev-parse HEAD)" = "$ECOSYSTEM_REF"
test "$(git describe --tags --exact-match HEAD)" = "$ECOSYSTEM_VERSION"

git archive --format=tar "$ECOSYSTEM_REF" -o ../opencode-ecosystem-source.tar
printf '%s  %s\n' "$ECOSYSTEM_SOURCE_SHA256" "../opencode-ecosystem-source.tar" > ../opencode-ecosystem-source.tar.sha256
sha256sum -c ../opencode-ecosystem-source.tar.sha256
```

O valor de `ECOSYSTEM_SOURCE_SHA256` deve referir-se exatamente ao TAR gerado
por `git archive --format=tar` para o commit indicado. Se o manifesto publicar
o hash de outro formato de arquivo, confira aquele arquivo com o algoritmo e o
nome publicados, sem reutilizar o valor para este TAR.

## Preflight dos instaladores

Antes de pedir `sudo`, chamar um gerenciador de pacotes ou instalar uma CLI, os
instaladores Linux, macOS e WSL recusam continuar se `ECOSYSTEM_REPO_URL` não
for HTTPS sem credenciais, consulta ou fragmento, se `ECOSYSTEM_REF` não tiver
40 hexadecimais ou se o checkout local que contém o script não estiver
exatamente nesse `HEAD` **e limpo**. A limpeza considera modificações, índices
pendentes e arquivos não rastreados; o instalador não faz `reset` nem `clean`
automaticamente. Se `ECOSYSTEM_DIR` já existir, ele também deve ser a raiz de
um checkout Git limpo no mesmo commit; um diretório não-Git, simbólico,
divergente ou alterado não é removido nem atualizado.
Como o preflight ocorre antes do gerenciador de pacotes, `git` já precisa estar
disponível no sistema que executará o script; sua ausência também interrompe o
fluxo sem tentar instalar dependências primeiro.

Essas verificações são deliberadamente fail-closed, mas operações de shell por
pathname não são atômicas contra uma alteração concorrente local (TOCTOU).
Elas reduzem a superfície de erro, não constituem uma garantia contra outro
processo com capacidade de modificar a árvore entre uma checagem e seu uso.

## Instalação Python mínima

Depois de conferir o checkout, a instalação mínima do projeto é local:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m marceloclaro.cli doctor
```

No estado estrutural documentado em **2026-08-23**, esse diagnóstico tinha
**19 checks**; o arquivo `opencode.json` declarava **6 MCPs** e **209 agentes**.
Esses números devem ser reavaliados no checkout instalado e não representam
resultado de testes, cobertura ou validação externa.

```bash
python3 -c "import json; c=json.load(open('opencode.json', encoding='utf-8')); print({'mcps': len(c.get('mcp', {})), 'agentes': len(c.get('agent', {}))})"
```

## Linux

O instalador Linux deve ser executado a partir do checkout local já conferido:

```bash
ECOSYSTEM_DIR="$PWD" ECOSYSTEM_REF="$ECOSYSTEM_REF" bash installer/linux/install.sh
```

Para que aliases e launchers possam ser persistidos sem reinterpretação pelo
shell, `ECOSYSTEM_DIR` deve ser um caminho absoluto **sob `HOME`**, com
componentes ASCII previsíveis e sem espaços, aspas, metacaracteres ou segmentos
`.`/`..`. Um checkout fora dessa fronteira é recusado; mova-o para uma pasta
compatível sob `HOME` em vez de tentar contornar a validação.

Ele recusa `ECOSYSTEM_REF` ausente ou diferente tanto do checkout-fonte quanto
do checkout de destino existente. As CLIs externas usam
`installer/common/install_clis.sh`; antes de habilitar um download automático,
informe para cada artefato os valores de URL HTTPS versionada (quando aplicável),
versão imutável e SHA-256 exigidos por essa biblioteca. A configuração é
validada antes de `sudo`, `apt`, `brew`, `npm`, cache ou download; sem esses
valores, a interrupção é intencional. O ticket `sudo` usado apenas nas
dependências é invalidado antes dessa etapa.

Pacotes NPM são instalados em modo offline e com scripts de ciclo de vida
desabilitados depois da conferência do tarball **principal**. O modo offline
impede download nessa chamada do `npm`, mas o NPM pode consumir dependências
transitivas já presentes no seu cache local. O instalador não confere
individualmente a procedência ou o hash dessas entradas transitivas; esse cache
não é uma prova de integridade transitiva. Se uma delas faltar, a instalação
falha em vez de buscar bytes adicionais silenciosamente.
`ECOSYSTEM_ARTIFACT_CACHE` não é um override suportado: os artefatos usam uma
raiz privada fixa sob `HOME`, recusando links simbólicos e caminhos externos.

O caminho principal foi escrito para distribuições Debian/Ubuntu. Os caminhos
para outros gerenciadores de pacote devem ser tratados como tentativa local e
revisados antes do uso.

## macOS

No macOS, também execute o arquivo local depois da conferência:

```bash
ECOSYSTEM_DIR="$PWD" ECOSYSTEM_REF="$ECOSYSTEM_REF" bash installer/macos/install.sh
```

O script depende de Homebrew já instalado e declara o caminho como best-effort.
O mesmo preflight confere o checkout-fonte e um destino existente antes de
`brew install`. Não há resultado de execução em hardware Apple anunciado por
este guia; examine o log local e o `doctor` após a instalação.

## Windows 10/11

O fluxo Windows usa WSL2 e possui requisitos adicionais de revisão do
`provision.sh`. Leia [windows/README.md](windows/README.md) antes de executá-lo.
Em resumo, o procedimento requer:

1. o checkout local completo e conferido;
2. uma `ProvisionVersion` imutável;
3. o SHA-256 esperado de `installer/windows/provision.sh`;
4. o SHA-256 esperado de `installer/common/install_clis.sh`
    (`CommonInstallerSha256`);
5. o SHA-256 esperado de `installer/common/path_safety.sh`
   (`PathSafetySha256`);
6. `ECOSYSTEM_REF` e as 13 entradas de procedência de CLIs repassados pelo
   wrapper diretamente ao ambiente WSL;
7. os artefatos externos versionados e hashados quando forem solicitados.

Se a instalação do WSL exigir reboot, a retomada é **manual**: depois de
reiniciar, reabra o PowerShell como administrador e execute novamente o mesmo
arquivo local com os parâmetros já conferidos. O wrapper não registra uma
retomada automática em `RunOnce`.

O fluxo Windows/WSL também não afirma validação E2E. Os hashes, o rehash no WSL
e o preflight são verificações pontuais; revise o log e execute as verificações
locais adequadas ao seu ambiente.

## Depois da instalação

```bash
.venv/bin/python -m marceloclaro.cli doctor
.venv/bin/python -m marceloclaro.cli helpdesk
.venv/bin/python -m marceloclaro.cli
```

Para desinstalação, use apenas o script local correspondente à plataforma e
leia seus avisos de confirmação antes de aceitar uma operação destrutiva.
