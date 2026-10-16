"""R908: rejeição de prova incompleta, proposição falsa e recibo obsoleto."""
from pathlib import Path
import importlib.util
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_formal_book_verifier_exists_before_any_formal_claim():
    assert (ROOT / 'scripts/verify_book_lean.py').is_file(), 'verificador reexecutável ausente'


def _module():
    spec = importlib.util.spec_from_file_location('r908_verify', ROOT / 'scripts/verify_book_lean.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_unproved_terms_are_rejected_in_real_source():
    assert (ROOT / 'scripts/verify_book_lean.py').is_file(), 'verificador reexecutável ausente'
    module = _module()
    for source in ['theorem bad : False := by sorry', 'axiom invented : False',
                   'theorem bad : False := by admit']:
        assert module.source_policy_errors(source)
    assert not module.source_policy_errors('theorem ok : 1 = 1 := by rfl')


def test_changed_sources_invalidate_receipt(tmp_path):
    assert (ROOT / 'scripts/verify_book_lean.py').is_file(), 'verificador reexecutável ausente'
    module = _module()
    source = tmp_path / 'Example.lean'
    source.write_text('theorem ok : 1 = 1 := by rfl\n')
    receipt = {'files': {'Example.lean': {'sha256': module.file_sha256(source)}}}
    assert module.receipt_matches_sources(receipt, tmp_path)
    source.write_text('theorem ok : 1 = 2 := by rfl\n')
    assert not module.receipt_matches_sources(receipt, tmp_path)


@pytest.mark.parametrize('name', ['chapter.tex', 'map.json', 'verifier.py'])
def test_changed_book_or_method_invalidates_receipt(tmp_path, name):
    module = _module()
    path = tmp_path/name
    path.write_text('original')
    receipt = {'context_files': {name: {'sha256': module.file_sha256(path)}}}
    assert module.receipt_matches_sources(receipt, tmp_path)
    path.write_text('changed')
    assert not module.receipt_matches_sources(receipt, tmp_path)


def test_correct_revision_with_dirty_dependency_is_rejected(tmp_path):
    import subprocess
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tmp_path), *args], text=True).strip()
    git('init', '-q')
    path = tmp_path/'proof.lean'
    path.write_text('theorem ok : 1=1 := by rfl')
    git('add', 'proof.lean')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
    rev = git('rev-parse', 'HEAD')
    assert _module().checked_dependency(tmp_path, rev)['tracked_worktree_clean'] is True
    path.write_text('changed')
    with pytest.raises(ValueError):
        _module().checked_dependency(tmp_path, rev)


def test_duplicate_axiom_output_cannot_hide_an_unproved_dependency():
    module = _module()
    for first in ['[sorryAx]', '[propext]']:
        output = (f"'Book.foo' depends on axioms: {first}\n"
                  "'Book.foo' does not depend on any axioms")
        with pytest.raises(ValueError):
            module.parse_axioms(output, ['Book.foo'])


def test_missing_or_unapproved_axiom_audits_are_rejected():
    module = _module()
    for output in ['', "'Book.foo' depends on axioms: [invented]"]:
        with pytest.raises(ValueError):
            module.parse_axioms(output, ['Book.foo'])
    assert module.parse_axioms("'Book.foo' depends on axioms: [propext, Classical.choice]",
                               ['Book.foo']) == {'Book.foo': ['propext', 'Classical.choice']}


@pytest.mark.parametrize('declaration', ['@[simp] theorem hidden', 'private theorem hidden',
                                          ' theorem hidden'])
def test_uninventoried_theorems_cannot_bypass_axiom_audit(declaration):
    source = ('namespace Book\ntheorem visible : 1=1 := by rfl\n'
              + declaration + ' : 2=2 := by rfl\nend Book')
    with pytest.raises(ValueError):
        _module().theorem_names(source)


def test_nested_comments_do_not_hide_holes_in_the_actual_source():
    module = _module()
    assert not module.source_policy_errors('/- sorry /- axiom -/ admit -/\ntheorem ok : 1=1 := by rfl')
    assert module.source_policy_errors('/- comment /- nested -/ -/\ntheorem bad : False := by sorry')


def test_missing_environment_is_not_a_proof(tmp_path):
    result = _module().run_lean('theorem ok : 1=1 := by rfl', tmp_path)
    assert result['status'] == 'environment_unavailable'
    assert result['returncode'] is None


def test_real_kernel_rejects_mutated_ema_calculation():
    project = ROOT/'livro-core/lean'
    if not (project / '.lake/packages/mathlib').is_dir():
        pytest.skip('Integração exige Lean/Mathlib; o gate de publicação continua obrigatório')
    module = _module()
    source = ('import Mathlib\nnamespace Mutation\n'
              'theorem ema : (7/10 : ℚ)*(1/2)+(3/10)*(9/10)=31/50 := by norm_num\n'
              'end Mutation\n')
    green = module.run_lean(source, project, audit_names=['Mutation.ema'])
    assert green['status'] == 'machine_checked', green
    red = module.run_lean(source.replace('=31/50', '=32/50'), project,
                          audit_names=['Mutation.ema'])
    assert red['status'] == 'compiler_rejected', red


def test_book_map_cannot_cite_a_nonexistent_proof():
    mapping = {'families': [{'id': 'F01', 'kind': 'formal_model',
                            'theorems': ['Book.missing'],
                            'book_sources': ['livro-core/mod-01-fundacoes.tex'],
                            'hypotheses_and_limits': 'Assumptions'}]}
    with pytest.raises(ValueError):
        _module().validate_math_map(mapping, {'Book.real'})


def test_observations_cannot_be_promoted_to_formal_proof():
    mapping = {'families': [{'id': 'F27', 'kind': 'empirical_not_formalized',
                            'theorems': ['Book.real'],
                            'book_sources': ['livro-core/mod-01-fundacoes.tex'],
                            'hypotheses_and_limits': 'Observed input'}]}
    with pytest.raises(ValueError):
        _module().validate_math_map(mapping, {'Book.real'})


def test_source_inventory_excludes_compiler_cache(tmp_path):
    spec = importlib.util.spec_from_file_location('book_inventory', ROOT/'livro-core/gen_inventario.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path/'proofs/Example.lean'
    source.parent.mkdir()
    source.write_text('theorem ok : 1=1 := by rfl')
    cache = source.parent/'.lake/build/transient.olean'
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b'cache')
    chapter = tmp_path/'chapter.tex'
    chapter.write_text(r'\fontecore{proofs/}{Formal sources}')
    assert module._cited_files(tmp_path, [chapter]) == {source}
