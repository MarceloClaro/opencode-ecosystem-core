# R1065 — scientific-data MCP

**Status:** implementado e testado com arquivos sintéticos. Nada publicado;
sem validação científica externa.

## Entregue

- `integrations/scientific_data/` com política, inspeção, CLI e MCP.
- `config/scientific_data.json` com raízes autorizadas.
- `tests/test_r1065_scientific_data.py` — **8 passed** no venv científico;
  o pytest do sistema ignora quando o stack não está presente.
- Spec `SPEC-935-R1065-scientific-data.md`.

## Stack validado

| Pacote | Versão |
|---|---|
| xarray | 2026.9.0 |
| h5py | 3.16.0 |
| rasterio | 1.5.2 |
| zarr | 3.4.2 |
| netCDF4 | 1.7.5.1 |
| h5netcdf | 1.8.2 |
| mcp | 1.30.0 (pin `<2` para FastMCP) |

Venv: `~/.cache/opencode-pilot/venvs/scientific`.

## Demonstração real

Arquivo sintético `/tmp/opencode/r1065-demo.nc` com
`temperature(time=2, lat=3, lon=4)`:

```bash
scientific-data inspect --path /tmp/opencode/r1065-demo.nc
scientific-data preview --path /tmp/opencode/r1065-demo.nc \
  --variable temperature --selector '{"time":1}'
```

Resultado: formato `netcdf`; dims `{time:2, lat:3, lon:4}`; preview shape
`[3,4]`; min 12, max 23, mean 17,5.

## Segurança

- Somente leitura; nenhuma conversão ou execução de conteúdo.
- Raízes allowlisted; symlink e path traversal negados.
- Preview limitado; não carrega o arquivo inteiro.
- Atributos e metadados passam por redação.
- Sem URL remota, sem `pickle`, sem engine arbitrária.

## Limites

- Metadados não validam calibração, qualidade ou conclusão científica.
- Preview é amostra, não estatística global.
- GRIB/BUFR/Parquet e armazenamento remoto ficam fora do escopo.
- Nenhuma revisão humana ou validação externa.

## Próximo passo

Usar `scientific_inspect` antes de qualquer análise; depois `scientific_preview`
para checar dimensões, CRS e faixa de valores. Para estatística inferencial,
delegar ao agente de estatística com os dados já validados.
