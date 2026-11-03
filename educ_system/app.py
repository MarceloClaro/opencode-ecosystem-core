from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="Sistema Educacional Simulado - AiramVeras & Diretoria Escolar", version="2.0.0")

security = HTTPBearer()

# Base de dados em memória simulada
DB = {
    "diretor": {"cpf": "77903790544", "senha": "123", "nome": "Diretor(a) Gestor(a)", "escola": "EEFM Prof. Simulado"},
    "turmas": [
        {"id": 1, "nome": "1º Ano A - Ensino Médio", "turno": "Manhã", "alunos_count": 35, "frequencia_media": 91.5},
        {"id": 2, "nome": "2º Ano B - Ensino Médio", "turno": "Tarde", "alunos_count": 32, "frequencia_media": 88.0},
        {"id": 3, "nome": "3º Ano A - Ensino Médio", "turno": "Manhã", "alunos_count": 30, "frequencia_media": 94.2},
    ],
    "alunos": [
        {"id": 101, "turma_id": 1, "nome": "Ana Clara Souza", "frequencia": 95.0, "media": 8.5, "status": "Regular"},
        {"id": 102, "turma_id": 1, "nome": "Bruno Silva Santos", "frequencia": 72.0, "media": 5.4, "status": "Alerta Frequência"},
        {"id": 103, "turma_id": 2, "nome": "Carlos Eduardo Lima", "frequencia": 89.0, "media": 7.2, "status": "Regular"},
        {"id": 104, "turma_id": 3, "nome": "Daniela Costa", "frequencia": 98.0, "media": 9.3, "status": "Destaque"},
    ],
    "frequencia_diaria": [],
    "notas_lancadas": [],
    "pei_registros": [],
    "paee_registros": [],
    "planos_aula": [],
    "pareceres_juridicos": []
}

class LoginRequest(BaseModel):
    cpf: str
    senha: str

class FrequenciaModel(BaseModel):
    aluno_id: int
    data: str
    presente: bool

class NotaModel(BaseModel):
    aluno_id: int
    disciplina: str
    nota: float
    unidade: str

class PEIModel(BaseModel):
    aluno_id: int
    necessidade: str
    adaptacoes_curriculares: str
    objetivos_trimestrais: str

class PAEEModel(BaseModel):
    aluno_id: int
    recursos_tecnologia_assistiva: str
    atendimento_contra_turno: str

class PlanoAulaModel(BaseModel):
    disciplina: str
    tema: str
    habilidade_bncc: str
    metodologia: str

class JuridicoModel(BaseModel):
    tipo: str # "Parecer", "Termo de Adaptação", "Prestação de Contas"
    descricao: str

@app.post("/api/auth/login")
def login(creds: LoginRequest):
    if creds.cpf == DB["diretor"]["cpf"] and creds.senha in ["123", "123456"]:
        return {
            "access_token": "token-simulado-educacional-999",
            "token_type": "bearer",
            "usuario": DB["diretor"]["nome"],
            "escola": DB["diretor"]["escola"]
        }
    raise HTTPException(status_code=401, detail="CPF ou senha inválidos.")

@app.get("/api/dashboard")
def get_dashboard():
    total_alunos = len(DB["alunos"])
    total_turmas = len(DB["turmas"])
    media_geral = sum(a["media"] for a in DB["alunos"]) / total_alunos if total_alunos > 0 else 0
    frequencia_geral = sum(a["frequencia"] for a in DB["alunos"]) / total_alunos if total_alunos > 0 else 0
    alertas = [a for a in DB["alunos"] if a["status"] == "Alerta Frequência" or a["media"] < 6.0]
    
    return {
        "total_alunos": total_alunos,
        "total_turmas": total_turmas,
        "media_geral": round(media_geral, 2),
        "frequencia_geral": round(frequencia_geral, 2),
        "total_alertas": len(alertas),
        "alertas": alertas
    }

@app.get("/api/turmas")
def get_turmas():
    return DB["turmas"]

@app.get("/api/alunos")
def get_alunos(turma_id: Optional[int] = None):
    if turma_id:
        return [a for a in DB["alunos"] if a["turma_id"] == turma_id]
    return DB["alunos"]

@app.post("/api/frequencia")
def registrar_frequencia(freq: FrequenciaModel):
    DB["frequencia_diaria"].append(freq.model_dump() if hasattr(freq, 'model_dump') else freq.dict())
    return {"status": "sucesso", "mensagem": "Frequência registrada com sucesso."}

@app.post("/api/notas")
def lancar_nota(nota: NotaModel):
    DB["notas_lancadas"].append(nota.model_dump() if hasattr(nota, 'model_dump') else nota.dict())
    for a in DB["alunos"]:
        if a["id"] == nota.aluno_id:
            a["media"] = round((a["media"] + nota.nota) / 2, 2)
    return {"status": "sucesso", "mensagem": "Nota lançada com sucesso."}

@app.get("/api/relatorios")
def get_relatorios():
    aprovados = len([a for a in DB["alunos"] if a["media"] >= 6.0 and a["frequencia"] >= 75.0])
    em_risco = len([a for a in DB["alunos"] if a["media"] < 6.0 or a["frequencia"] < 75.0])
    return {
        "total_avaliados": len(DB["alunos"]),
        "aprovados_estimados": aprovados,
        "em_risco": em_risco,
        "taxa_aprovacao_projetada": f"{(aprovados / len(DB['alunos'])) * 100:.1f}%" if DB["alunos"] else "0%"
    }

# --- AiramVeras Endpoints (PEI, PAEE, Planos de Aula, Jurídico/Pedagógico) ---
@app.post("/api/airam/pei")
def criar_pei(pei: PEIModel):
    reg = pei.model_dump() if hasattr(pei, 'model_dump') else pei.dict()
    DB["pei_registros"].append(reg)
    return {"status": "sucesso", "mensagem": "Plano Educacional Individualizado (PEI) gerado e salvo com sucesso.", "pei": reg}

@app.get("/api/airam/pei")
def listar_pei():
    return DB["pei_registros"]

@app.post("/api/airam/paee")
def criar_paee(paee: PAEEModel):
    reg = paee.model_dump() if hasattr(paee, 'model_dump') else paee.dict()
    DB["paee_registros"].append(reg)
    return {"status": "sucesso", "mensagem": "Plano de Atendimento Educacional Especializado (PAEE) gerado com sucesso.", "paee": reg}

@app.get("/api/airam/paee")
def listar_paee():
    return DB["paee_registros"]

@app.post("/api/airam/plano-aula")
def criar_plano_aula(plano: PlanoAulaModel):
    reg = plano.model_dump() if hasattr(plano, 'model_dump') else plano.dict()
    DB["planos_aula"].append(reg)
    return {"status": "sucesso", "mensagem": "Plano de Aula alinhado à BNCC gerado com sucesso por IA.", "plano": reg}

@app.get("/api/airam/plano-aula")
def listar_planos_aula():
    return DB["planos_aula"]

@app.post("/api/airam/juridico")
def criar_juridico(jur: JuridicoModel):
    reg = jur.model_dump() if hasattr(jur, 'model_dump') else jur.dict()
    DB["pareceres_juridicos"].append(reg)
    return {"status": "sucesso", "mensagem": "Parecer ou documento jurídico-pedagógico emitido com sucesso.", "documento": reg}

@app.get("/api/airam/juridico")
def listar_juridico():
    return DB["pareceres_juridicos"]

# Servir Frontend estático se existir
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
