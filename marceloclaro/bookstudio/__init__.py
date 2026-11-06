"""Book Studio Universal — contratos e gates da fase R1078."""
from .contracts import (
    BookProject,
    PROJECT_FILE,
    load_project,
    save_project,
    validate_isbn,
)
from .kdp import (
    InkType,
    KDPCoverSpec,
    KDPError,
    PaperStock,
    is_kdp_trim_supported,
    kdp_cover_spec,
    parse_trim,
)
from .license_gate import (
    IntegrationMode,
    LicenseClass,
    LicenseDecision,
    LicenseViolation,
    assert_landscape,
    classify_license,
    evaluate,
    validate_landscape,
)
from .release import Artifact, ReleaseManifest, ReleaseError, sha256_file
from .tokens import (
    DesignTokens,
    PaletteEntry,
    TokenError,
    contrast_ratio,
    cmyk_tac,
    default_tokens,
)

__all__ = [
    "Artifact",
    "BookProject",
    "DesignTokens",
    "InkType",
    "IntegrationMode",
    "KDPCoverSpec",
    "KDPError",
    "LicenseClass",
    "LicenseDecision",
    "LicenseViolation",
    "PROJECT_FILE",
    "PaletteEntry",
    "PaperStock",
    "ReleaseError",
    "ReleaseManifest",
    "TokenError",
    "assert_landscape",
    "classify_license",
    "contrast_ratio",
    "cmyk_tac",
    "default_tokens",
    "evaluate",
    "is_kdp_trim_supported",
    "kdp_cover_spec",
    "load_project",
    "parse_trim",
    "save_project",
    "sha256_file",
    "validate_isbn",
    "validate_landscape",
]

__version__ = "0.1.0"
