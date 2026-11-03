---
name: remotion-auditavel
description: Use Remotion em um projeto local com licença explícita, inspeção read-only, prévia antes do render e conferência do plano de edição. Aplique quando o usuário pedir vídeo programático em React/Remotion, revisar composições, validar render ou checar se a Remotion License se aplica; não copia código do Remotion, não renderiza sem aprovação e não substitui parecer jurídico.
metadata:
  version: "1"
  origem: "R1025 — skill original; Remotion é referência, não dependência copiada"
---

# Remotion auditável

Use Remotion como ferramenta declarada pelo usuário, não como dependência
implícita. Esta skill organiza licença, inspeção, prévia, render e QC. Ela não
instala Remotion, não executa o projeto e não copia código de terceiros.

## Licença

Antes de instalar ou distribuir, confirme a elegibilidade:

- Remotion usa a **Remotion License**, não uma licença OSI como MIT.
- O resumo do `LICENSE.md` permite uso gratuito por indivíduos, organizações
  sem fins lucrativos e empresas com até 3 funcionários.
- Empresa for-profit acima desse limite precisa de licença comercial.
- Não é permitido vender, alugar ou relicenciar um derivado do Remotion.
- Licença do código não cobre mídia, fontes, modelos ou marcas de terceiros.

Consulte [Licença Remotion](references/licenca-remotion.md) e o texto oficial
no commit fixado. A skill faz um resumo operacional; **não é parecer jurídico**.

## Inspeção

Antes de propor alterações, inspecione o projeto local sem executá-lo:

```bash
python3 -m integrations.remotion_mcp
```

No MCP `remotion-audit`, use `project_scan` com o caminho do projeto. O retorno
traz dependências Remotion, versões fixadas ou flutuantes, arquivos de licença,
configuração, composições encontradas e avisos. O scanner:

- lê `package.json`, `LICENSE`, `remotion.config.*` e fontes;
- ignora `node_modules`, `out`, `build`, `.git` e diretórios ocultos;
- limita arquivos e bytes e não segue symlink na raiz;
- usa regex para `<Composition>` e **não avalia TypeScript**.

Nunca trate uma composição descoberta por regex como prova de que o projeto
compila. Não instale dependências para "verificar".

## Prévia e render

A prévia vem antes do render:

```bash
npx remotion studio --no-open
```

O plugin `remotion-guard` permite `remotion studio` e bloqueia
`remotion render`, `still` e `bundle` sem aprovação explícita. Para renderizar,
o operador precisa definir `REMOTION_RENDER_APPROVED=1` no ambiente. A aprovação
é uma decisão humana; não a presuma por pedido genérico como "faça o vídeo".

Instalação de `remotion` ou `@remotion/*` exige `REMOTION_LICENSE_ACK=1`, que
registra ciência da licença. Isso não substitui a análise de elegibilidade.

Antes do render, valide o plano com `render_preflight` ou com o validador R1024:

```bash
python3 -m integrations.video_edit_plan validate plano.json
```

## Composição e QC

- Derive movimento do frame da composição; não use animação CSS ou relógio de
  execução para avançar a cena.
- Mantenha `durationInFrames`, `fps`, largura e altura coerentes com a saída.
- Preserve arquivos e composições existentes; mudanças inesperadas merecem
  confirmação, não sobrescrita.
- Valide o plano R1024 antes do render e compare os metadados do arquivo com
  `video_edit_plan verify`.
- Metadados corretos não provam qualidade visual, sincronização ou segurança
  de enquadramento; assista à prévia e confira o trecho crítico.

Fluxo resumido em [Fluxo de produção](references/fluxo-de-producao.md). Exemplo
de plano em [Exemplo de plano](references/exemplo-plano.json).

## Limites

- A skill e o MCP não instalam, renderizam ou executam Remotion.
- O scanner não compila TypeScript e pode não ver composições dinâmicas.
- A política de licença é resumo; não é parecer jurídico nem garante que o uso
  do usuário se enquadra.
- O plugin reduz render acidental; não impede uso comercial indevido nem
  substitui revisão de direitos, consentimento e licença de mídia.
- Nenhum código do Remotion é copiado para o Core.
