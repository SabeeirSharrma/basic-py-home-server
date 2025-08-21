import os
import urllib.parse
import http.cookies
import random
import string
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import psutil

# -------------------------
# Load Admin Login (from login.txt)
# -------------------------
def load_login(file="servers/web_files/login.txt"):
    creds = {"username": "admin", "password": "12345"}
    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    creds[key.strip()] = value.strip()
    return creds

# Active sessions
sessions = {}

# Global FTP credentials (updated from main.py)
ftp_user = "admin"
ftp_pass = "12345"

def set_ftp_credentials(user, password):
    """Update FTP credentials for API stats"""
    global ftp_user, ftp_pass
    ftp_user = user
    ftp_pass = password


class SimpleRequestHandler(BaseHTTPRequestHandler):
    def _is_logged_in(self):
        """Check if session cookie is valid"""
        if "Cookie" in self.headers:
            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" in cookie:
                sid = cookie["session_id"].value
                if sid in sessions:
                    return True
        return False

    def _serve_file(self, path, content_type="text/html"):
        """Serve static files from web_files"""
        try:
            with open(os.path.join("servers/web_files", path), "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_GET(self):
        # -----------------
        # Login page
        # -----------------
        if self.path in ["/admlogin", "/admlogin/"]:
            return self._serve_file("admlogin.html")

        # -----------------
        # Logout
        # -----------------
        if self.path.startswith("/logout"):
            sid = None
            if "Cookie" in self.headers:
                cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
                if "session_id" in cookie:
                    sid = cookie["session_id"].value
            if sid and sid in sessions:
                del sessions[sid]

            self.send_response(302)
            self.send_header("Location", "/admlogin")
            self.send_header("Set-Cookie", "session_id=deleted; Max-Age=0")
            self.end_headers()
            return

        # -----------------
        # Admin panel (protected)
        # -----------------
        if self.path in ["/admpanel", "/admpanel/"]:
            if not self._is_logged_in():
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
                return
            return self._serve_file("admpanel.html")

        # -----------------
        # API Stats (protected)
        # -----------------
        if self.path == "/api/stats":
            if not self._is_logged_in():
                self.send_error(403, "Forbidden")
                return
            stats = {
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "download": f"{psutil.net_io_counters().bytes_recv / 1024:.2f} KB",
                "upload": f"{psutil.net_io_counters().bytes_sent / 1024:.2f} KB",
                "ftp_user": ftp_user,
                "ftp_pass": ftp_pass if ftp_pass else "anonymous",
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        # -----------------
        # Static resources (CSS/JS)
        # -----------------
        if self.path.endswith(".css"):
            return self._serve_file(self.path.lstrip("/"), "text/css")
        if self.path.endswith(".js"):
            return self._serve_file(self.path.lstrip("/"), "application/javascript")

        # -----------------
        # Default: index.html
        # -----------------
        if self.path in ["/", "/index"]:
            return self._serve_file("index.html")

        # 404 if nothing matched
        self.send_error(404, "Unknown endpoint")

    def do_POST(self):
        # -----------------
        # Handle login form
        # -----------------
        if self.path == "/admlogin":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = urllib.parse.parse_qs(body)

            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]

            creds = load_login()

            if username == creds["username"] and password == creds["password"]:
                # Generate new session
                sid = "".join(random.choices(string.ascii_letters + string.digits, k=32))
                sessions[sid] = username

                self.send_response(302)
                self.send_header("Location", "/admpanel")
                self.send_header("Set-Cookie", f"session_id={sid}; HttpOnly")
                self.end_headers()
            else:
                # Invalid login → back to login page
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
        else:
            self.send_error(501, "Unsupported method")

class WebServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port

    def start(self):
        server_address = (self.host, self.port)
        httpd = HTTPServer(server_address, SimpleRequestHandler)
        print(f"🌍 Web server running at http://{self.host}:{self.port}")
        httpd.serve_forever()
