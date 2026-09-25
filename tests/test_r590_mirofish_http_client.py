"""
Testes R-976.20 — Cliente HTTP do backend MiroFish-Offline (SPEC-976).

Integração por COMPOSIÇÃO com o serviço externo AGPL-3.0 (fork MarceloClaro/
MiroFish em ~/projetos/MiroFish-Offline). NENHUM código do projeto AGPL é
copiado para o Core; o Core apenas:

1. Detecta o checkout externo (MIROFISH_OFFLINE_DIR).
2. Sobe o backend Flask externo na venv própria do repo (quando presente).
3. Invoca a API HTTP real (/health, /api/simulation/*, /api/report/*).

Anti-overclaim (R110): a simulação OASIS-full (create/prepare/start) depende
de LLM_API_KEY/ZEP_API_KEY e de camel-oasis (Python <3.12); este teste valida
o que é determinístico e real neste ambiente: healthcheck, listagens e
fail-closed. O motor local mirofish.social segue como caminho determinístico
principal (R-976.6/7).
"""
import os
import subprocess
import sys
import time
import unittest
from typing import Optional

BASE_URL = os.environ.get("MIROFISH_HTTP_URL", "http://127.0.0.1:5001")
SERVICE_DIR = os.environ.get(
    "MIROFISH_OFFLINE_DIR", os.path.expanduser("~/projetos/MiroFish-Offline-AGPL")
)
BAD_URL = os.environ.get("MIROFISH_HTTP_BAD_URL", "http://127.0.0.1:5999")

_server_proc: Optional[subprocess.Popen] = None


def _health_ok(url: str) -> bool:
    import urllib.request

    try:
        with urllib.request.urlopen(url + "/health", timeout=3) as r:
            body = r.read().decode("utf-8")
            return r.status == 200 and '"ok"' in body
    except Exception:
        return False


def _ensure_backend_up() -> bool:
    """Sobe o backend externo na venv própria do repo AGPL se possível."""
    global _server_proc
    if _health_ok(BASE_URL):
        return True
    venv_py = os.path.join(SERVICE_DIR, ".venv", "bin", "python")
    backend_dir = os.path.join(SERVICE_DIR, "backend")
    if not (os.path.isfile(venv_py) and os.path.isdir(backend_dir)):
        return False
    code = (
        "import sys; sys.path.insert(0, '.'); "
        "from app import create_app; "
        "create_app().run(host='127.0.0.1', port=5001, debug=False, threaded=True)"
    )
    log = open("/tmp/opencode/mirofish-test-backend.log", "a")
    _server_proc = subprocess.Popen(
        [venv_py, "-c", code],
        cwd=backend_dir,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    for _ in range(30):
        time.sleep(0.5)
        if _health_ok(BASE_URL):
            return True
    return False


def setUpModule():
    global BASE_URL
    BASE_URL = os.environ.get("MIROFISH_HTTP_URL", BASE_URL)
    if not _ensure_backend_up():
        print("WARN: backend externo não subiu; testes de servidor serão pulados.")


def tearDownModule():
    if _server_proc is not None:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=5)
        except Exception:
            _server_proc.kill()


SERVER_UP = _health_ok(BASE_URL)


class TestMiroFishHttpClientServer(unittest.TestCase):
    """Testes que exigem o servidor externo de pé."""

    @classmethod
    def setUpClass(cls):
        if not SERVER_UP:
            raise unittest.SkipTest("Servidor externo indisponível; pulando.")

    def test_01_driver_importable(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        self.assertTrue(callable(MiroFishOfflineDriver))

    def test_02_health_returns_ok(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        h = driver.health()
        self.assertIsInstance(h, dict)
        self.assertTrue(h["ok"], h)
        self.assertIn("status", h)
        self.assertEqual(h["status"], "ok")

    def test_03_list_simulations_returns_list(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        sims = driver.list_simulations()
        self.assertIsInstance(sims, list)
        for s in sims:
            self.assertIsInstance(s, dict)

    def test_04_list_reports_returns_list(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        reps = driver.list_reports()
        self.assertIsInstance(reps, list)

    def test_05_list_projects_returns_list(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        projs = driver.list_projects()
        self.assertIsInstance(projs, list)

    def test_06_check_includes_http_status(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        c = driver.check()
        self.assertTrue(c["ok"], c)
        self.assertTrue(c["http_ok"], c)
        self.assertIsInstance(c["http_simulations_count"], int)
        self.assertIsInstance(c["http_health"], dict)

    def test_07_prepare_with_http_evidence(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        p = driver.prepare("doc teste", n_agents=5, seed=7)
        self.assertIsInstance(p, dict)
        self.assertTrue(p["prepared"], p)
        self.assertIn("http", p)
        self.assertTrue(p["http"]["ok"], p)

    def test_08_detect_service_still_finds_external_repo(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        st = driver.status
        self.assertTrue(st.available, st)
        self.assertIn("backend", str(st.backend_entry))


class TestMiroFishHttpFailClosed(unittest.TestCase):
    """Fail-closed R-976.9: serviço indisponível nunca falha silenciosamente."""

    def test_10_health_ok_false_never_raises(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BAD_URL)
        h = driver.health()
        self.assertIsInstance(h, dict)
        self.assertFalse(h["ok"], h)
        self.assertIn("reason", h)

    def test_11_list_raises_when_server_down(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BAD_URL)
        with self.assertRaises(RuntimeError):
            driver.list_simulations()

    def test_12_prepare_raises_when_server_down(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BAD_URL)
        with self.assertRaises(RuntimeError):
            driver.prepare("doc", n_agents=3, seed=1)

    def test_13_no_service_dir_raises(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(
            service_dir="/tmp/nao-existe-mirofish", base_url=BASE_URL
        )
        h = driver.health()
        self.assertFalse(h["ok"], h)
        with self.assertRaises(RuntimeError):
            driver.prepare("doc", n_agents=3, seed=1)


class TestMiroFishHttpErrors(unittest.TestCase):
    """Erros HTTP mapeados para exceções claras."""

    @classmethod
    def setUpClass(cls):
        if not SERVER_UP:
            raise unittest.SkipTest("Servidor externo indisponível; pulando.")

    def test_20_get_missing_simulation_raises(self):
        from integrations.mirofish_offline import MiroFishOfflineDriver

        driver = MiroFishOfflineDriver(service_dir=SERVICE_DIR, base_url=BASE_URL)
        with self.assertRaises(RuntimeError):
            driver.get_simulation("sim_nao_existe_999")


if __name__ == "__main__":
    unittest.main(verbosity=2)