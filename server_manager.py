import threading
from rich.console import Console

console = Console()

class ServerManager:
    def __init__(self):
        self.servers = []
        self.threads = []

    def add_server(self, server):
        self.servers.append(server)

    def start_all(self):
        """Start all registered servers in their own threads"""
        for server in self.servers:
            t = threading.Thread(target=server.start, daemon=False)
            t.start()
            self.threads.append(t)

    def stop_all(self):
        for server in self.servers:
            try:
                server.stop()
            except Exception as e:
                console.print(f"[red]⚠ Error stopping server: {e}[/red]")

