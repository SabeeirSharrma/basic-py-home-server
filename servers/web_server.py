import http.server
import socketserver
import json
import os
import time
import psutil
from http import cookies
from urllib.parse import parse_qs

ftp_credentials = {"user": "admin", "password": "12345"}  # fallback

# Track network I/O for upload/download
last_net_io = {
    "time": time.time(),
    "bytes_sent": psutil.net_io_counters().bytes_sent,
    "bytes_recv": psutil.net_io_counters().bytes_recv,
}

# Load credentials from login.txt
def load_credentials():
    creds = {}
    if os.path.exists("login.txt"):
        with open("login.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                if ":" in line:
                    user, pw = line.split(":", 1)
                    creds[user.strip()] = pw.strip()
    return creds


# Sessions in memory {session_id: username}
sessions = {}

import uuid


class WebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="servers/web_files", **kwargs)

    def is_logged_in(self):
        if "Cookie" in self.headers:
            c = cookies.SimpleCookie(self.headers["Cookie"])
            if "session" in c:
                sid = c["session"].value
                if sid in sessions:
                    return True
        return False

    def do_GET(self):
        global last_net_io

        # Routing rules
        if self.path in ["/", "", "/index", "/index.html"]:
            self.path = "/index.html"
        elif self.path == "/admlogin":
            self.path = "/admlogin.html"
        elif self.path == "/admpanel":
            if not self.is_logged_in():
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
                return
            self.path = "/admpanel.html"
        elif self.path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session=; Max-Age=0")
            self.send_header("Location", "/admlogin")
            self.end_headers()
            return

        # API endpoint
        if self.path == "/api/stats":
            now = time.time()
            net_io = psutil.net_io_counters()
            elapsed = now - last_net_io["time"]
            if elapsed <= 0:
                elapsed = 1e-6

            upload_bps = (net_io.bytes_sent - last_net_io["bytes_sent"]) / elapsed
            download_bps = (net_io.bytes_recv - last_net_io["bytes_recv"]) / elapsed

            last_net_io = {
                "time": now,
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
            }

            def human_readable_speed(bps):
                if bps < 1024:
                    return f"{bps:.2f} B/s"
                elif bps < 1024**2:
                    return f"{bps/1024:.2f} KB/s"
                else:
                    return f"{bps/1024**2:.2f} MB/s"

            stats = {
                "cpu": round(psutil.cpu_percent(), 2),
                "ram": round(psutil.virtual_memory().used / (1024 * 1024), 2),
                "download": human_readable_speed(download_bps),
                "upload": human_readable_speed(upload_bps),
                "ftp_user": ftp_credentials["user"],
                "ftp_pass": ftp_credentials["password"]
                if ftp_credentials["password"]
                else "No password (anonymous)",
                "web_port": self.server.server_address[1],
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        # fallback
        file_path = os.path.join("servers/web_files", self.path.lstrip("/"))
        if not os.path.exists(file_path):
            self.path = "/index.html"
        
        if self.path == "/admlogin":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = parse_qs(body)

            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]

            credentials = load_credentials()

            if username in credentials and credentials[username] == password:
                # ✅ Success → create session and go to /admpanel
                sid = str(uuid.uuid4())
                sessions[sid] = username
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; HttpOnly; Path=/")
                self.send_header("Location", "/admpanel")
                self.end_headers()
            else:
                # ❌ Fail → reload /admlogin with error
                self.send_response(302)
                self.send_header("Location", "/admlogin?error=1")
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

        super().do_GET()

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = dict(x.split("=") for x in body.split("&") if "=" in x)

            username = params.get("username", "")
            password = params.get("password", "")

            credentials = load_credentials()
            if username in credentials and credentials[username] == password:
                # success → create session
                sid = str(uuid.uuid4())
                sessions[sid] = username
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; HttpOnly")
                self.send_header("Location", "/admpanel")
                self.end_headers()
            else:
                # fail → back to login
                self.send_response(302)
                self.send_header("Location", "/admlogin")
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


class WebServer:
    def __init__(self, port=8080):
        self.port = port
        self.httpd = socketserver.ThreadingTCPServer(("", port), WebHandler)

    def start(self):
        print(f"🌐 Web server running at http://localhost:{self.port}")
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
