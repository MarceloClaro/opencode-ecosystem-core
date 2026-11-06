"""R1065 — inspeção somente leitura de NetCDF, HDF5, Zarr e GeoTIFF."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from integrations.desktop_operator import runtime

from . import policy


class InspectError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _versions() -> dict:
    import h5py
    import netCDF4
    import rasterio
    import xarray
    import zarr
    return {"xarray": xarray.__version__, "h5py": h5py.__version__,
            "rasterio": rasterio.__version__, "zarr": zarr.__version__,
            "netCDF4": netCDF4.__version__}


def status() -> dict:
    try:
        versions = _versions()
    except Exception as exc:
        return {"ok": False, "error": {"code": "ENGINE_MISSING", "message": str(exc)}}
    return {"ok": True, "read_only": True, "engines": versions,
            "formats": ["netcdf", "hdf5", "zarr", "geotiff"],
            "external_validation": False}


def _safe(value: Any, depth: int = 0) -> Any:
    if depth > 4:
        return "[TRUNCATED]"
    if isinstance(value, dict):
        return {str(k)[:100]: _safe(v, depth + 1) for k, v in list(value.items())[:50]}
    if isinstance(value, (list, tuple)):
        return [_safe(v, depth + 1) for v in list(value)[:50]]
    if isinstance(value, bytes):
        return value[:200].decode("utf-8", "replace")
    if isinstance(value, str):
        return runtime.redact_payload(value[:500])
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return runtime.redact_payload(str(value)[:300])


def _open_dataset(path: Path):
    import xarray as xr
    errors = []
    for engine in ("netcdf4", "h5netcdf", "scipy"):
        try:
            return xr.open_dataset(path, engine=engine, decode_cf=True, mask_and_scale=True)
        except Exception as exc:
            errors.append(f"{engine}: {type(exc).__name__}")
    raise InspectError("OPEN_FAILED", f"não foi possível abrir NetCDF ({'; '.join(errors)})")


def _encoding(var) -> dict:
    result = {}
    for key in ("chunksizes", "zlib", "complevel", "shuffle", "dtype",
                "original_shape", "scale_factor", "add_offset", "_FillValue"):
        if key in var.encoding:
            result[key] = _safe(var.encoding[key])
    return result


def _dataset_meta(ds, fmt: str, path: Path) -> dict:
    variables = []
    for name, var in ds.variables.items():
        variables.append({
            "name": name, "dims": list(var.dims), "shape": list(var.shape),
            "dtype": str(var.dtype), "attrs": _safe(dict(var.attrs)),
            "encoding": _encoding(var),
            "nbytes": int(getattr(var, "size", 0)) * int(getattr(var.dtype, "itemsize", 0)),
        })
    return {"format": fmt, "path": str(path), "size_bytes": path.stat().st_size
            if path.is_file() else None, "dims": {k: int(v) for k, v in ds.sizes.items()},
            "coords": list(ds.coords), "variables": variables,
            "attrs": _safe(dict(ds.attrs)), "backend": fmt}


def _hdf5_meta(path: Path) -> dict:
    import h5py
    nodes = []
    try:
        with h5py.File(path, "r") as handle:
            def visit(name, obj):
                if len(nodes) >= 500:
                    return
                if isinstance(obj, h5py.Dataset):
                    nodes.append({"path": name, "kind": "dataset", "shape": list(obj.shape),
                                  "dtype": str(obj.dtype), "chunks": obj.chunks,
                                  "compression": obj.compression,
                                  "attrs": _safe(dict(obj.attrs)),
                                  "nbytes": int(obj.size) * int(obj.dtype.itemsize)})
                else:
                    nodes.append({"path": name, "kind": "group", "attrs": _safe(dict(obj.attrs))})
            handle.visititems(visit)
    except Exception as exc:
        raise InspectError("OPEN_FAILED", f"não foi possível abrir HDF5: {type(exc).__name__}") from exc
    return {"format": "hdf5", "path": str(path), "size_bytes": path.stat().st_size,
            "nodes": nodes, "truncated": len(nodes) >= 500}


def _raster_meta(path: Path) -> dict:
    import rasterio
    try:
        with rasterio.open(path) as src:
            return {"format": "geotiff", "path": str(path), "size_bytes": path.stat().st_size,
                    "driver": src.driver, "width": src.width, "height": src.height,
                    "count": src.count, "dtypes": list(src.dtypes),
                    "crs": str(src.crs) if src.crs else None,
                    "bounds": list(src.bounds), "transform": list(src.transform)[:6],
                    "res": list(src.res), "nodata": src.nodata,
                    "descriptions": list(src.descriptions),
                    "compress": src.profile.get("compress"),
                    "overviews": [src.overviews(i) for i in range(1, src.count + 1)]}
    except Exception as exc:
        raise InspectError("OPEN_FAILED", f"não foi possível abrir raster: {type(exc).__name__}") from exc


def inspect(config: policy.ScientificConfig, path: str | Path) -> dict:
    target = policy.validate_path(config, path)
    suffix = target.suffix.casefold()
    try:
        if target.is_dir() and suffix == ".zarr":
            import xarray as xr
            ds = xr.open_zarr(target, consolidated=False)
            try:
                return {"ok": True, "metadata": _dataset_meta(ds, "zarr", target)}
            finally:
                ds.close()
        if suffix in {".tif", ".tiff", ".gtiff"}:
            return {"ok": True, "metadata": _raster_meta(target)}
        if suffix in {".h5", ".hdf5", ".he5"}:
            import h5py
            with h5py.File(target, "r") as handle:
                native_netcdf = "_NCProperties" in handle.attrs
            if native_netcdf:
                ds = _open_dataset(target)
                try:
                    return {"ok": True, "metadata": _dataset_meta(ds, "netcdf-hdf5", target)}
                finally:
                    ds.close()
            return {"ok": True, "metadata": _hdf5_meta(target)}
        ds = _open_dataset(target)
        try:
            return {"ok": True, "metadata": _dataset_meta(ds, "netcdf", target)}
        finally:
            ds.close()
    except policy.ScientificDenied:
        raise
    except InspectError:
        raise
    except Exception as exc:
        raise InspectError("INSPECT_FAILED", f"{type(exc).__name__}: {str(exc)[:300]}") from exc


def _stats(array) -> dict:
    import numpy as np
    data = np.asarray(array)
    if not np.issubdtype(data.dtype, np.number):
        return {"numeric": False}
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        return {"numeric": True, "count": 0}
    sample = finite.reshape(-1)[:200]
    return {"numeric": True, "count": int(finite.size),
            "min": float(finite.min()), "max": float(finite.max()),
            "mean": float(finite.mean()), "std": float(finite.std()),
            "sample": [float(v) for v in sample]}


def _slice_for_shape(shape: tuple[int, ...], max_points: int) -> tuple[slice, ...]:
    if not shape:
        return ()
    side = max(1, int(math.floor(max_points ** (1 / max(1, len(shape))))))
    return tuple(slice(0, min(int(dim), side)) for dim in shape)


def _preview_dataset(config: policy.ScientificConfig, target: Path, variable: str | None,
                     selector: dict | None, max_points: int, fmt: str) -> dict:
    import xarray as xr
    ds = xr.open_zarr(target, consolidated=False) if fmt == "zarr" else _open_dataset(target)
    try:
        name = variable
        if not name:
            names = list(ds.data_vars)
            if len(names) != 1:
                raise InspectError("VARIABLE_REQUIRED", "informe a variável")
            name = names[0]
        if name not in ds.variables:
            raise InspectError("VARIABLE_NOT_FOUND", "variável não encontrada")
        da = ds[name]
        original_size = int(da.size)
        if selector:
            for key, value in selector.items():
                if key not in da.dims:
                    raise InspectError("SELECTOR_INVALID", f"dimensão inválida: {key}")
                if type(value) is not int:
                    raise InspectError("SELECTOR_INVALID", "seletor deve usar inteiros")
                size = da.sizes[key]
                if not 0 <= value < size:
                    raise InspectError("SELECTOR_INVALID", f"índice fora de faixa: {key}")
            da = da.isel(**selector)
        slicer = _slice_for_shape(tuple(da.shape), max_points)
        if slicer:
            da = da.isel({dim: sl for dim, sl in zip(da.dims, slicer)})
        stats = _stats(da.values)
        return {"ok": True, "variable": name, "dims": list(da.dims),
                "shape": list(da.shape), "selector": selector or {},
                "preview_limited": original_size > max_points, "stats": stats}
    finally:
        ds.close()


def preview(config: policy.ScientificConfig, path: str | Path, *, variable: str | None = None,
            selector: dict | None = None, band: int = 1,
            max_points: int | None = None) -> dict:
    target = policy.validate_path(config, path)
    cap = max(100, min(int(max_points or config.max_preview_points), 5000))
    suffix = target.suffix.casefold()
    try:
        if suffix in {".tif", ".tiff", ".gtiff"}:
            import rasterio
            with rasterio.open(target) as src:
                if type(band) is not int or not 1 <= band <= src.count:
                    raise InspectError("BAND_INVALID", "banda fora de faixa")
                scale = min(1.0, 256 / max(src.width, src.height))
                out_shape = (max(1, int(src.height * scale)), max(1, int(src.width * scale)))
                data = src.read(band, out_shape=out_shape)
                return {"ok": True, "band": band, "shape": list(data.shape),
                        "preview_limited": scale < 1.0, "stats": _stats(data)}
        if suffix in {".h5", ".hdf5", ".he5"}:
            import h5py
            import numpy as np
            with h5py.File(target, "r") as handle:
                if not variable:
                    datasets = []
                    handle.visititems(lambda name, obj: datasets.append(name) if isinstance(obj, h5py.Dataset) else None)
                    if len(datasets) != 1:
                        raise InspectError("VARIABLE_REQUIRED", "informe o caminho do dataset")
                    variable = datasets[0]
                if variable not in handle or not isinstance(handle[variable], h5py.Dataset):
                    raise InspectError("VARIABLE_NOT_FOUND", "dataset não encontrado")
                ds = handle[variable]
                slicer = tuple(slice(0, min(int(dim), 64)) for dim in ds.shape)
                data = ds[slicer]
                return {"ok": True, "variable": variable, "shape": list(data.shape),
                        "preview_limited": ds.size > data.size, "stats": _stats(np.asarray(data))}
        if target.is_dir() and suffix == ".zarr":
            return _preview_dataset(config, target, variable, selector, cap, "zarr")
        return _preview_dataset(config, target, variable, selector, cap, "netcdf")
    except (policy.ScientificDenied, InspectError):
        raise
    except Exception as exc:
        raise InspectError("PREVIEW_FAILED", f"{type(exc).__name__}: {str(exc)[:300]}") from exc
