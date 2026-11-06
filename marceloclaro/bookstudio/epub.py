"""Auditoria e patch de acessibilidade de EPUB3."""
from __future__ import annotations

from datetime import datetime, timezone
import posixpath
import re
from pathlib import Path
from typing import Any, Dict
import zipfile
from xml.etree import ElementTree as ET


class EpubError(ValueError):
    """EPUB inválido ou sem estrutura esperada."""


def _opf_path(archive: zipfile.ZipFile) -> str:
    try:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
    except KeyError as exc:
        raise EpubError("META-INF/container.xml ausente") from exc
    rootfile = container.find(
        ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
    )
    if rootfile is None or not rootfile.get("full-path"):
        raise EpubError("container.xml sem rootfile")
    return rootfile.get("full-path")


def audit_epub(path: str | Path) -> Dict[str, Any]:
    target = Path(path).expanduser().resolve()
    if not target.is_file():
        raise EpubError(f"EPUB ausente: {target}")
    result: Dict[str, Any] = {
        "path": str(target),
        "bytes": target.stat().st_size,
        "mimetype_first": False,
        "mimetype_stored": False,
        "opf": None,
        "title": None,
        "language": None,
        "identifier": None,
        "spine_items": 0,
        "manifest_items": 0,
        "images": 0,
        "img_tags": 0,
        "img_with_alt": 0,
        "accessibility_summary": False,
        "accessibility_features": [],
    }
    with zipfile.ZipFile(target) as archive:
        names = archive.namelist()
        result["mimetype_first"] = bool(names) and names[0] == "mimetype"
        if "mimetype" in names:
            info = archive.getinfo("mimetype")
            result["mimetype_stored"] = info.compress_type == zipfile.ZIP_STORED
        opf_path = _opf_path(archive)
        result["opf"] = opf_path
        opf_text = archive.read(opf_path).decode("utf-8", "replace")
        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        opf = ET.fromstring(opf_text)
        result["title"] = (opf.findtext(".//dc:title", namespaces=ns) or "").strip() or None
        result["language"] = (opf.findtext(".//dc:language", namespaces=ns) or "").strip() or None
        result["identifier"] = (opf.findtext(".//dc:identifier", namespaces=ns) or "").strip() or None
        result["spine_items"] = len(opf.findall(".//opf:itemref", ns))
        result["manifest_items"] = len(opf.findall(".//opf:item", ns))
        result["accessibility_summary"] = "schema:accessibilitySummary" in opf_text
        result["accessibility_features"] = re.findall(
            r'property="schema:accessibilityFeature"[^>]*>([^<]+)<', opf_text
        )
        base = posixpath.dirname(opf_path)
        for href in re.findall(r'<item[^>]+href="([^"]+)"[^>]*media-type="application/xhtml\+xml"', opf_text):
            xhtml_path = posixpath.normpath(posixpath.join(base, href))
            if xhtml_path not in names:
                continue
            data = archive.read(xhtml_path).decode("utf-8", "replace")
            result["img_tags"] += len(re.findall(r"<img\b", data, re.I))
            result["img_with_alt"] += len(re.findall(r"<img\b[^>]*\balt\s*=", data, re.I))
        result["images"] = sum(
            1 for name in names
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg"))
        )
    return result


def patch_accessibility_summary(epub: str | Path, summary: str,
                                output: str | Path | None = None) -> Path:
    """Insere ``schema:accessibilitySummary`` no OPF e reescreve o EPUB.

    Preserva ``mimetype`` como primeira entrada e sem compressão, requisito
    do EPUB3. O patch é idempotente.
    """
    source = Path(epub).expanduser().resolve()
    target = Path(output).expanduser().resolve() if output else source
    if not source.is_file():
        raise EpubError(f"EPUB ausente: {source}")
    if not isinstance(summary, str) or not summary.strip():
        raise EpubError("summary não pode ser vazio")

    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        opf_path = _opf_path(archive)
        opf_text = archive.read(opf_path).decode("utf-8", "replace")
        if "schema:accessibilitySummary" not in opf_text:
            meta = (
                '    <meta property="schema:accessibilitySummary">'
                f"{summary.strip()}"
                "</meta>\n"
            )
            if "</metadata>" not in opf_text:
                raise EpubError("OPF sem </metadata>")
            opf_text = opf_text.replace("</metadata>", meta + "  </metadata>", 1)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        opf_text = re.sub(
            r'(<meta property="dcterms:modified">)[^<]*(</meta>)',
            rf"\g<1>{now}\g<2>",
            opf_text,
        )
        payload = {name: archive.read(name) for name in names}

    temp = target.with_suffix(target.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w") as out:
        for name in names:
            if name == opf_path:
                data = opf_text.encode("utf-8")
            else:
                data = payload[name]
            if name == "mimetype":
                out.writestr(zipfile.ZipInfo("mimetype"), data, compress_type=zipfile.ZIP_STORED)
            else:
                out.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
    temp.replace(target)
    return target
