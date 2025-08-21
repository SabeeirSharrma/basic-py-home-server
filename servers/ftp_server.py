import os
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer as PyFTPServer
from rich.console import Console

console = Console()

class FTPServer:
    def __init__(self, host="127.0.0.1", port=21, user="admin", password="12345", directory="servers/web_files"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.directory = os.path.abspath(directory)
        self.server = None
        self.thread = None

    def start(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.user, self.password, self.directory, perm="elradfmwMT")
        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = PyFTPServer((self.host, self.port), handler)

        def serve():
            console.print(f"[blue]📂 FTPServer running on ftp://{self.host}:{self.port}[/blue]")
            try:
                self.server.serve_forever()
            except Exception as e:
                console.print(f"[red]❌ FTPServer error: {e}[/red]")

        self.thread = Thread(target=serve, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            console.print("[yellow]⚠️ Stopping FTPServer...[/yellow]")
            self.server.close_all()
            if self.thread:
                self.thread.join(timeout=2)
            console.print("[yellow]🛑 FTPServer stopped[/yellow]")
