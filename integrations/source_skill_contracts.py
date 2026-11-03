"""R1023 — verificador local de registros de evidência das skills de fonte.

Este módulo é somente leitura e sem rede. Ele responde se um registro está
estruturalmente apto a seguir para revisão humana; nunca confirma direitos,
vigência, autenticidade remota ou conteúdo. Nenhuma instrução contida na fonte
é interpretada ou executada.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from urllib.parse import urlsplit

MAX_INPUT_BYTES = 1024 * 1024
SHA256 = re.compile(r"^[0-9a-f]{64}$")
WHITESPACE = re.compile(r"[\s\u0000-\u001f\u007f]")
BOOK_RIGHTS = frozenset(
    {"public_domain", "cc_by", "cc_by_sa", "cc_by_nc_sa", "authorized", "institutional_license"}
)
BOOK_COVERAGE = frozenset({"complete", "partial", "sample"})
BOOK_SOURCE_ROLES = frozenset({"primary_text", "catalog_record", "ai_summary"})
LEGAL_RECORD_TYPES = frozenset(
    {"enacted_norm", "historical_text", "consolidated", "proposal"}
)
OFFICIAL_HOSTS = frozenset(
    {
        "www.planalto.gov.br",
        "planalto.gov.br",
        "www2.al.ce.gov.br",
        "normas.leg.br",
        "www.in.gov.br",
        "legislacao.presidencia.gov.br",
        "www.camara.leg.br",
        "www12.senado.leg.br",
        "www.senado.leg.br",
        "www.stf.jus.br",
        "www.cnj.jus.br",
        "www.tre-ce.jus.br",
    }
)


class ContractInputError(ValueError):
    """Entrada inválida, com código estável para a CLI."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _non_empty_text(value):
    return isinstance(value, str) and bool(value.strip())


def _string_list(value):
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _sha256(value):
    return isinstance(value, str) and bool(SHA256.fullmatch(value.lower()))


def _https_url(value):
    if not _non_empty_text(value) or WHITESPACE.search(value):
        return None
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        return None
    return host


def _iso_date(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _iso_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _result(reasons, *, content_verified=False, rights_verified=False,
            validity_verified=False):
    return {
        "status": "blocked" if reasons else "candidate_for_review",
        "reasons": list(reasons),
        "content_verified": content_verified,
        "rights_verified": rights_verified,
        "validity_verified": validity_verified,
        "actions_executed": [],
        "review_required": True,
    }


def assess_book(record):
    """Valida o registro de extração de livro; não lê a obra nem a URL."""
    if not isinstance(record, dict):
        return _result(["record_not_object"])
    reasons = []
    if not _non_empty_text(record.get("title")):
        reasons.append("title_missing")
    if not _non_empty_text(record.get("author")):
        reasons.append("author_missing")
    if not _non_empty_text(record.get("edition")):
        reasons.append("edition_missing")
    if not _https_url(record.get("source_url")):
        reasons.append("source_url_invalid")
    if not _sha256(record.get("source_sha256")):
        reasons.append("hash_invalid")
    rights = record.get("rights_basis")
    if rights == "unknown" or rights is None:
        reasons.append("rights_unresolved")
    elif rights not in BOOK_RIGHTS:
        reasons.append("rights_basis_invalid")
    if not _non_empty_text(record.get("rights_evidence")):
        reasons.append("rights_evidence_missing")
    if record.get("text_available") is not True:
        reasons.append("text_unavailable")
    if record.get("coverage") not in BOOK_COVERAGE:
        reasons.append("coverage_invalid")
    role = record.get("source_role")
    if role not in BOOK_SOURCE_ROLES:
        reasons.append("source_role_invalid")
    elif role == "ai_summary":
        reasons.append("primary_source_required")
    if not _string_list(record.get("locators")):
        reasons.append("locators_missing")
    if record.get("execute_source_instructions") is not False:
        reasons.append("source_instructions_forbidden")
    return _result(reasons)


def assess_legislation(record):
    """Valida o registro de consulta legal; não certifica vigência nem acesso."""
    if not isinstance(record, dict):
        return _result(["record_not_object"])
    reasons = []
    if not _non_empty_text(record.get("law_id")):
        reasons.append("law_id_missing")
    if not _non_empty_text(record.get("jurisdiction")):
        reasons.append("jurisdiction_missing")
    if not _iso_date(record.get("as_of")):
        reasons.append("reference_date_invalid")
    if not _iso_timestamp(record.get("retrieved_at")):
        reasons.append("retrieval_date_invalid")
    host = _https_url(record.get("source_url"))
    if host is None or host not in OFFICIAL_HOSTS:
        reasons.append("official_source_required")
    if not _sha256(record.get("source_sha256")):
        reasons.append("hash_invalid")
    if not _non_empty_text(record.get("text_version")):
        reasons.append("text_version_missing")
    record_type = record.get("record_type")
    if record_type not in LEGAL_RECORD_TYPES:
        reasons.append("record_type_invalid")
    elif record_type == "proposal":
        reasons.append("proposal_not_enacted")
    if record.get("claim_current_validity") is not False:
        reasons.append("validity_requires_legal_review")
    if record.get("text_available") is not True:
        reasons.append("text_unavailable")
    if not _string_list(record.get("locators")):
        reasons.append("locators_missing")
    return _result(reasons)


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractInputError("duplicate_key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ContractInputError("non_finite_number")


def load_record(raw):
    """Decodifica JSON estrito, limitado a 1 MiB, sem aceitar NaN/duplicatas."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "strict")
    if not isinstance(raw, str):
        raise ContractInputError("input_not_text")
    if len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ContractInputError("input_too_large")
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except ContractInputError:
        raise
    except (ValueError, TypeError) as exc:
        raise ContractInputError("invalid_json") from exc
    if not isinstance(value, dict):
        raise ContractInputError("record_not_object")
    return value


def _emit(value):
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _blocked_input(code):
    _emit({"status": "blocked", "reasons": [code], "content_verified": False,
           "rights_verified": False, "validity_verified": False,
           "actions_executed": [], "review_required": True})


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="source-skill-contracts",
        description="Verifica registros locais das skills de fonte (sem rede).",
    )
    parser.add_argument("kind", choices=("book", "legislation"))
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
        record = load_record(raw)
    except (ContractInputError, UnicodeDecodeError, OSError) as exc:
        _blocked_input(getattr(exc, "code", "input_invalid"))
        return 2
    result = assess_book(record) if args.kind == "book" else assess_legislation(record)
    _emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
