import os
import sys
from rich.console import Console
from rich.panel import Panel
from server_manager import ServerManager
from servers.web_server import WebServer
from servers.ftp_server import FTPServer, set_ftp_credentials, ftp_credentials

console = Console()

def load_settings(file="settings.txt"):
    """Read settings.txt into a dictionary"""
    settings = {
        "port": "8080",
        "ftp_port": "21",
        "ftp_user": "admin",
        "ftp_pass": "12345"
    }
    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    return settings

def save_settings(settings, file="settings.txt"):
    """Write settings back to file"""
    with open(file, "w") as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")

def main():
    settings = load_settings()

    # Start servers
    manager = ServerManager()

    # Web server
    web_server = WebServer(port=int(settings.get("port", 8080)))
    manager.add_server(web_server)

    # FTP server
    ftp_server = FTPServer(
        host="127.0.0.1",
        port=int(settings.get("ftp_port", 21)),
        user=settings.get("ftp_user", "admin"),
        password=settings.get("ftp_pass", "12345"),
    )
    manager.add_server(ftp_server)

    # Pretty startup banner
    console.print(Panel.fit("🚀 Home Server Started 🚀", style="bold cyan"))
    console.print(f"🌍 [bold green]Web server running[/bold green] at: [cyan]http://127.0.0.1:{settings.get('port')}[/cyan]")
    console.print(f"📂 [bold blue]FTP server running[/bold blue] at: [cyan]ftp://127.0.0.1:{settings.get('ftp_port')}[/cyan]")
    console.print(f"   ➤ Username: [bold yellow]{ftp_server.user}[/bold yellow]")
    console.print(f"   ➤ Password: [bold yellow]{ftp_server.password if ftp_server.password else 'No password (anonymous)'}[/bold yellow]\n")

    # Start all servers
    manager.start_all()

    console.print("[bold yellow]Type 'stop' to shut down.[/bold yellow]")
    console.print("[bold yellow]Type 'help' or '?' for commands.[/bold yellow]")

    try:
        while True:
            cmd = input("> ").strip()
            if cmd.lower() == "stop":
                console.print("[red]Shutting down servers...[/red]")
                manager.stop_all()
                break

            elif cmd.lower() in ["help", "?"]:
                console.print("""
[bold cyan]Available commands:[/bold cyan]
  [yellow]stop[/yellow]  - Stop all servers
  [yellow]help / ?[/yellow] - Show this help
  [yellow]ftp edit -user=NAME -pass=PASS[/yellow] → Change FTP credentials (use -pass=* for no password)
  [yellow]web set -port=PORT[/yellow] → Change web server port
                """)

            elif cmd.startswith("ftp edit"):
                new_user, new_pass = None, None
                for p in cmd.split():
                    if p.startswith("-user="):
                        new_user = p.split("=", 1)[1]
                    elif p.startswith("-pass="):
                        new_pass = p.split("=", 1)[1]

                if new_pass == "*":
                    new_pass = None

                if new_user or new_pass is not None:
                    set_ftp_credentials(new_user or ftp_server.user, new_pass if new_pass is not None else ftp_server.password)
                    ftp_server.user = ftp_credentials["user"]
                    ftp_server.password = ftp_credentials["pass"]
                    settings["ftp_user"] = ftp_server.user
                    settings["ftp_pass"] = ftp_server.password or ""
                    save_settings(settings)
                    console.print(f"[green]✅ FTP credentials updated![/green]\n  Username: {ftp_server.user}\n  Password: {ftp_server.password}")
                else:
                    console.print("[red]⚠ Invalid syntax. Use: ftp edit -user=NAME -pass=PASS[/red]")

            elif cmd.startswith("web set"):
                parts = cmd.split()
                new_port = None
                for p in parts:
                    if p.startswith("-port="):
                        new_port = int(p.split("=", 1)[1])

                if new_port:
                    console.print(f"[green]✅ Web server port updated to {new_port}! Restart required.[/green]")
                    settings["port"] = str(new_port)
                    save_settings(settings)
                else:
                    console.print("[red]⚠ Invalid syntax. Use: web set -port=PORT[/red]")

            else:
                console.print(f"[red]⚠ Unknown command:[/red] {cmd}")

    except KeyboardInterrupt:
        console.print("\n[red]Ctrl+C detected, shutting down...[/red]")
        manager.stop_all()

if __name__ == "__main__":
    main()
