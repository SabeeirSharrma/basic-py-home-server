import http.server
import socketserver
import os
import json
import psutil
from threading import Thread
from http import cookies
from urllib.parse import parse_qs
from servers.ftp_server import ftp_credentials
from livereload import Server as LiveReloadServer
from rich.console import Console

# Tornado is used under the hood by livereload
try:
    from tornado.ioloop import IOLoop
except Exception:
    IOLoop = None

console = Console()


def load_credentials():
    """Load valid credentials from login.txt. Lines starting with // are ignored.
       Each non-empty 'user:pass' line is a valid credential pair."""
    creds = []
    login_file = "servers/web_files/login.txt"
    if os.path.exists(login_file):
        with open(login_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                if ":" in line:
                    user, pwd = line.split(":", 1)
                    creds.append((user.strip(), pwd.strip()))
    return creds


class WebHandler(http.server.SimpleHTTPRequestHandler):
    credentials = load_credentials()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="servers/web_files", **kwargs)

    # ------------------- GET -------------------
    def do_GET(self):
        if self.path == "/api/stats":
            stats = {
                "cpu": round(psutil.cpu_percent(), 2),
                "ram": round(psutil.virtual_memory().used / (1024 * 1024), 2),  # MB
                "download": "N/A",
                "upload": "N/A",
                "ftp_user": ftp_credentials["user"],
                "ftp_pass": ftp_credentials["password"] if ftp_credentials["password"] else "No password (anonymous)",
                "web_port": self.server.server_address[1],
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        if self.path.endswith(".html"):
            self.path = self.path[:-5]
        if self.path in ["/", ""]:
            if not self.is_logged_in():
                self.redirect("/admlogin")
                return
            self.path = "/index"

        if self.path == "/admpanel" and not self.is_logged_in():
            self.redirect("/admlogin")
            return

        if self.path == "/admlogin" and self.is_logged_in():
            self.redirect("/admpanel")
            return

        if self.path == "/logout":
            self.clear_login()
            return

        file_path = f"servers/web_files{self.path}.html"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                livereload_script = (
                    f'<script src="http://127.0.0.1:{self.server.server_address[1] + 1}/livereload.js?snipver=1"></script>'
                )
                if "</body>" in content:
                    content = content.replace("</body>", f"{livereload_script}\n</body>")
                else:
                    content += livereload_script

                content_bytes = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content_bytes)))
                self.end_headers()
                self.wfile.write(content_bytes)
                return
            except FileNotFoundError:
                pass

        super().do_GET()

    # ------------------- POST -------------------
    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = parse_qs(body)

            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            if (username, password) in self.credentials:
                self.send_response(302)
                self.send_header("Location", "/admpanel")
                c = cookies.SimpleCookie()
                c["auth_token"] = "1"
                c["auth_token"]["path"] = "/"
                self.send_header("Set-Cookie", c.output(header="", sep=""))
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
        else:
            self.send_error(404, "Not Found")

    # ------------------- helpers -------------------
    def redirect(self, location: str):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def is_logged_in(self):
        cookie = self.headers.get("Cookie")
        return cookie and "auth_token=1" in cookie

    def clear_login(self):
        self.send_response(302)
        self.send_header("Location", "/admlogin")
        c = cookies.SimpleCookie()
        c["auth_token"] = ""
        c["auth_token"]["path"] = "/"
        c["auth_token"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        self.send_header("Set-Cookie", c.output(header="", sep=""))
        self.end_headers()


class WebServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.httpd = None
        self.http_thread: Thread | None = None
        self.lr_thread: Thread | None = None
        self.livereload: LiveReloadServer | None = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.httpd = socketserver.ThreadingTCPServer((self.host, self.port), WebHandler)
        self.http_thread = Thread(target=self.httpd.serve_forever, name="HTTPServerThread")
        self.http_thread.start()

        self.livereload = LiveReloadServer()
        self.livereload.watch("servers/web_files/**/*.html")
        self.livereload.watch("servers/web_files/**/*.css", delay=0.2)
        self.livereload.watch("servers/web_files/**/*.js", delay=0.2)
        self.livereload.watch("servers/web_files/**/*.*")

        def run_lr():
            self.livereload.serve(port=self.port + 1)

        self.lr_thread = Thread(target=run_lr, name="LiveReloadThread")
        self.lr_thread.start()

        self.running = True
        console.print(f"[green]🌍 Web server started at http://{self.host}:{self.port}[/green]")

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

        console.print("[red]🛑 Web server closed[/red]")
