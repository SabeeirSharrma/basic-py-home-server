import http.server
import socketserver
import os
import json
import urllib.parse
import psutil
from threading import Thread
from rich.console import Console

console = Console()

# Sessions for login
sessions = {}
SESSION_COOKIE = "ADMSESSION"

def read_login(file="servers/login.txt"):
    creds = {"username": "admin", "password": "12345"}
    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    creds[k.strip()] = v.strip()
    return creds

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".html"):
            self.path = self.path.replace(".html", "")

        if self.path == "/":
            self.path = "/index.html"
        elif self.path == "/index":
            self.path = "/index.html"
        elif self.path == "/admpanel":
            if not self.is_authenticated():
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
                return
            self.path = "/admpanel.html"
        elif self.path == "/admlogin":
            self.path = "/admlogin.html"

        elif self.path.startswith("/api/stats"):
            stats = {
                "cpu": f"{psutil.cpu_percent()}%",
                "ram": f"{psutil.virtual_memory().used // (1024*1024)} MB / {psutil.virtual_memory().total // (1024*1024)} MB",
                "download": f"{psutil.net_io_counters().bytes_recv // (1024*1024)} MB",
                "upload": f"{psutil.net_io_counters().bytes_sent // (1024*1024)} MB",
                "ftp_user": self.server.ftp_user,
                "ftp_pass": self.server.ftp_pass,
                "web_port": self.server.port,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            data = urllib.parse.parse_qs(self.rfile.read(length).decode())
            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            creds = read_login()
            if username == creds["username"] and password == creds["password"]:
                session_id = os.urandom(16).hex()
                sessions[session_id] = True
                self.send_response(302)
                self.send_header("Location", "/admpanel")
                self.send_header("Set-Cookie", f"{SESSION_COOKIE}={session_id}; HttpOnly")
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/admlogin?error=1")
                self.end_headers()
        else:
            self.send_error(501, "Unsupported method (POST)")

    def is_authenticated(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            if SESSION_COOKIE in part:
                session_id = part.strip().split("=", 1)[1]
                return session_id in sessions
        return False

class WebServer:
    def __init__(self, port=8080, directory="servers/web_files"):
        self.port = port
        self.directory = os.path.abspath(directory)
        self.httpd = None
        self.thread = None
        self.ftp_user = "admin"
        self.ftp_pass = "12345"

    def start(self):
        if not os.path.exists(self.directory):
            console.print(f"[red]❌ Web directory not found: {self.directory}[/red]")
            return

        os.chdir(self.directory)
        handler = CustomHandler
        handler.extensions_map.update({
            ".js": "application/javascript",
            ".css": "text/css",
        })
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        self.httpd.port = self.port
        self.httpd.ftp_user = self.ftp_user
        self.httpd.ftp_pass = self.ftp_pass

        def serve():
            console.print(f"[green]🌐 WebServer running on port {self.port}[/green]")
            try:
                self.httpd.serve_forever()
            except Exception as e:
                console.print(f"[red]❌ WebServer error: {e}[/red]")

        self.thread = Thread(target=serve, daemon=True)
        self.thread.start()

    def stop(self):
        if self.httpd:
            console.print("[yellow]⚠️ Stopping WebServer...[/yellow]")
            self.httpd.shutdown()
            self.httpd.server_close()
            if self.thread:
                self.thread.join(timeout=2)
            console.print("[red]🛑 WebServer stopped[/red]")
