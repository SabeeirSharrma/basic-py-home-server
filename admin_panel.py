# admin_panel.py
import http.server
import socketserver
import json
import os
import time
import psutil
import threading
from urllib.parse import urlparse, parse_qs

# pull the live FTP creds from the running FTP server module
try:
    from servers.ftp_server import ftp_credentials
except Exception:
    ftp_credentials = {"user": "admin", "password": "12345"}

# ---------- helpers ----------
def load_settings():
    s = {}
    if os.path.exists("settings.txt"):
        with open("settings.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    s[k.strip()] = v.strip()
    return s

_last_net = {
    "time": time.time(),
    "sent": psutil.net_io_counters().bytes_sent,
    "recv": psutil.net_io_counters().bytes_recv,
}

_last_speedtest = {
    "time": 0,
    "download": None,
    "upload": None,
    "error": None,
}

def run_speedtest():
    """Run speedtest-cli and cache results (bits/sec)."""
    global _last_speedtest
    try:
        import speedtest  # pip install speedtest-cli
        st = speedtest.Speedtest()
        st.get_best_server()
        dl = st.download()
        ul = st.upload()
        _last_speedtest.update({"time": time.time(), "download": dl, "upload": ul, "error": None})
    except Exception as e:
        _last_speedtest.update({"time": time.time(), "download": None, "upload": None, "error": str(e)})

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="adminpanel", **kwargs)

    # small JSON helper
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # routes
        if self.path in ("/", "/admpanel", "/admpanel.html"):
            self.path = "/admpanel.html"
            return super().do_GET()

        if self.path == "/logout":
            # no auth now; keep link harmless
            self.send_response(302)
            self.send_header("Location", "/admpanel")
            self.end_headers()
            return

        if self.path.startswith("/stats"):
            vm = psutil.virtual_memory()
            # More realistic "used" on Windows: total - available
            used = vm.total - vm.available
            cpu = psutil.cpu_percent(interval=0.1)

            now = time.time()
            io = psutil.net_io_counters()
            dt = max(now - _last_net["time"], 1e-6)
            up_bps = (io.bytes_sent - _last_net["sent"]) / dt
            down_bps = (io.bytes_recv - _last_net["recv"]) / dt
            _last_net.update({"time": now, "sent": io.bytes_sent, "recv": io.bytes_recv})

            out = {
                "cpu_usage": round(cpu, 1),
                "ram_used_mb": round(used / (1024 * 1024), 1),
                "ram_total_mb": round(vm.total / (1024 * 1024), 1),
                "ram_percent": round(vm.percent, 1),
                "net_up_bps": up_bps,
                "net_down_bps": down_bps,
            }
            return self._json(out)

        if self.path.startswith("/speedtest"):
            # cache for 5 minutes unless ?refresh=1
            qs = parse_qs(urlparse(self.path).query)
            force = qs.get("refresh", ["0"])[0] == "1"
            fresh = (time.time() - _last_speedtest["time"]) < 300

            if not force and fresh and _last_speedtest["download"] is not None:
                return self._json(
                    {"download": _last_speedtest["download"], "upload": _last_speedtest["upload"], "error": None}
                )

            # run test in this request (blocking only this request)
            run_speedtest()
            return self._json(
                {"download": _last_speedtest["download"], "upload": _last_speedtest["upload"], "error": _last_speedtest["error"]}
            )

        if self.path.startswith("/settings"):
            s = load_settings()
            data = {
                "web_port": int(s.get("web_port", "8080")),
                "admin_port": int(s.get("admin_port", s.get("admp_port", "9090"))),
                "ftp_user": ftp_credentials.get("user", "admin"),
                "ftp_pass": ftp_credentials.get("password") or "",
            }
            return self._json(data)

        # static files in ./adminpanel
        return super().do_GET()

class AdminPanelServer:
    def __init__(self, host="127.0.0.1", port=9090):
        self.host = host
        self.port = port
        self.httpd = socketserver.ThreadingTCPServer((self.host, self.port), AdminHandler)
        self.thread: threading.Thread | None = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.httpd.serve_forever, name="AdminPanelServer", daemon=True)
        self.thread.start()
        try:
            from rich.console import Console
            Console().print(f"[green]🛡 Admin panel running at http://{self.host}:{self.port}/admpanel[/green]")
        except Exception:
            print(f"Admin panel running at http://{self.host}:{self.port}/admpanel")

    def stop(self):
        try:
            self.httpd.shutdown()
            self.httpd.server_close()
        except Exception:
            pass
