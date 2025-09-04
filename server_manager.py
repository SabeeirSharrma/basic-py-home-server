from rich.console import Console

console = Console()

class ServerManager:
    def __init__(self):
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def start_all(self):
        for s in self.servers:
            try:
                s.start()
            except Exception as e:
                console.print(f"[red]⚠ Failed to start {s.__class__.__name__}: {e}[/red]")

    def stop_all(self):
        for s in self.servers:
            try:
                s.stop()
                console.print(f"[green]✅ {s.__class__.__name__} stopped[/green]")
            except Exception as e:
                console.print(f"[red]⚠ Failed to stop {s.__class__.__name__}: {e}[/red]")
        self.servers.clear()
