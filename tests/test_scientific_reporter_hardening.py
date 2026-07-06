# -*- coding: utf-8 -*-

from pathlib import Path
import warnings


def test_scientific_reporter_source_compiles_without_syntaxwarning():
    source_path = Path("mci/scientific_reporter.py")
    source = source_path.read_text(encoding="utf-8")

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        compile(source, str(source_path), "exec")
