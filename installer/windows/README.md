# Instalação Windows com WSL — procedimento local

Este guia cobre o instalador Windows e o provisionamento WSL sem execução de
conteúdo remoto por pipe. Trabalhe sempre com um checkout local completo e
revise os scripts antes de abri-los como administrador.

> A verificação local de hash não constitui certificação externa, garantia de
> segurança ou confirmação de que um ambiente atenderá a todas as necessidades
> de uso.

## Pré-requisitos de procedência

Obtenha de um manifesto de versão revisado estes valores antes de executar um
script:

| Variável ou parâmetro | Valor necessário |
|---|---|
| `ECOSYSTEM_VERSION` | Identificador de versão imutável. |
| `ECOSYSTEM_REF` | Commit Git completo com 40 caracteres. |
| `ProvisionVersion` | A mesma versão ou outro identificador imutável do `provision.sh`. |
| `ProvisionSha256` | SHA-256 publicado com 64 caracteres para `provision.sh`. |
| `CommonInstallerSha256` | SHA-256 publicado com 64 caracteres para `installer/common/install_clis.sh`. |
| `PathSafetySha256` | SHA-256 publicado com 64 caracteres para `installer/common/path_safety.sh`. |

Além deles, obtenha do manifesto os metadados dos artefatos externos. O wrapper
recebe cada valor por parâmetro de mesmo nome ou por variável de ambiente e o
encaminha ao WSL em `$wslEnvironment`:

| Entrada | Finalidade |
|---|---|
| `OPENCODE_INSTALLER_URL` | URL HTTPS do instalador OpenCode, quando esse caminho for usado. |
| `OPENCODE_INSTALLER_SHA256` | SHA-256 publicado do instalador OpenCode. |
| `OPENCODE_ARTIFACT_VERSION` | Versão imutável do instalador OpenCode. |
| `OPENCODE_NPM_VERSION` | Versão imutável NPM do OpenCode, alternativa ao instalador. |
| `OPENCODE_NPM_SHA256` | SHA-256 publicado do tarball NPM principal do OpenCode. |
| `ANTIGRAVITY_INSTALLER_URL` | URL HTTPS do instalador Antigravity. |
| `ANTIGRAVITY_INSTALLER_SHA256` | SHA-256 publicado do instalador Antigravity. |
| `ANTIGRAVITY_ARTIFACT_VERSION` | Versão imutável do instalador Antigravity. |
| `CLAUDE_CODE_VERSION` | Versão imutável NPM do Claude Code. |
| `CLAUDE_CODE_NPM_SHA256` | SHA-256 publicado do tarball NPM principal do Claude Code. |
| `OLLAMA_BINARY_URL` | URL HTTPS do binário Ollama. |
| `OLLAMA_BINARY_SHA256` | SHA-256 publicado do binário Ollama. |
| `OLLAMA_ARTIFACT_VERSION` | Versão imutável do binário Ollama. |

O wrapper aceita somente valores textuais sem CR/LF para o transporte ao WSL e,
antes de instalar WSL, valida a configuração selecionada: URL HTTPS versionada
sem credenciais, consulta ou fragmento, versão imutável e SHA-256 com 64
caracteres. O provisionador e `install_clis.sh` repetem essa validação antes de
`sudo`, `apt`, cache, download, `npm` ou execução de CLI. Isso não substitui a
conferência independente do manifesto.

O repositório deve ter sido conferido em checkout destacado antes desta etapa:

```powershell
Set-Location C:\caminho\opencode-ecosystem-core
git checkout --detach <commit-git-completo-com-40-caracteres>
git rev-parse HEAD
if (git status --porcelain=v1 --untracked-files=all) { throw 'O checkout deve estar limpo.' }
git describe --tags --exact-match HEAD
Get-FileHash -Algorithm SHA256 -LiteralPath .\installer\windows\provision.sh
```

Compare manualmente cada saída com o commit, a versão e o SHA-256 do manifesto
independente. Não use um rótulo móvel como versão de instalação.

Os arquivos `*.sh` são mantidos em LF por `.gitattributes`; os hashes publicados
para `provision.sh` e `install_clis.sh` referem-se a esses bytes canônicos. Em
um checkout existente que tenha convertido os fins de linha, restaure os dois
arquivos a partir do commit conferido antes de calcular o hash.

## Executar o wrapper PowerShell a partir do arquivo local

Abra o PowerShell como administrador somente depois da conferência anterior.
O exemplo abaixo usa o `provision.sh` localizado ao lado do wrapper:

```powershell
$version = '<versao-imutavel>'
$revision = '<commit-git-completo-com-40-caracteres>'
$expectedProvisionSha256 = '<sha-256-publicado-com-64-caracteres>'
$expectedCommonInstallerSha256 = '<sha-256-publicado-com-64-caracteres>'
$expectedPathSafetySha256 = '<sha-256-publicado-com-64-caracteres>'
$actualProvisionSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath .\installer\windows\provision.sh).Hash
$actualCommonInstallerSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath .\installer\common\install_clis.sh).Hash
$actualPathSafetySha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath .\installer\common\path_safety.sh).Hash

if ($actualProvisionSha256 -ne $expectedProvisionSha256) { throw 'SHA-256 divergente para provision.sh' }
if ($actualCommonInstallerSha256 -ne $expectedCommonInstallerSha256) { throw 'SHA-256 divergente para install_clis.sh' }
if ($actualPathSafetySha256 -ne $expectedPathSafetySha256) { throw 'SHA-256 divergente para path_safety.sh' }

$env:ECOSYSTEM_REF = $revision
$env:OPENCODE_INSTALLER_URL = '<url-https-versionada-ou-vazio-para-usar-npm>'
$env:OPENCODE_INSTALLER_SHA256 = '<sha-256-publicado-com-64-caracteres-ou-vazio-para-usar-npm>'
$env:OPENCODE_ARTIFACT_VERSION = '<versao-imutavel-ou-vazia-para-usar-npm>'
$env:OPENCODE_NPM_VERSION = '<versao-npm-imutavel>'
$env:OPENCODE_NPM_SHA256 = '<sha-256-publicado-com-64-caracteres-do-tarball-principal>'
$env:ANTIGRAVITY_INSTALLER_URL = '<url-https-versionada>'
$env:ANTIGRAVITY_INSTALLER_SHA256 = '<sha-256-publicado-com-64-caracteres>'
$env:ANTIGRAVITY_ARTIFACT_VERSION = '<versao-imutavel>'
$env:CLAUDE_CODE_VERSION = '<versao-npm-imutavel>'
$env:CLAUDE_CODE_NPM_SHA256 = '<sha-256-publicado-com-64-caracteres-do-tarball-principal>'
$env:OLLAMA_BINARY_URL = '<url-https-versionada>'
$env:OLLAMA_BINARY_SHA256 = '<sha-256-publicado-com-64-caracteres>'
$env:OLLAMA_ARTIFACT_VERSION = '<versao-imutavel>'
.\installer\windows\Install-OpenCodeEcosystem.ps1 -ProvisionVersion $version -ProvisionSha256 $expectedProvisionSha256 -CommonInstallerSha256 $expectedCommonInstallerSha256 -PathSafetySha256 $expectedPathSafetySha256
```

`ECOSYSTEM_REF` é necessário porque o provisionador recusa instalar um checkout
sem revisão Git imutável. O wrapper monta uma lista explícita de ambiente para
o processo WSL; não é necessário editar `WSLENV`. O wrapper também exige que
`ProvisionVersion` não seja um identificador móvel e confere o SHA-256 antes
de instalar WSL/DISM ou usar suas cópias locais de `provision.sh` e
`installer/common/install_clis.sh`. O checkout local também precisa conter
`installer/common/path_safety.sh`, usado para validar o diretório que poderá
ser persistido pelo provisionador; seus bytes são conferidos antes da alteração
do SO, rehashados imediatamente antes da cópia e novamente no WSL.

## Reinicialização do WSL

Se a instalação do WSL solicitar reinicialização, o wrapper não grava uma
retomada automática. A **retomada manual** exige que, após reiniciar e concluir
a criação inicial do usuário Ubuntu, você abra novamente o PowerShell como
administrador, confira os hashes e execute o mesmo arquivo local com os mesmos
parâmetros validados.

## Execução no WSL

O wrapper copia `provision.sh` e `install_clis.sh` previamente verificados, mais
`path_safety.sh` exigido no checkout local, para uma árvore temporária no WSL.
Os caminhos relativos exigidos por `provision.sh` são preservados. Ele também
informa o caminho montado do checkout local original ao provisionador, que
confere seu `HEAD` contra `ECOSYSTEM_REF` e recusa alterações rastreadas ou
arquivos não rastreados antes de `sudo`, `apt` ou CLIs. Se essa preparação ou o
preflight falhar, o fluxo é interrompido antes dessas operações.

Quando for necessário preservar a árvore completa, execute o provisionador
diretamente a partir do checkout visível no WSL, depois de conferir os hashes
no PowerShell. Use ambiente explícito e Bash não-login, sem perfis; complete a
lista com as 13 entradas de artefato da tabela anterior:

```powershell
$wslEnv = @(
  'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
  'HOME=/home/<usuario>', 'USER=<usuario>', 'LOGNAME=<usuario>', 'BASH_ENV=', 'ENV=',
  'ECOSYSTEM_REF=<commit-git-completo-com-40-caracteres>'
  # acrescente aqui as 13 entradas OPENCODE_*, ANTIGRAVITY_*, CLAUDE_CODE_* e OLLAMA_*
)
& "$env:SystemRoot\System32\wsl.exe" -d Ubuntu -- /usr/bin/env -i $wslEnv /bin/bash --noprofile --norc -c '/bin/bash /mnt/c/caminho/opencode-ecosystem-core/installer/windows/provision.sh'
```

Antes de usar esse caminho, confirme que
`/mnt/c/caminho/opencode-ecosystem-core/installer/common/install_clis.sh` está
presente e que os valores de versão e SHA-256 de artefatos externos exigidos
pela biblioteca foram exportados ao WSL. O provisionador deve parar quando um
artefato obrigatório não puder ser conferido. Para execução direta, exporte as
13 entradas da tabela anterior no mesmo shell; o wrapper só faz esse repasse
automático quando ele próprio é usado.

## O que é configurado

O script pode solicitar a instalação do WSL2 e do Ubuntu, instalar dependências
no WSL, preparar CLIs externas quando os artefatos forem informados e regenerar
o `opencode.json` local. Ele preserva as proteções do Defender e do Firewall
em vez de desativá-las.

Depois de uma execução sem erros, confirme o estado no checkout WSL:

```powershell
$wslEnv = @('PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOME=/home/<usuario>', 'USER=<usuario>', 'LOGNAME=<usuario>', 'BASH_ENV=', 'ENV=')
& "$env:SystemRoot\System32\wsl.exe" -d Ubuntu -- /usr/bin/env -i $wslEnv /bin/bash --noprofile --norc -c 'cd ~/opencode-ecosystem-core && .venv/bin/python -m marceloclaro.cli doctor'
& "$env:SystemRoot\System32\wsl.exe" -d Ubuntu -- /usr/bin/env -i $wslEnv /bin/bash --noprofile --norc -c 'cd ~/opencode-ecosystem-core && .venv/bin/python -c "import json; c=json.load(open(\"opencode.json\", encoding=\"utf-8\")); print(len(c.get(\"mcp\", {})), len(c.get(\"agent\", {})))"'
```

Na configuração documentada em **2026-08-23**, o diagnóstico continha **19 checks**,
e `opencode.json` declarava **6 MCPs** e **209 agentes**. São
contagens estruturais locais, não resultados de cobertura, testes ou validação
externa.

## Limites do cache NPM e da automação de shell

Para pacotes NPM, o SHA-256 informado cobre o tarball principal. `npm --offline`
evita download durante a instalação, mas pode consumir dependências transitivas
do cache NPM local. O instalador não autentica individualmente esses bytes de
cache; portanto, cache offline não é uma garantia de integridade transitiva. Se
uma dependência não estiver disponível, o fluxo falha em vez de buscá-la sem
declaração.

Os rehashes e preflights reduzem risco, mas comandos de shell que verificam e
depois usam caminhos ainda têm uma janela TOCTOU diante de modificação local
concorrente. Este guia não anuncia teste ou garantia E2E do fluxo Windows/WSL;
revise os artefatos, o log e o estado local antes do uso.

## Atalhos e remoção

O wrapper tenta criar atalhos do Windows para OpenCode, Antigravity, Claude Code e a CLI do ecossistema. Verifique os caminhos criados antes de usá-los. Para remover componentes, use `Uninstall-OpenCodeEcosystem.ps1` apenas a partir do checkout local e leia a confirmação exigida para cada operação destrutiva.
