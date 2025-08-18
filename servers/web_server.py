import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


class WebServer:
    def __init__(self, host="127.0.0.1", port=8080, web_root="htdocs"):
        self.host = host
        self.port = port
        self.web_root = os.path.abspath(web_root)
        self.httpd = None
        self.thread = None

    def start(self):
        """Start the web server in a background thread"""
        if not os.path.exists(self.web_root):
            os.makedirs(self.web_root)

        handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(
            *args, directory=self.web_root, **kwargs
        )

        self.httpd = HTTPServer((self.host, self.port), handler)
        print(f"Web server running at http://{self.host}:{self.port}")
        print(f"Serving files from: {self.web_root}")

        # Run in background thread so input() still works in main.py
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the web server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("Web server stopped.")
