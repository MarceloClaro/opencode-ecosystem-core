"""R925: árvores agregadas continuam sensíveis aos bytes, não são ignore lists."""
import json
from pathlib import Path

import pytest

from sdd.tdd_history import TDDHistory


@pytest.fixture
def managed(tmp_path):
    root=tmp_path/'project'; root.mkdir(); (root/'production.py').write_text('value=1\n')
    env=root/'.its-fine/venvs/hf-tts'; site=env/'lib/python3.12/site-packages'
    (site/'dependency').mkdir(parents=True)
    (site/'dependency/code.py').write_text('value=2\n')
    (env/'owned_wrapper.py').write_text('value=3\n')
    (env/'pyvenv.cfg').write_text('home = /python\nversion_info = 3.12.14\n')
    (env/'core-environment.json').write_text(json.dumps({'kind':'core_itsfine_environment_v1','root':str(root),'group':'voice'}))
    history=TDDHistory(root=root,state_dir=tmp_path/'private-history')
    return root,env,site,history


def test_managed_dependency_sources_are_hashed_not_dropped(managed):
    root,env,site,history=managed
    result=history._sources()
    trees=result.get('dependency_trees',{})
    key=site.relative_to(root).as_posix()
    assert key in trees, 'Dependências ainda não têm representação agregada'
    assert trees[key]['source_files']==1 and len(trees[key]['sha256'])==64
    assert 'production.py' in result['files']
    assert (env/'owned_wrapper.py').relative_to(root).as_posix() in result['files']
    assert (site/'dependency/code.py').relative_to(root).as_posix() not in result['files']


def test_dependency_change_changes_current_source_identity(managed):
    _,_,site,history=managed
    before=history._sources()
    (site/'dependency/code.py').write_text('value=999\n')
    after=history._sources()
    assert before!=after
    assert before.get('dependency_trees')!=after.get('dependency_trees'), 'Fonte omitida em vez de hasheada'


def test_unmanaged_tree_is_not_exempt_and_symlinks_fail_closed(managed):
    root,env,site,history=managed
    (env/'core-environment.json').unlink()
    result=history._sources()
    assert (site/'dependency/code.py').relative_to(root).as_posix() in result['files']
    (env/'core-environment.json').write_text(json.dumps({'kind':'core_itsfine_environment_v1','root':str(root),'group':'voice'}))
    (site/'dependency/code.py').unlink()
    (site/'dependency/code.py').symlink_to(root/'production.py')
    try: history._sources()
    except ValueError: pass
    else: assert False, 'Fonte symlink foi aceita no agregado'


def test_lock_and_receipt_changes_change_source_identity(managed):
    root,_,_,history=managed
    locks=root/'integrations/itsfine-locks'; locks.mkdir(parents=True)
    lock=locks/'voice-py312.txt'; lock.write_text('dependency==1\n')
    receipts=root/'.its-fine/core/engines'; receipts.mkdir(parents=True)
    receipt=receipts/'hf-tts.json'; receipt.write_text('{"status":"not_prepared"}')
    before=history._sources()
    lock.write_text('dependency==2\n')
    middle=history._sources()
    receipt.write_text('{"status":"prepared_cpu"}')
    after=history._sources()
    assert before!=middle, 'Mudança no lock não foi atestada'
    assert middle!=after, 'Mudança no recibo não foi atestada'
