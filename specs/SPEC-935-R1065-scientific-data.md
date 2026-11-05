# SPEC-935-R1065 — scientific-data MCP (NetCDF, HDF5, Zarr, GeoTIFF)

**Status:** implementado e testado com arquivos sintéticos; MCP somente leitura.
**Objetivo:** permitir que o Core inspecione dados científicos locais sem abrir
arrays inteiros, sem executar conteúdo e sem expor caminhos fora das raízes
autorizadas.

## 1. Stack

Venv isolado Python 3.12:
`xarray 2026.9.0`, `h5py 3.16.0`, `rasterio 1.5.2`, `zarr 3.4.2`,
`netCDF4 1.7.5.1`, `h5netcdf 1.8.2`, `mcp 1.30.0`.

## 2. Ferramentas MCP

| Ferramenta | Efeito |
|---|---|
| `scientific_status` | versões e formatos suportados |
| `scientific_inspect` | metadados de NetCDF/HDF5/Zarr/GeoTIFF |
| `scientific_preview` | estatísticas e amostra limitada de uma variável/banda |

Todas são `readOnlyHint=True`; nenhuma escreve, converte ou executa código do
arquivo.

## 3. Política

- Raízes autorizadas: repositório, `/mnt/c/Users/marce/Downloads`,
  `/tmp/opencode` (config `config/scientific_data.json`; `SCIENTIFIC_DATA_ROOTS`
  pode substituir).
- Rejeitar symlink, caminho fora da raiz, extensão não suportada, arquivo
  acima de 2 GiB e diretório que não seja `.zarr`.
- Extensões: `.nc`, `.nc4`, `.cdf`, `.h5`, `.hdf5`, `.he5`, `.tif`, `.tiff`,
  `.gtiff`, `.zarr`.
- Metadados e atributos passam por redação (`sk-`, e-mail, CPF, tokens).
- `preview` nunca despeja o array inteiro: aplica seletor e limita a
  `max_preview_points` (100–5000; padrão 2000), retornando estatísticas e no
  máximo 200 valores de amostra.
- Sem URLs remotas; sem `pickle`; sem engine arbitrária.

## 4. Formatos

- **NetCDF**: `xarray.open_dataset` com engines `netcdf4` → `h5netcdf` →
  `scipy`, decodificação CF.
- **HDF5 genérico**: árvore `h5py` com grupos/datasets, shape, dtype, chunks,
  compressão e atributos; limite de 500 nós.
- **Zarr**: `xarray.open_zarr(..., consolidated=False)`.
- **GeoTIFF**: `rasterio` com CRS, bounds, transform, resolução, nodata,
  descrições, overviews e compressão; preview por banda com downscale.

## 5. Aceitação

1. inspecionar NetCDF e preview com seletor;
2. inspecionar HDF5 genérico e preview de dataset;
3. inspecionar Zarr e preview;
4. inspecionar GeoTIFF com CRS/bounds e preview de banda;
5. negar caminho fora da raiz e symlink;
6. negar formato não suportado e seletor inválido;
7. limitar preview de 100×100 a ~10×10 e marcar `preview_limited`;
8. catálogo MCP com exatamente três ferramentas.

**Resultado:** **8 passed** no venv científico; o pytest do sistema ignora o
módulo quando o stack não está instalado.

## 6. Integração

- MCP `scientific-data` registrado no `opencode.json` e no gerador.
- Perfil `scientific-data-analyst` no catálogo (somente leitura).
- O MCP usa o venv científico absoluto; não altera o Python do Core.

## 7. Limites

- Metadados não provam qualidade científica, calibração ou validade dos dados.
- Preview é amostra, não estatística do arquivo inteiro.
- NetCDF3/NetCDF4 e HDF5 têm dialetos; formatos exóticos podem falhar.
- GRIB, BUFR, Parquet e dados remotos não estão no escopo.
- Nenhuma validação externa, publicação ou revisão científica.
