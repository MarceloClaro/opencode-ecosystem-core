import subprocess
import time
import sys
import os
import socket
import atexit

def install_dependencies():
    try:
        import webview
    except ImportError:
        print("Biblioteca 'pywebview' não encontrada. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
            print("Biblioteca 'pywebview' instalada com sucesso!")
        except Exception as e:
            print(f"Erro ao tentar instalar 'pywebview': {e}")
            print("Por favor, instale manualmente executando: pip install pywebview")
            sys.exit(1)

install_dependencies()
import webview

def is_port_open(port=8501):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except Exception:
        return False

# 1. Iniciar o servidor do Streamlit se não estiver ativo
server_proc = None
if not is_port_open(8501):
    print("Iniciando o servidor do Gêmeo Digital em background...")
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")
    
    # Roda streamlit com --server.headless=true para não abrir o browser padrão
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Aguarda o servidor iniciar
    print("Aguardando inicialização do servidor...")
    for _ in range(20):
        if is_port_open(8501):
            print("Servidor iniciado com sucesso!")
            break
        time.sleep(1)
else:
    print("Servidor do Gêmeo Digital já está ativo na porta 8501.")

# 2. Registrar a limpeza do processo na saída do programa
def cleanup():
    if server_proc:
        print("Finalizando o servidor de background...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("Servidor finalizado.")

atexit.register(cleanup)

# 3. Criar a janela nativa do Desktop (Webview2)
print("Abrindo o Gêmeo Digital Periodontal em uma janela nativa...")
webview.create_window(
    title='🦷 Gêmeo Digital Periodontal 3D - SUS-Twin Framework',
    url='http://localhost:8501',
    width=1280,
    height=800,
    resizable=True
)

webview.start()
