# Catálogo e planejador de conteúdo offline (R1022)

## Origem da ideia

O Project NOMAD organiza conteúdo offline em categorias, tiers e recursos, com
tamanho, versão e URL de origem. O Core não tinha um formato equivalente para
planejar pacotes de conhecimento offline. A R1022 extrai **o modelo de
organização e planejamento**, não os dados, o código ou a interface do NOMAD.
O projeto original é Apache-2.0.

## O que foi adicionado

- `integrations/offline_content.py`
- `tests/test_r1022_offline_content.py`
- `specs/SPEC-935-R1022-offline-content-catalog.md`
- Comando direto:
  `python3 -m marceloclaro.cli conteudo-offline ...`

## Formato do catálogo

```json
{
  "schema_version": "1.0",
  "categories": [
    {
      "id": "saude",
      "title": "Saúde",
      "description": "Referências de saúde",
      "tiers": [
        {
          "id": "saude-essencial",
          "title": "Essencial",
          "description": "Primeiros socorros",
          "includes_tiers": [],
          "resources": [
            {
              "id": "primeiros-socorros",
              "title": "Primeiros socorros",
              "version": "2026-01",
              "url": "https://example.org/primeiros-socorros.zim",
              "size_mb": 10,
              "kind": "zim",
              "license": "CC-BY-4.0",
              "sha256": "opcional-64-hex"
            }
          ]
        }
      ]
    }
  ]
}
```

Campos de recurso:

| Campo | Regra |
|---|---|
| `id` | letras, números, ponto, sublinhado e hífen; único |
| `title` | texto não vazio |
| `version` | texto não vazio |
| `url` | `https`, com host e sem credenciais |
| `bytes` | inteiro positivo; exato |
| `size_mb` | número positivo; aproximado, marcado como estimado |
| `kind` | `zim`, `epub`, `pdf`, `dataset`, `map`, `course`, `video`, `audio`, `other` |
| `license` | opcional; ausência gera aviso |
| `sha256` | opcional; 64 hexadecimais |

## Uso

```bash
# Listar categorias e tiers
python3 -m marceloclaro.cli conteudo-offline list catalogo.json

# Planejar um tier e seus includes
python3 -m marceloclaro.cli conteudo-offline plan catalogo.json \
  --select saude:saude-ampla

# Saída JSON para outro programa
python3 -m marceloclaro.cli conteudo-offline plan catalogo.json \
  --select saude:saude-ampla --json
```

O plano mostra recursos, versões, tamanhos, licenças, total exato/estimado,
avisos de licença ausente e tamanho aproximado. `includes_tiers` é resolvido
dentro da mesma categoria; ciclos e tiers ausentes são recusados.

## Segurança

- O catálogo é lido de arquivo regular local, não symlink, até 8 MiB.
- Nenhuma URL é acessada, baixada, instalada ou executada.
- O planejador não substitui verificação de licença, direito autoral, hash do
  arquivo remoto ou decisão humana.
- `size_mb` é aproximado; use `bytes` quando o tamanho exato for conhecido.

## Verificação

- 20 testes determinísticos, sem rede.
- RED controlado e GREEN 20/20 em worktree isolada.
- `SpecVerifier`: 5/5 critérios no gate `software_delivery_gate`.
- CLI integrada a `marceloclaro.cli`.
