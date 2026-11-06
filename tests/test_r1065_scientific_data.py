"""R1065: inspeção científica local; usa arquivos sintéticos e não executa conteúdo."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("xarray")
pytest.importorskip("h5py")
pytest.importorskip("rasterio")
pytest.importorskip("mcp.server.fastmcp")

import h5py
import numpy as np
import rasterio
import xarray as xr
from rasterio.transform import from_origin

from integrations.scientific_data import inspect as inspector, policy


def config(root: Path) -> policy.ScientificConfig:
    return policy.ScientificConfig(allowed_roots=(str(root),), max_preview_points=500)


def make_netcdf(root: Path) -> Path:
    ds = xr.Dataset(
        {"temp": (("time", "lat"), np.arange(12, dtype="float32").reshape(3, 4))},
        coords={"time": [0, 1, 2], "lat": [10.0, 20.0, 30.0, 40.0]},
        attrs={"title": "synthetic"},
    )
    path = root / "sample.nc"
    ds.to_netcdf(path)
    return path


def make_hdf5(root: Path) -> Path:
    path = root / "sample.h5"
    with h5py.File(path, "w") as handle:
        group = handle.create_group("group")
        group.create_dataset("data", data=np.arange(10, dtype="int16"))
        group.attrs["note"] = "synthetic"
    return path


def make_zarr(root: Path) -> Path:
    ds = xr.Dataset({"value": (("x",), np.array([1.0, 2.0, 3.0]))})
    path = root / "sample.zarr"
    ds.to_zarr(path, consolidated=False)
    return path


def make_geotiff(root: Path) -> Path:
    path = root / "sample.tif"
    with rasterio.open(
        path, "w", driver="GTiff", height=4, width=5, count=1, dtype="uint8",
        crs="EPSG:4326", transform=from_origin(-60.0, 5.0, 0.1, 0.1),
    ) as dst:
        dst.write(np.arange(20, dtype="uint8").reshape(4, 5), 1)
    return path


def test_netcdf_inspect_and_preview(tmp_path):
    path = make_netcdf(tmp_path)
    result = inspector.inspect(config(tmp_path), path)
    assert result["ok"] is True
    meta = result["metadata"]
    assert meta["format"] == "netcdf"
    assert "temp" in {v["name"] for v in meta["variables"]}
    preview = inspector.preview(config(tmp_path), path, variable="temp")
    assert preview["ok"] is True
    assert preview["stats"]["min"] == 0.0
    assert preview["stats"]["max"] == 11.0
    selected = inspector.preview(config(tmp_path), path, variable="temp", selector={"time": 1})
    assert selected["shape"] == [4]
    assert selected["stats"]["mean"] == pytest.approx(5.5)


def test_hdf5_inspect_and_preview(tmp_path):
    path = make_hdf5(tmp_path)
    result = inspector.inspect(config(tmp_path), path)
    assert result["ok"] is True
    assert result["metadata"]["format"] == "hdf5"
    assert any(node["path"] == "group/data" for node in result["metadata"]["nodes"])
    preview = inspector.preview(config(tmp_path), path, variable="group/data")
    assert preview["stats"]["min"] == 0
    assert preview["stats"]["max"] == 9


def test_zarr_inspect_and_preview(tmp_path):
    path = make_zarr(tmp_path)
    result = inspector.inspect(config(tmp_path), path)
    assert result["ok"] is True
    assert result["metadata"]["format"] == "zarr"
    preview = inspector.preview(config(tmp_path), path, variable="value")
    assert preview["shape"] == [3]
    assert preview["stats"]["count"] == 3


def test_geotiff_inspect_and_preview(tmp_path):
    path = make_geotiff(tmp_path)
    result = inspector.inspect(config(tmp_path), path)
    assert result["ok"] is True
    meta = result["metadata"]
    assert meta["format"] == "geotiff"
    assert meta["count"] == 1
    assert meta["crs"] == "EPSG:4326"
    assert meta["width"] == 5 and meta["height"] == 4
    preview = inspector.preview(config(tmp_path), path, band=1)
    assert preview["stats"]["min"] == 0
    assert preview["stats"]["max"] == 19


def test_outside_root_and_symlink_denied(tmp_path):
    root = tmp_path / "allowed"
    root.mkdir()
    outside = tmp_path / "outside.nc"
    outside.write_bytes(b"x")
    with pytest.raises(policy.ScientificDenied):
        policy.validate_path(config(root), outside)
    link = root / "link.nc"
    link.symlink_to(outside)
    with pytest.raises(policy.ScientificDenied):
        policy.validate_path(config(root), link)


def test_unsupported_format_and_bad_selector(tmp_path):
    path = tmp_path / "text.txt"
    path.write_text("x")
    with pytest.raises(policy.ScientificDenied):
        policy.validate_path(config(tmp_path), path)
    netcdf = make_netcdf(tmp_path)
    with pytest.raises(inspector.InspectError) as exc:
        inspector.preview(config(tmp_path), netcdf, variable="temp", selector={"time": 99})
    assert exc.value.code == "SELECTOR_INVALID"


def test_preview_is_capped(tmp_path):
    ds = xr.Dataset({"big": (("x", "y"), np.zeros((100, 100), dtype="float32"))})
    path = tmp_path / "big.nc"
    ds.to_netcdf(path)
    preview = inspector.preview(config(tmp_path), path, variable="big", max_points=100)
    assert preview["ok"] is True
    assert preview["preview_limited"] is True
    assert max(preview["shape"]) <= 10


def test_mcp_tool_names():
    from integrations.scientific_data.mcp_server import TOOL_NAMES

    assert TOOL_NAMES == {"scientific_status", "scientific_inspect", "scientific_preview"}
