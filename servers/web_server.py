import http.server
import socketserver
import threading
import os
import json
import psutil
from threading import Thread
from servers.ftp_server import ftp_credentials
from livereload import Server as LiveReloadServer
from rich.console import Console

try:
    from tornado.ioloop import IOLoop
except Exception:
    IOLoop = None

console = Console()


class WebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="servers/web_files", **kwargs)

    def do_GET(self):
        if self.path in ["/", "", "/index", "/index.html"]:
            self.path = "/index.html"

        if self.path == "/api/stats":
            stats = {
                "cpu": round(psutil.cpu_percent(), 2),
                "ram": round(psutil.virtual_memory().used / (1024 * 1024), 2),  # MB
                "ftp_user": ftp_credentials["user"],
                "ftp_pass": ftp_credentials["password"] if ftp_credentials["password"] else "No password (anonymous)",
                "web_port": self.server.server_address[1],
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        return super().do_GET()


class WebServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.httpd = None
        self.http_thread = None
        self.lr_thread = None
        self.livereload = None
        self.running = False

    def start(self):
        if self.running:
            return

        self.httpd = socketserver.ThreadingTCPServer((self.host, self.port), WebHandler)
        self.http_thread = Thread(target=self.httpd.serve_forever, daemon=True)
        self.http_thread.start()

        self.livereload = LiveReloadServer()
        self.livereload.watch("servers/web_files/**/*.html")
        self.livereload.watch("servers/web_files/**/*.css", delay=0.2)
        self.livereload.watch("servers/web_files/**/*.js", delay=0.2)

        def run_lr():
            self.livereload.serve(port=self.port + 1)

        self.lr_thread = Thread(target=run_lr, daemon=True)
        self.lr_thread.start()

        self.running = True
        console.print(f"[green]🌍 Web server running at http://{self.host}:{self.port}[/green]")

    def stop(self):
        if not self.running:
            return
        self.running = False

        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None

        if self.http_thread and self.http_thread.is_alive():
            self.http_thread.join(timeout=2)

        if IOLoop is not None:
            try:
                IOLoop.instance().add_callback(IOLoop.instance().stop)
            except Exception:
                pass

        if self.livereload:
            try:
                self.livereload.watcher._tasks.clear()
            except Exception:
                pass
            self.livereload = None

        if self.lr_thread and self.lr_thread.is_alive():
            self.lr_thread.join(timeout=2)

        console.print("[yellow]🛑 Web server stopped[/yellow]")
