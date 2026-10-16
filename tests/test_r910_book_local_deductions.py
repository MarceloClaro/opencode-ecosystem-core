"""R910: rastreabilidade editorial; não é cobertura funcional nem prova Lean."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_each_formal_family_has_local_exposition():
    mapping = json.loads((ROOT / 'docs/book-math-map-r908.json').read_text())
    missing = []
    for f in mapping['families']:
        if f['kind'] == 'empirical_not_formalized':
            continue
        for source in f['book_sources']:
            text = (ROOT / source).read_text()
            if not re.search(r'\\begin\{formalizacao\}\{' + f['id'] + r'\}', text):
                missing.append((f['id'], source))
    assert missing == [], f'Deduções ainda sem exposição local: {missing}'


def test_derived_probability_rules_are_not_called_axioms():
    text = (ROOT / 'livro-core/mod-01-fundacoes.tex').read_text()
    assert 'axioma de multiplicação' not in text
    assert 'Axioma da probabilidade total' not in text


def test_explicit_foundation_bridge_and_didactic_calculations_exist():
    from scripts.verify_book_lean import theorem_names
    foundation = set(theorem_names((ROOT / 'livro-core/lean/Foundations.lean').read_text()))
    models = set(theorem_names((ROOT / 'livro-core/lean/Models.lean').read_text()))
    assert 'BookFoundations.independent_error_probability_real' in foundation
    assert {'BookModels.four_fifths_exact', 'BookModels.two_sixths_exact',
            'BookModels.eight_tenths_exact', 'BookModels.three_tenths_exact',
            'BookModels.three_fourths_exact', 'BookModels.zero_elevenths_exact',
            'BookModels.coverage_complement_bounds'} <= models


def test_validator_implementation_exists_before_use():
    assert (ROOT / 'scripts/book_local_deductions.py').is_file()


def test_axiom_annotations_have_generator():
    assert (ROOT / 'livro-core/gen_lean_axioms.py').is_file()


import copy
import hashlib
import importlib.util
import pytest
from scripts.book_local_deductions import validate_local_deductions


def _editorial_fixture():
    mapping = {'families': [{'id': 'F01', 'kind': 'formal_model',
                             'book_sources': ['chapter.tex'], 'theorems': ['Book.lemma']}]}
    text = r"""
\begin{formalizacao}{F01}{Complemento}
\textbf{Enunciado.} A conclusão é uma identidade condicional.
\textbf{Hipóteses.} As massas são finitas e normalizadas.
\textbf{Lemas e dedução.} Adicionam-se massas de conjuntos disjuntos.
\textbf{Lean 4.} \leanref{Book.lemma} é o enunciado identificado.
\textbf{Axiomas e alcance.} Consultar \ref{sec:fundamentos-lean}; sem evidência empírica.
\end{formalizacao}
"""
    return mapping, {'chapter.tex': text}, {'Book.lemma': ['propext']}


def test_editorial_validator_accepts_explicit_contract():
    result = validate_local_deductions(*_editorial_fixture())
    assert result['status'] == 'editorial_links_checked'
    assert result['family_source_pairs'] == 1


@pytest.mark.parametrize('mutation', ['missing', 'fake_name', 'no_hypothesis', 'empirical', 'commented'])
def test_editorial_validator_rejects_broken_traceability(mutation):
    mapping, texts, audit = _editorial_fixture()
    if mutation == 'missing':
        texts['chapter.tex'] = ''
    elif mutation == 'fake_name':
        texts['chapter.tex'] = texts['chapter.tex'].replace('Book.lemma', 'Book.invented')
    elif mutation == 'no_hypothesis':
        texts['chapter.tex'] = texts['chapter.tex'].replace(r'\textbf{Hipóteses.}', r'\textbf{Conjectura.}')
    elif mutation == 'empirical':
        mapping['families'][0]['kind'] = 'empirical_not_formalized'
    else:
        texts['chapter.tex'] = '\n'.join('%' + line for line in texts['chapter.tex'].splitlines())
    with pytest.raises(ValueError):
        validate_local_deductions(mapping, texts, audit)


def test_axiom_generator_rejects_stale_source_and_forbidden_axiom(tmp_path):
    spec = importlib.util.spec_from_file_location('book_axioms', ROOT / 'livro-core/gen_lean_axioms.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / 'example.lean'
    path.write_text('theorem example : True := True.intro')
    receipt = {'status': 'machine_checked', 'files': {'example.lean': {
        'status': 'machine_checked', 'returncode': 0,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'theorems': ['Book.example'], 'axioms': {'Book.example': []}}}}
    assert r'\endcsname{nenhum}' in module.render_axiom_macros(receipt, tmp_path)
    corrupt = copy.deepcopy(receipt)
    corrupt['files']['example.lean']['axioms']['Book.example'] = ['sorryAx']
    with pytest.raises(ValueError, match='Axioma'):
        module.render_axiom_macros(corrupt, tmp_path)
    path.write_text('changed')
    with pytest.raises(ValueError, match='diverge'):
        module.render_axiom_macros(receipt, tmp_path)


def test_entire_book_has_audited_editorial_links():
    mapping = json.loads((ROOT / 'docs/book-math-map-r908.json').read_text())
    receipt = json.loads((ROOT / 'docs/verification-book-lean-r908.json').read_text())
    audit = {n: ax for result in receipt['files'].values() for n, ax in result['axioms'].items()}
    texts = {str(p.relative_to(ROOT)): p.read_text() for p in (ROOT/'livro-core').glob('mod-*.tex')}
    assert validate_local_deductions(mapping, texts, audit)['status'] == 'editorial_links_checked'


def test_remaining_local_instances_have_named_propositions():
    from scripts.verify_book_lean import theorem_names
    models = theorem_names((ROOT / 'livro-core/lean/Models.lean').read_text())
    attention = theorem_names((ROOT / 'livro-core/lean/Attention.lean').read_text())
    assert 'BookModels.eighteen_twentieths_exact' in models
    assert 'BookAttention.eligible_maximum_exists' in attention


def test_complete_count_ratio_requires_nonzero_total():
    from scripts.verify_book_lean import theorem_names
    assert 'BookModels.full_coverage_identity' in theorem_names((ROOT / 'livro-core/lean/Models.lean').read_text())


def test_matrix_and_concentration_steps_are_not_unproved_labels():
    from scripts.verify_book_lean import theorem_names
    names = set(theorem_names((ROOT / 'livro-core/lean/Models.lean').read_text()))
    assert {'BookModels.attention_output_identity', 'BookModels.attention_matrix_scale',
            'BookModels.reference_concentration_exact'} <= names


def test_high_accuracy_risk_has_rounding_precision():
    text = (ROOT / 'livro-core/lean/Algebra.lean').read_text()
    section = text.split('theorem independent_error_216_high_accuracy_interval', 1)[1].split('theorem ', 1)[0]
    assert '(19435 : ℝ) / 100000' in section
    assert '(19436 : ℝ) / 100000' in section


def test_short_exact_statement_is_not_rejected_by_length():
    mapping, texts, audit = _editorial_fixture()
    texts['chapter.tex'] = texts['chapter.tex'].replace('A conclusão é uma identidade condicional.', '$2/6=1/3$.')
    assert validate_local_deductions(mapping, texts, audit)['local_blocks'] == 1


def test_every_named_book_proposition_is_referenced_in_the_exposition():
    from scripts.verify_book_lean import theorem_names
    known = {n for p in (ROOT / 'livro-core/lean').glob('*.lean') for n in theorem_names(p.read_text())}
    used = {n for p in (ROOT / 'livro-core').glob('mod-*.tex') for n in re.findall(r'\\leanref\{([\w.]+)\}', p.read_text())}
    assert known - used == set()
