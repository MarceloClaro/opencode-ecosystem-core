"""Contratos de partição; fixtures não são o vídeo do usuário."""
import importlib.util
import json
import copy
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1]/'integrations/video_segment_audit.py'


def api():
    assert MODULE.is_file(), 'segmentador ainda ausente'
    spec=importlib.util.spec_from_file_location('video_segment_audit', MODULE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_full_coverage_and_tail():
    m=api();p=m.plan_segments('video-id', 10001, '25/1')
    assert p['segments'][0]['start_frame']==0
    assert p['segments'][-1]['end_frame']==10001
    assert sum(s['end_frame']-s['start_frame'] for s in p['segments'])==10001
    assert m.validate_coverage(p)


def test_every_segment_in_target_when_feasible():
    m=api();p=m.plan_segments('id', 25*400,'25/1')
    assert all(60 <= s['duration_seconds'] <= 90 for s in p['segments'])


def test_short_video_never_discarded():
    m=api();p=m.plan_segments('id',25*31,'25/1')
    assert len(p['segments'])==1 and p['segments'][0]['duration_seconds']==31
    assert p['segments'][0]['duration_exception']


def test_scene_candidate_preferred_near_target():
    m=api();p=m.plan_segments('id',25*150,'25/1',scene_frames=[25*72])
    assert p['segments'][0]['end_frame']==25*72
    assert p['segments'][0]['boundary_kind']=='scene_candidate'


def test_gap_and_overlap_are_rejected():
    m=api();p=m.plan_segments('id',25*150,'25/1')
    p['segments'][1]['start_frame']+=1
    with pytest.raises(ValueError):m.validate_coverage(p)
    p['segments'][1]['start_frame']-=2
    with pytest.raises(ValueError):m.validate_coverage(p)


def test_context_not_counted_in_editorial_coverage():
    m=api();p=m.plan_segments('id',25*150,'25/1',context_seconds=2)
    assert p['segments'][0]['context_end_frame']>p['segments'][0]['end_frame']
    assert p['segments'][1]['context_start_frame']<p['segments'][1]['start_frame']
    assert m.validate_coverage(p)


def test_stable_ids_and_fractional_fps():
    m=api();a=m.plan_segments('02XpQTA-_XE',9000,'30000/1001');b=m.plan_segments('02XpQTA-_XE',9000,'30000/1001')
    assert a==b
    assert a['segments'][0]['id']=='02XpQTA-_XE-P0001'
    assert abs(a['duration_seconds']-300.3)<1e-8


@pytest.mark.parametrize('total,fps',[(0,'25/1'),(10,'0/1'),(10,'25/0'),(True,'25/1'),(-1,'25/1')])
def test_bad_source_rejected(total,fps):
    with pytest.raises(ValueError):api().plan_segments('id',total,fps)


def test_assembly_blocks_unedited_unapproved():
    m=api();p=m.plan_segments('id',25*75,'25/1')
    with pytest.raises(ValueError,match='approval|edited'):m.assembly_inputs(p)


def test_assembly_binds_approval_to_current_hash(tmp_path):
    m=api();p=ready_plan(m,tmp_path)
    output=Path(p['segments'][0]['edited']['path'])
    assert m.assembly_inputs(p)==[str(output)]
    output.write_bytes(b'modified')
    with pytest.raises(ValueError,match='hash'):m.assembly_inputs(p)


def ready_plan(m, tmp_path, seconds=75):
    """Invented receipts ONLY exercise policy; the bytes are not real media."""
    p=m.plan_segments('fixture',25*seconds,'25/1')
    source=tmp_path/'source.fixture';source.write_bytes(b'not media: policy fixture')
    p['source']={'path':str(source),'sha256':m.sha256_file(source),
                 'timing_verified':True,'timing_mode':'cfr','has_audio':True}
    binding=m.plan_digest(p)
    for i,s in enumerate(p['segments']):
        out=tmp_path/f'output-{i}.fixture';out.write_bytes(f'not media {i}'.encode())
        digest=m.sha256_file(out)
        s['edited']={'path':str(out),'sha256':digest}
        s['technical_qa']={'passed':True,'artifact_sha256':digest,'plan_sha256':binding,
            'frame_count':s['end_frame']-s['start_frame'],'fps':p['fps'],
            'duration_seconds':s['duration_seconds'],'audio_present':True,
            'decode_errors':0,'av_sync_reviewed':True,
            'stream_signature':{'video_codec':'fixture','width':128,'height':72,
                'pixel_format':'yuv420p','audio_codec':'fixture','sample_rate':48000,'channels':2}}
        s['approval']={'approved':True,'reviewer':'fixture-not-human-approval',
            'technical_qa':True,'audiovisual_review':True,'artifact_sha256':digest,
            'plan_sha256':binding}
    return p


def test_infeasible_range_is_explicit():
    m=api();p=m.plan_segments('id',25*91,'25/1')
    assert sum(s['end_frame']-s['start_frame'] for s in p['segments'])==25*91
    assert all(s['duration_exception'] for s in p['segments'])
    assert all(s['review_required'] for s in p['segments'])


def test_boundaries_reserve_feasible_tail():
    p=api().plan_segments('id',25*180,'25/1',scene_frames=[25*61])
    assert all(60<=s['duration_seconds']<=90 for s in p['segments'])


def test_pause_preferred_and_speech_avoided():
    m=api();p=m.plan_segments('id',25*150,'25/1',scene_frames=[25*72],
          pause_frames=[25*78],speech_intervals=[[25*70,25*77]])
    assert p['segments'][0]['end_frame']==25*78
    assert p['segments'][0]['boundary_kind']=='pause_candidate'
    assert not p['segments'][0]['cut_inside_speech']


def test_unavoidable_dialogue_cut_is_reported():
    p=api().plan_segments('id',25*150,'25/1',speech_intervals=[[1,25*150-1]])
    assert p['segments'][0]['cut_inside_speech']
    assert p['segments'][0]['review_required']


@pytest.mark.parametrize('kwargs',[
    {'min_seconds':float('nan')},{'max_seconds':0},{'target_seconds':100},
    {'context_seconds':-1},{'scene_frames':[True]},{'scene_frames':[-1]},
    {'pause_frames':[3751]},{'speech_intervals':[[20,10]]}])
def test_invalid_planning_options(kwargs):
    with pytest.raises(ValueError):api().plan_segments('id',3750,'25/1',**kwargs)


@pytest.mark.parametrize('id',['../escape','a\nffmpeg','',None])
def test_invalid_ids(id):
    with pytest.raises(ValueError):api().plan_segments(id,3750,'25/1')


@pytest.mark.parametrize('field,value',[
    ('duration_seconds',123),('end_seconds',123),('id','different'),
    ('context_end_frame',999999),('duration_exception',True),('start_frame',False)])
def test_reject_mutated_coverage_fields(field,value):
    m=api();p=m.plan_segments('id',3750,'25/1');p['segments'][0][field]=value
    with pytest.raises(ValueError):m.validate_coverage(p)


def test_many_total_lengths_have_exact_coverage():
    m=api()
    for total in range(1,1201):
        p=m.plan_segments('fixture',total,'1/1')
        assert m.validate_coverage(p)
        assert sum(s['end_frame']-s['start_frame'] for s in p['segments'])==total
        if (total+89)//90<=total//60:
            assert all(60<=s['duration_seconds']<=90 for s in p['segments'])


def test_assembly_rejects_changed_source(tmp_path):
    m=api();p=ready_plan(m,tmp_path)
    Path(p['source']['path']).write_bytes(b'changed')
    with pytest.raises(ValueError,match='hash'):m.assembly_inputs(p)


@pytest.mark.parametrize('field,value',[
    ('approved','true'),('technical_qa',1),('audiovisual_review',False),
    ('reviewer',' '),('plan_sha256','0'*64),('artifact_sha256','0'*64)])
def test_assembly_rejects_bad_approval(tmp_path,field,value):
    m=api();p=ready_plan(m,tmp_path);p['segments'][0]['approval'][field]=value
    with pytest.raises(ValueError):m.assembly_inputs(p)


@pytest.mark.parametrize('field,value',[
    ('frame_count',1874),('fps','24/1'),('duration_seconds',76),
    ('decode_errors',1),('audio_present',False),('av_sync_reviewed',False),
    ('passed','yes'),('plan_sha256','0'*64),('artifact_sha256','0'*64)])
def test_assembly_rejects_bad_qa(tmp_path,field,value):
    m=api();p=ready_plan(m,tmp_path);p['segments'][0]['technical_qa'][field]=value
    with pytest.raises(ValueError):m.assembly_inputs(p)


def test_assembly_rejects_unverified_timing(tmp_path):
    m=api();p=ready_plan(m,tmp_path);p['source']['timing_verified']=False
    with pytest.raises(ValueError):m.assembly_inputs(p)


def test_assembly_rejects_duplicate_outputs_and_stream_mismatch(tmp_path):
    m=api();p=ready_plan(m,tmp_path,150)
    p['segments'][1]['technical_qa']['stream_signature']['width']=256
    with pytest.raises(ValueError,match='stream'):m.assembly_inputs(p)
    p['segments'][1]['technical_qa']['stream_signature']['width']=128
    p['segments'][1]['edited']=copy.deepcopy(p['segments'][0]['edited'])
    with pytest.raises(ValueError):m.assembly_inputs(p)


def test_export_roundtrip_does_not_overwrite(tmp_path):
    m=api();p=m.plan_segments('fixture',3750,'25/1')
    folder=tmp_path/'new';m.export_plan(p,folder)
    assert json.loads((folder/'segments.json').read_text())==p
    assert (folder/'segments.csv').read_text().count('fixture-P')==2
    with pytest.raises(FileExistsError):m.export_plan(p,folder)


def test_many_speech_intervals_are_indexed():
    m=api()
    intervals=[[i*4,i*4+2] for i in range(1000)]
    p=m.plan_segments('fixture',5000,'25/1',speech_intervals=intervals)
    assert m.validate_coverage(p)
    assert all(isinstance(s['cut_inside_speech'],bool) for s in p['segments'])
