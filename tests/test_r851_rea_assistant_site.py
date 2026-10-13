"""Contrato R851: site de instruções loopback, sem acesso ao repositório.

HTTP real e script real; o adaptador de DOM em Node testa a interação de cópia,
mas não substitui inspeção visual do navegador.
"""
from __future__ import annotations

from contextlib import contextmanager
from html.parser import HTMLParser
import http.client
import json
import subprocess
import threading


@contextmanager
def site_em_execucao():
    from webapp.rea_assistant_site import make_server

    server = make_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def requisitar(server, path="/", method="GET", headers=None, hosts=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        if hosts is None:
            connection.request(method, path, headers=headers or {})
        else:
            connection.putrequest(method, path, skip_host=True)
            for host in hosts:
                connection.putheader("Host", host)
            for key, value in (headers or {}).items():
                connection.putheader(key, value)
            connection.endheaders()
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def test_loopback_e_recursos_publicos():
    # Detecta bind em todas as interfaces e recursos públicos inacessíveis.
    with site_em_execucao() as server:
        assert server.server_address[0] == "127.0.0.1"
        for path, media in [("/", "text/html"), ("/index.html", "text/html"),
                            ("/styles.css", "text/css"), ("/script.js", "text/javascript"),
                            ("/favicon.svg", "image/svg+xml")]:
            status, headers, body = requisitar(server, path)
            assert status == 200, path
            assert headers["Content-Type"].startswith(media), path
            assert int(headers["Content-Length"]) == len(body) > 0


def test_host_externo_duplicado_ou_ausente_e_recusado():
    # Detecta DNS rebinding e interpretação permissiva de Host duplicado.
    with site_em_execucao() as server:
        valid = f"127.0.0.1:{server.server_port}"
        for hosts in [["example.org"], ["127.0.0.1:1"], ["127.0.0.1.example.org"],
                      ["user@127.0.0.1"], [valid, "example.org"], [], [valid, valid]]:
            assert requisitar(server, hosts=hosts)[0] == 403, hosts
        assert requisitar(server, hosts=[f"localhost:{server.server_port}"])[0] == 200


def test_origin_externo_e_recusado():
    # Detecta acesso originado por página externa mesmo com Host local válido.
    with site_em_execucao() as server:
        for origin in ["https://example.org", "null", "http://127.0.0.1:1",
                       f"https://127.0.0.1:{server.server_port}"]:
            assert requisitar(server, headers={"Origin": origin})[0] == 403
        for local in ["127.0.0.1", "localhost"]:
            assert requisitar(server, headers={"Origin": f"http://{local}:{server.server_port}"})[0] == 200


def test_caminhos_do_repositorio_nao_sao_expostos():
    # Detecta troca por servidor de diretório ou rota de análise HTTP.
    with site_em_execucao() as server:
        for path in ["/AGENTS.md", "/.env", "/.git/config", "/docs/ASSISTENTE_REA_LOCAL.md",
                     "/rea/inspect", "/api/inspect", "/webapp/", "/missing.css"]:
            status, _, body = requisitar(server, path)
            assert status == 404, path
            assert b"directory listing" not in body.lower()


def test_traversal_e_caminho_nao_canonico_sao_recusados():
    # Detecta normalização de traversal antes da allowlist.
    with site_em_execucao() as server:
        for path in ["/../AGENTS.md", "/%2e%2e/AGENTS.md", "/%252e%252e/AGENTS.md",
                     "/%2fstyles.css", "//styles.css", "/styles.css?path=../.env",
                     "/styles.css#x", "/foo/../index.html", "/%00", "/%5cindex.html"]:
            assert requisitar(server, path)[0] == 400, path


def test_metodos_que_podem_enviar_dados_sao_recusados():
    # Detecta adição inadvertida de rotas HTTP mutáveis ou HEAD fora do contrato.
    with site_em_execucao() as server:
        for method in ["POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "CONNECT"]:
            assert requisitar(server, method=method)[0] == 405, method


def test_politica_do_navegador_bloqueia_conexoes_e_enquadramento():
    # Detecta permissões de conexão/recurso externo e remoção de isolamento de origem.
    with site_em_execucao() as server:
        status, headers, _ = requisitar(server)
        assert status == 200
        directives = {part.split()[0]: part.split()[1:]
                      for part in headers["Content-Security-Policy"].split(";") if part.strip()}
        assert directives["default-src"] == ["'none'"]
        assert directives["connect-src"] == ["'none'"]
        assert directives["form-action"] == ["'none'"]
        assert directives["frame-ancestors"] == ["'none'"]
        assert directives["script-src"] == ["'self'"]
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Cross-Origin-Resource-Policy"] == "same-origin"
        assert headers["Referrer-Policy"] == "no-referrer"


class RecursosDaPagina(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.buttons, self.ids = [], [], set()
        self.lang = None
        self.viewport = False
        self.live = False
        self.forms = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if tag in {"script", "img", "iframe", "link"}:
            self.refs.append(attrs.get("src") or attrs.get("href"))
        if tag == "button" and "data-copy-target" in attrs:
            self.buttons.append(attrs["data-copy-target"])
        if attrs.get("id") == "copy-status":
            self.live = attrs.get("role") == "status" and attrs.get("aria-live") == "polite"
        self.forms = self.forms or tag == "form"


def test_pagina_tem_recursos_locais_e_comandos_associados():
    # Detecta referências externas, botão sem comando ou feedback inacessível.
    with site_em_execucao() as server:
        status, _, body = requisitar(server)
        assert status == 200
        page = RecursosDaPagina()
        page.feed(body.decode("utf-8"))
        assert page.lang == "pt-BR" and page.viewport
        assert page.refs and all(ref in {"/styles.css", "/script.js", "/favicon.svg"} for ref in page.refs)
        assert len(page.buttons) >= 4 and set(page.buttons) <= page.ids
        assert page.live and not page.forms


NODE_CLIENT = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = {copied: [], status: ''};
let click;
const button = {dataset: {copyTarget: 'command'}, textContent: 'Copiar',
  addEventListener(type, fn) {if (type === 'click') click = fn;}};
const code = {textContent: '  python -m marceloclaro.cli rea setup  '};
const feedback = {set textContent(value) {result.status = value;}};
let selection;
const document = {
  querySelectorAll() {return [button];},
  getElementById(id) {return id === 'command' ? code : feedback;},
  createElement() {return {style: {}, setAttribute() {}, select() {selection = this.value;}, remove() {}};},
  body: {appendChild() {}},
  execCommand(name) {if (name !== 'copy') throw Error('bad command'); result.copied.push(selection); return true;}
};
const navigator = payload.mode === 'fallback' ? {} : {clipboard: {
  async writeText(text) {if (payload.mode === 'failure') throw Error('permission denied'); result.copied.push(text);}
}};
vm.runInNewContext(payload.script, {document, navigator, window: {isSecureContext: true}, setTimeout() {}});
(async () => {await click(); process.stdout.write(JSON.stringify(result));})().catch(error => {
  process.stderr.write(String(error)); process.exitCode = 1;
});
"""


def executar_cliente(server, mode):
    status, _, body = requisitar(server, "/script.js")
    assert status == 200
    run = subprocess.run(["node", "-e", NODE_CLIENT], input=json.dumps({"script": body.decode("utf-8"), "mode": mode}),
                         text=True, capture_output=True, timeout=5)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def test_copia_comando_e_informa_sucesso_no_cliente():
    # Detecta cópia vazia, sem trim ou ausência de feedback para a pessoa.
    with site_em_execucao() as server:
        result = executar_cliente(server, "success")
        assert result["copied"] == ["python -m marceloclaro.cli rea setup"]
        assert "copiado" in result["status"].lower()


def test_falha_de_copia_informa_como_prosseguir():
    # Detecta rejeição silenciosa da Clipboard API.
    with site_em_execucao() as server:
        result = executar_cliente(server, "failure")
        assert result["copied"] == []
        assert "selecione" in result["status"].lower()


def test_copia_alternativa_sem_clipboard_api():
    # Detecta falta de cópia local em navegador sem Clipboard API.
    with site_em_execucao() as server:
        result = executar_cliente(server, "fallback")
        assert result["copied"] == ["python -m marceloclaro.cli rea setup"]
        assert "copiado" in result["status"].lower()
