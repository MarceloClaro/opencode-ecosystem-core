"""Banca persistente: pergunta, resposta real e réplica; sem notas inventadas."""
from contextlib import contextmanager
import copy,fcntl,hashlib,json,os,re,tempfile,uuid,math
from pathlib import Path
from .evidence import read_artifact,text

class BancaSessionStore:
    def __init__(self,root):
        self.root=Path(root)

    def _path(self,sid):
        if not isinstance(sid,str) or not re.fullmatch(r'banca-[a-f0-9]{32}',sid): raise ValueError('Sessão inválida')
        path=self.root/(sid+'.json')
        if path.is_symlink(): raise ValueError('Sessão simbólica recusada')
        return path

    @contextmanager
    def _locked(self):
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        with (self.root/'.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try: yield
            finally: fcntl.flock(lock,fcntl.LOCK_UN)

    def _save(self,state):
        payload=json.dumps(state,ensure_ascii=False,sort_keys=True,allow_nan=False)
        envelope={'state':state,'sha256':hashlib.sha256(payload.encode()).hexdigest()}
        fd,temporary=tempfile.mkstemp(dir=self.root,prefix='.banca-',suffix='.tmp')
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                json.dump(envelope,stream,ensure_ascii=False,sort_keys=True,allow_nan=False)
                stream.flush();os.fsync(stream.fileno())
            os.replace(temporary,self._path(state['session_id']))
        finally:
            if Path(temporary).exists(): Path(temporary).unlink()

    def _load(self,sid):
        path=self._path(sid)
        if path.stat().st_size>8*1024*1024: raise ValueError('Sessão excessiva')
        envelope=json.loads(path.read_text())
        state=envelope['state']
        payload=json.dumps(state,ensure_ascii=False,sort_keys=True,allow_nan=False)
        if hashlib.sha256(payload.encode()).hexdigest()!=envelope['sha256'] or state['session_id']!=sid: raise ValueError('Sessão corrompida')
        return state

    def start(self,review,rubric=None):
        if not isinstance(review,dict) or not review.get('question_families'): raise ValueError('Revisão com questões obrigatória')
        if not self._fresh(review): raise ValueError('Artefato alterado; execute nova revisão')
        if rubric is not None:
            if not isinstance(rubric,dict) or not isinstance(rubric.get('criteria'),list) or not rubric['criteria']: raise ValueError('Rubrica inválida')
            source=read_artifact(rubric.get('source_path'))
            text(rubric.get('locator'),'localizador da rubrica',1000)
            if source['sha256']!=rubric.get('source_sha256'): raise ValueError('Hash da rubrica divergente')
            ids=set()
            for criterion in rubric['criteria']:
                cid=text(criterion.get('criterion_id'),'critério',100)
                if cid in ids: raise ValueError('Critério duplicado')
                ids.add(cid)
                maximum=criterion.get('maximum')
                if type(maximum) not in (int,float) or not math.isfinite(maximum) or not 0<maximum<=100: raise ValueError('Máximo da rubrica inválido')
            rubric={**copy.deepcopy(rubric),'verification_scope':'local_document_integrity_only','institutional_authenticity_verified':False}
        state={'session_id':'banca-'+uuid.uuid4().hex,'review':copy.deepcopy(review),'rubric':rubric,'index':0,'turn_kind':'central','answers':[],'ratings':[],'status':'waiting_for_answer'}
        with self._locked(): self._save(state)
        return self._view(state)

    @staticmethod
    def _fresh(review):
        try: return read_artifact(review['artifact']['path'])['sha256']==review['artifact']['sha256']
        except (OSError,ValueError): return False

    def _view(self,state):
        families=state['review']['question_families']; index=state['index']
        questions=[]
        if state['status']=='waiting_for_answer' and index<len(families):
            family=families[index]
            question=family['question']
            if state['turn_kind']=='replica':
                answer=state['answers'][-1]['answer']
                question='Na resposta recebida, você afirmou: “'+answer[:220]+'”. '+family['replica']
            questions=[question]
        turn=hashlib.sha256(f"{state['session_id']}:{index}:{state['turn_kind']}".encode()).hexdigest()[:24]
        return {'session_id':state['session_id'],'status':state['status'],'turn_id':turn,'turn_kind':state['turn_kind'],'questions':questions,'answered_turns':len(state['answers']),'llm_inference_executed':False,'external_validation':False}

    def question(self,sid):
        with self._locked():
            state=self._load(sid)
            artifact=state['review']['artifact']
            if read_artifact(artifact['path'])['sha256']!=artifact['sha256']:
                return {'session_id':sid,'status':'stale_artifact','questions':[],'reason':'O artefato mudou; execute nova revisão antes de continuar.'}
            return self._view(state)

    def answer(self,sid,answer,turn_id=None):
        answer=text(answer,'resposta',12000)
        with self._locked():
            state=self._load(sid)
            if state['status']!='waiting_for_answer': raise ValueError('Sessão não aguarda resposta')
            current=self._view(state)
            if turn_id is not None and turn_id!=current['turn_id']: raise ValueError('Resposta de outro turno ou repetida')
            artifact=state['review']['artifact']
            if read_artifact(artifact['path'])['sha256']!=artifact['sha256']: raise ValueError('Artefato alterado; nova revisão necessária')
            state['answers'].append({'turn_id':current['turn_id'],'family':state['review']['question_families'][state['index']]['family'],'turn_kind':state['turn_kind'],'answer':answer,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest()})
            if state['turn_kind']=='central': state['turn_kind']='replica'
            else:
                state['index']+=1;state['turn_kind']='central'
                if state['index']>=len(state['review']['question_families']): state['status']='answered_pending_human_review'
            self._save(state)
            return self._view(state)

    def cancel(self,sid):
        with self._locked():
            state=self._load(sid);state['status']='cancelled';self._save(state);return self._view(state)

    def rate(self,sid,criterion_id,score,answer_turn_ids,justification,reviewer_id):
        """Registra julgamento declarado; não autentica avaliador nem instituição."""
        from .scoring import observed_rating
        with self._locked():
            state=self._load(sid)
            if not self._fresh(state['review']): raise ValueError('Artefato alterado')
            if state['status']=='cancelled': raise ValueError('Sessão cancelada')
            rating=observed_rating(state,criterion_id,score,answer_turn_ids,justification,reviewer_id)
            state['ratings']=[r for r in state['ratings'] if r['dimension']!=criterion_id]+[rating]
            self._save(state)
        return self.finish(sid)

    def finish(self,sid):
        with self._locked():
            state=self._load(sid)
            stale=not self._fresh(state['review'])
            stale_rubric=False
            if state['rubric']:
                try: stale_rubric=read_artifact(state['rubric']['source_path'])['sha256']!=state['rubric']['source_sha256']
                except (OSError,ValueError): stale_rubric=True
            answered={a['family'] for a in state['answers'] if a['turn_kind']=='replica'}
            scores=[]
            criteria=state['rubric']['criteria'] if state['rubric'] else [{'criterion_id':q['family'],'maximum':None} for q in state['review']['question_families']]
            for criterion in criteria:
                rating=next((r for r in state['ratings'] if r['dimension']==criterion['criterion_id']),None)
                scores.append(rating or {'dimension':criterion['criterion_id'],'score':None,'maximum':criterion['maximum'],'status':'unobserved' if not state['answers'] else 'not_scored','reason':'Não há julgamento documentado deste critério; resposta registrada não autoriza nota automática.'})
            return {'session_id':sid,'status':'stale_artifact' if stale else ('stale_rubric' if stale_rubric else state['status']),'answers':state['answers'],'scores':scores,'scores_current':not stale and not stale_rubric,'unanswered_objections':[q['family'] for q in state['review']['question_families'] if q['family'] not in answered],'unresolved_critical_objections':[x['objection_id'] for x in state['review']['objections'] if x['severity']=='critical'],'approved':False,'human_review_required':True,'rubric':state['rubric'],'external_validation':False,'limitations':['Respostas não encerram automaticamente objeções científicas.','Notas são julgamentos declarados de treinamento, sem autenticação do avaliador ou validade institucional.']}
