from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time


HOST = "127.0.0.1"
PORT = 8765


class BenchmarkHandler(BaseHTTPRequestHandler):
    def _enviar_json(self, status, dados):
        corpo = json.dumps(dados).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

        self.wfile.write(corpo)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/benchmark":
            self._enviar_json(404, {"erro": "rota nao encontrada"})
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = self.rfile.read(tamanho)

            dados = json.loads(corpo.decode("utf-8"))

            recebido_ns = time.perf_counter_ns()

            resposta = {
                "ok": True,
                "id": dados.get("id"),
                "acao": dados.get("acao"),
                "origem": dados.get("origem"),
                "servidor_recebido_ns": recebido_ns,
                "servidor_enviado_ns": time.perf_counter_ns(),
            }

            self._enviar_json(200, resposta)

        except Exception as erro:
            self._enviar_json(
                500,
                {
                    "ok": False,
                    "erro": str(erro),
                },
            )

    def log_message(self, formato, *args):
        return


if __name__ == "__main__":
    servidor = ThreadingHTTPServer((HOST, PORT), BenchmarkHandler)

    print(
        f"Benchmark Online V1 ativo em http://{HOST}:{PORT}",
        flush=True,
    )
    print("Pressione Ctrl+C para encerrar.", flush=True)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        print("Servidor encerrado.", flush=True)
