from fastapi.testclient import TestClient
from educ_system.app import app

client = TestClient(app)

def test_login_sucesso():
    response = client.post("/api/auth/login", json={"cpf": "77903790544", "senha": "123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["usuario"] == "Diretor(a) Gestor(a)"

def test_login_falha():
    response = client.post("/api/auth/login", json={"cpf": "00000000000", "senha": "errada"})
    assert response.status_code == 401

def test_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_alunos" in data
    assert "total_turmas" in data
    assert "media_geral" in data

def test_turmas():
    response = client.get("/api/turmas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_airam_pei():
    response = client.post("/api/airam/pei", json={
        "aluno_id": 101,
        "necessidade": "TEA",
        "adaptacoes_curriculares": "Atividades visuais",
        "objetivos_trimestrais": "Socialização"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "sucesso"

def test_airam_paee():
    response = client.post("/api/airam/paee", json={
        "aluno_id": 101,
        "recursos_tecnologia_assistiva": "Leitor de tela",
        "atendimento_contra_turno": "Segundas"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "sucesso"

def test_airam_plano_aula():
    response = client.post("/api/airam/plano-aula", json={
        "disciplina": "Matemática",
        "tema": "Funções",
        "habilidade_bncc": "EM13MAT401",
        "metodologia": "Ativa"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "sucesso"

def test_airam_juridico():
    response = client.post("/api/airam/juridico", json={
        "tipo": "Parecer Pedagógico",
        "descricao": "Regularização de vida escolar"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "sucesso"
