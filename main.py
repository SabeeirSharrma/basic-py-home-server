import os
from rich.console import Console
from rich.panel import Panel
from server_manager import ServerManager
from servers.web_server import WebServer
from servers.ftp_server import FTPServer, set_ftp_credentials, ftp_credentials
from admin_panel import AdminPanelServer  # NEW

console = Console()
manager = ServerManager()


def load_settings(file="settings.txt"):
    """Read settings.txt into a dictionary"""
    settings = {
        "web_port": "8080",
        "admin_port": "8081",  # NEW
        "ftp_port": "21",
        "ftp_user": ftp_credentials["user"],
        "ftp_pass": ftp_credentials["password"]
    }
    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    return settings


def save_settings(settings, file="settings.txt"):
    with open(file, "w") as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")


def main():
    settings = load_settings()

    # Sync FTP credentials with settings.txt at startup
    set_ftp_credentials(
        user=settings.get("ftp_user", "admin"),
        password=settings.get("ftp_pass", "12345"),
        settings_file="settings.txt"
    )

    # Start servers
    manager = ServerManager()

    # Web server
    web_server = WebServer(port=int(settings.get("web_port", 8080)))
    manager.add_server(web_server)

    # FTP server
    ftp_server = FTPServer(
        host="127.0.0.1",
        port=int(settings.get("ftp_port", 21))
    )
    manager.add_server(ftp_server)

    # Admin Panel server
    admin_server = AdminPanelServer(
        host="127.0.0.1",
        port=int(settings.get("admin_port", 8081))
    )
    manager.add_server(admin_server)

    # Pretty startup banner
    console.print(Panel.fit("🚀 Home Server Started 🚀", style="bold cyan"))
    console.print(f"🌍 [bold green]Web server running[/bold green] at: [cyan]http://127.0.0.1:{web_server.port}[/cyan]")
    console.print(f"🔑 [bold magenta]Admin panel running[/bold magenta] at: [cyan]http://127.0.0.1:{admin_server.port}/[/cyan]")
    console.print(f"📂 [bold blue]FTP server running[/bold blue] at: [cyan]ftp://127.0.0.1:{ftp_server.port}[/cyan]")
    console.print(f"   ➤ Username: [bold yellow]{ftp_credentials['user']}[/bold yellow]")
    console.print(f"   ➤ Password: [bold yellow]{ftp_credentials['password'] if ftp_credentials['password'] else 'No password (anonymous)'}[/bold yellow]\n")

    # Start all servers
    manager.start_all()

    console.print("[bold yellow]Type 'stop' to shut down.[/bold yellow]")
    console.print("[bold yellow]Type 'help' or '?' for commands.[/bold yellow]")

    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "stop":
                console.print("[cyan]Shutting down servers...[/cyan]")
                manager.stop_all()
                console.print("[bold red]🛑 All servers closed. You can now exit safely.[/bold red]")
                break

            elif cmd in ["help", "?"]:
                console.print("""
[bold cyan]Available commands:[/bold cyan]
  [yellow]stop[/yellow]  - Stop all servers
  [yellow]help / ?[/yellow] - Show this help
  [yellow]ftp edit -user={username} -pass={password}[/yellow]
     → Change FTP credentials (use -pass=* to remove password)
  [yellow]web set -port={PORT}[/yellow]
     → Change the web server port dynamically
  [yellow]admin set -port={PORT}[/yellow]
     → Change the admin panel port dynamically
                """)

            elif cmd.startswith("ftp edit"):
                parts = cmd.split()
                new_user, new_pass = None, None
                for p in parts:
                    if p.startswith("-user="):
                        new_user = p.split("=", 1)[1]
                    elif p.startswith("-pass="):
                        new_pass = p.split("=", 1)[1]

                if new_user or new_pass is not None:
                    if new_pass == "*":
                        new_pass = None
                    # Update credentials globally + settings.txt
                    set_ftp_credentials(
                        user=new_user or ftp_credentials["user"],
                        password=new_pass if new_pass is not None else ftp_credentials["password"],
                        settings_file="settings.txt"
                    )
                    console.print(f"[green]✅ FTP credentials updated![/green]\n  Username: {ftp_credentials['user']}\n  Password: {ftp_credentials['password'] or 'anonymous'}")
                else:
                    console.print("[red]⚠ Invalid syntax. Use: ftp edit -user=NAME -pass=PASS[/red]")

            elif cmd.startswith("web set -port="):
                try:
                    new_port = int(cmd.split("=", 1)[1])
                    console.print(f"[cyan]🔄 Restarting web server on port {new_port}...[/cyan]")
                    web_server.stop()
                    web_server = WebServer(port=new_port)
                    manager.add_server(web_server)
                    web_server.start()

                    settings["web_port"] = str(new_port)
                    save_settings(settings)

                    console.print(f"[green]✅ Web server restarted at http://127.0.0.1:{new_port}[/green]")
                except Exception as e:
                    console.print(f"[red]⚠ Failed to change web port: {e}[/red]")

            elif cmd.startswith("admin set -port="):
                try:
                    new_port = int(cmd.split("=", 1)[1])
                    console.print(f"[cyan]🔄 Restarting admin panel on port {new_port}...[/cyan]")
                    admin_server.stop()
                    admin_server = AdminPanelServer(port=new_port)
                    manager.add_server(admin_server)
                    admin_server.start()

                    settings["admin_port"] = str(new_port)
                    save_settings(settings)

                    console.print(f"[green]✅ Admin panel restarted at http://127.0.0.1:{new_port}/admlogin[/green]")
                except Exception as e:
                    console.print(f"[red]⚠ Failed to change admin port: {e}[/red]")

    except KeyboardInterrupt:
        console.print("\n[red]Ctrl+C detected, shutting down...[/red]")
        manager.stop_all()
        console.print("[red]🛑 Web server closed[/red]")
        console.print("[yellow]🛑 FTP server closed[/yellow]")
        console.print("[magenta]🛑 Admin panel closed[/magenta]")
        console.print("You can now close this window")


if __name__ == "__main__":
    main()
