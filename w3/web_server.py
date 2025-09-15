from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os
import socket

# 상수 정의
HOST = "0.0.0.0"
PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


def format_log(client_ip, path):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"[ACCESS] time={now} ip={client_ip} path={path}"


class SimpleHandler(BaseHTTPRequestHandler):
    def log_message(self, format_, *args):  # suppress default noisy log or customize
        pass  # 우리는 직접 포맷된 로그를 출력하므로 기본은 무시

    def do_GET(self):  # noqa: N802 (PEP8 naming override from base class)
        client_ip = self.client_address[0]
        path = self.path
        # index 또는 루트만 지원 (단순 요구사항에 맞춤). 그 외는 404 반환
        if path in ("/", "/index.html"):
            if os.path.exists(INDEX_FILE):
                try:
                    with open(INDEX_FILE, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except OSError:
                    self.send_error(500, "Internal Server Error")
            else:
                self.send_error(500, "index.html not found")
        else:
            self.send_error(404, "Not Found")
        print(format_log(client_ip, path))


def run_server(host=HOST, port=PORT):
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Starting HTTP server on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
