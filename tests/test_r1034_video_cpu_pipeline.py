"""Regressões do núcleo CPU; sem modelo remoto ou inferência em testes."""
import importlib.util
import json
import wave
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "integrations/video_cpu_pipeline.py"


@pytest.fixture
def api():
    assert MODULE.is_file(), "núcleo ainda não implementado"
    spec = importlib.util.spec_from_file_location("video_cpu_pipeline", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def speakers():
    return {"s1": {"consent_declared": True}, "s2": {"consent_declared": True}}


def test_consent_required(api):
    with pytest.raises(ValueError, match="consent"):
        api.validate_turns([{"speaker":"s1", "start":0, "end":1}], {"s1":{}}, 2)


def test_overlapping_speakers_are_preserved(api):
    turns=[{"speaker":"s1", "start":0, "end":2},{"speaker":"s2", "start":1, "end":3}]
    assert api.validate_turns(turns, speakers(), 3) == turns


@pytest.mark.parametrize("start,end", [(2,1),(-1,2),(0,float("nan")),(0,4)])
def test_bad_times_rejected(api,start,end):
    with pytest.raises(ValueError):
        api.validate_turns([{"speaker":"s1", "start":start, "end":end}],speakers(),3)


def test_unknown_speaker_rejected(api):
    with pytest.raises(ValueError,match="speaker"):
        api.validate_turns([{"speaker":"x", "start":0, "end":1}],speakers(),3)


def test_final_audio_binding(api,tmp_path,monkeypatch):
    monkeypatch.setattr(api,'audio_duration',lambda path:2.0)
    audio=tmp_path/'mix.wav';audio.write_bytes(b'original final mix')
    alignment={"language":"pt-BR","audio_sha256":api.sha256_file(audio),"duration":2,"words":[{"speaker":"s1","start":0.1,"end":0.7,"text":"Olá"}]}
    assert api.validate_alignment(alignment,audio,speakers())
    audio.write_bytes(b'modified mix')
    with pytest.raises(ValueError,match="hash"):
        api.validate_alignment(alignment,audio,speakers())


def test_caption_formats_and_speaker_separation(api):
    words=[{"speaker":"s1","start":0.1,"end":0.8,"text":"Olá <amigo>"},{"speaker":"s2","start":0.4,"end":1.0,"text":"Sim {voz}\\N"}]
    cues=api.make_cues(words)
    assert len(cues)==2 and cues[1]['start'] < cues[0]['end']
    out=api.render_subtitles(cues)
    assert set(out)=={'srt','vtt','ass'}
    assert '00:00:00,100 --> 00:00:00,800' in out['srt']
    assert out['vtt'].startswith('WEBVTT')
    assert '&lt;amigo&gt;' in out['vtt']
    assert '[Events]' in out['ass'] and 'Dialogue:' in out['ass']
    assert '{voz}' not in out['ass']


def test_caption_word_wrapping(api):
    words=[{"speaker":"s1","start":i*0.4,"end":i*0.4+0.3,"text":"palavra"} for i in range(30)]
    cues=api.make_cues(words,max_chars=20,max_lines=2)
    assert len(cues)>1
    assert sum(len(c['words']) for c in cues)==len(words)
    assert all(len(c['text'].splitlines())<=2 for c in cues)
    assert all(len(line)<=20 for c in cues for line in c['text'].splitlines())


def test_resume_checks_input_output_and_params(api,tmp_path):
    source=tmp_path/'in';source.write_text('x')
    output=tmp_path/'out';output.write_text('y')
    stamp=api.stage_receipt([source],[output],{'voice':'s1'},'test-v1')
    assert api.can_resume(stamp,[source],[output],{'voice':'s1'},'test-v1')
    assert not api.can_resume(stamp,[source],[output],{'voice':'s2'},'test-v1')
    output.write_text('corrupted')
    assert not api.can_resume(stamp,[source],[output],{'voice':'s1'},'test-v1')


def test_timeline_overlap_not_hold(api):
    timeline=api.scene_timeline([90,120,90],12)
    assert timeline['total_frames']==276
    assert [x['start'] for x in timeline['scenes']]==[0,78,186]
    with pytest.raises(ValueError):api.scene_timeline([10,10],12)


def test_motion_continuity(api):
    assert api.smooth_progress(0,30)==0
    assert api.smooth_progress(29,30)==1
    points=[api.smooth_progress(i,30) for i in range(30)]
    assert all(a<=b for a,b in zip(points,points[1:]))
    assert max(b-a for a,b in zip(points,points[1:]))<0.06


def test_same_speaker_overlap_is_not_silent(api):
    with pytest.raises(ValueError,match="overlap"):
        api.validate_turns([{'speaker':'s1','start':0,'end':2},{'speaker':'s1','start':1,'end':3}],speakers(),3)


@pytest.mark.parametrize('registry',[{'s1':None},{'s1':'yes'},{'s1':True}])
def test_invalid_registry_record(api,registry):
    with pytest.raises(ValueError):api.validate_turns([{'speaker':'s1','start':0,'end':1}],registry,2)


def test_alignment_type_and_real_duration(api,tmp_path,monkeypatch):
    audio=tmp_path/'x.wav';audio.write_bytes(b'x')
    with pytest.raises(ValueError):api.validate_alignment([],audio,speakers())
    monkeypatch.setattr(api,'audio_duration',lambda path:2.0)
    with pytest.raises(ValueError,match="duration"):
        api.validate_alignment({'language':'pt-BR','audio_sha256':api.sha256_file(audio),'duration':3,'words':[{'speaker':'s1','start':0,'end':1,'text':'Oi'}]},audio,speakers())


def test_reject_cue_lost_in_ass_rounding(api):
    with pytest.raises(ValueError,match='resolution'):
        api.render_subtitles([{'speaker':'s1','start':0.1001,'end':0.1002,'text':'Oi'}])


def test_caption_direct_input_cannot_add_blocks(api):
    out=api.render_subtitles([{'speaker':'s1','start':0,'end':1,'text':'Oi\r\n\r\nSTYLE\n--> {x}'}])
    assert '\r' not in out['ass']
    assert '\n\nSTYLE' not in out['vtt']
    assert '{x}' not in out['ass']


def test_write_new_does_not_follow_existing_symlink(api,tmp_path):
    target=tmp_path/'do-not-create';out=tmp_path/'link';out.symlink_to(target)
    with pytest.raises(FileExistsError):api._write_new(out,'no')
    assert not target.exists()


def test_bool_time_invalid(api):
    with pytest.raises(ValueError):api.validate_turns([{'speaker':'s1','start':False,'end':1}],speakers(),2)


def test_partial_model_is_rejected_before_import(api,tmp_path):
    model=tmp_path/'model';model.mkdir();(model/'model.bin').write_bytes(b'not a model')
    with pytest.raises(ValueError,match='config'):
        api.transcribe_cpu(tmp_path/'absent.wav',model,tmp_path/'result.json')


def test_caption_cli_with_real_wav_and_no_overwrite(api,tmp_path):
    audio=tmp_path/'fixture.wav'
    with wave.open(str(audio),'wb') as stream:
        stream.setparams((1,2,16000,0,'NONE','not compressed'))
        stream.writeframes(b'\0\0'*32000)
    alignment=tmp_path/'alignment.json';registry=tmp_path/'registry.json';out=tmp_path/'out'
    alignment.write_text(json.dumps({'language':'pt-BR','audio_sha256':api.sha256_file(audio),'duration':2,'words':[{'speaker':'s1','start':0.2,'end':1.5,'text':'Teste técnico'}]}))
    registry.write_text(json.dumps(speakers()))
    args=['captions','--alignment',str(alignment),'--audio',str(audio),'--speakers',str(registry),'--out',str(out)]
    api.main(args)
    assert (out/'captions.pt-BR.srt').is_file()
    assert (out/'captions.pt-BR.vtt').is_file()
    assert (out/'captions.pt-BR.ass').is_file()
    with pytest.raises(FileExistsError):api.main(args)


def test_resume_rejects_changed_input(api,tmp_path):
    source=tmp_path/'input';output=tmp_path/'output'
    source.write_bytes(b'a');output.write_bytes(b'b')
    receipt=api.stage_receipt([source],[output],{},'1')
    source.write_bytes(b'changed')
    assert not api.can_resume(receipt,[source],[output],{},'1')


@pytest.mark.parametrize('kwargs',[
    {'cpu_threads':0},{'cpu_threads':9},{'cpu_threads':True},
    {'beam_size':0},{'beam_size':6},{'beam_size':False}])
def test_transcribe_rejects_bad_runtime(api,tmp_path,kwargs):
    with pytest.raises(ValueError,match='threads|beam'):
        api.transcribe_cpu(tmp_path/'absent.wav',tmp_path/'model',tmp_path/'out.json',**kwargs)
