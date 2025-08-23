import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer as PyFTPServer
from rich.console import Console

console = Console()

ftp_credentials = {"user": "admin", "password": "12345"}


def set_ftp_credentials(user, password, settings_file="settings.txt"):
    ftp_credentials["user"] = user
    ftp_credentials["password"] = password

    lines = []
    try:
        with open(settings_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        pass

    with open(settings_file, "w") as f:
        found_user = found_pass = False
        for line in lines:
            if line.startswith("ftp_user="):
                f.write(f"ftp_user={user}\n")
                found_user = True
            elif line.startswith("ftp_pass="):
                f.write(f"ftp_pass={password or ''}\n")
                found_pass = True
            else:
                f.write(line)
        if not found_user:
            f.write(f"ftp_user={user}\n")
        if not found_pass:
            f.write(f"ftp_pass={password or ''}\n")


class FTPServer:
    def __init__(self, host="127.0.0.1", port=21):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            return

        authorizer = DummyAuthorizer()
        if ftp_credentials["password"]:
            authorizer.add_user(ftp_credentials["user"], ftp_credentials["password"], ".", perm="elradfmw")
        else:
            authorizer.add_anonymous(".", perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = PyFTPServer((self.host, self.port), handler)
        self.running = True

        def serve():
            try:
                self.server.serve_forever()
            except Exception:
                pass

        self.thread = threading.Thread(target=serve, daemon=True)
        self.thread.start()
        console.print(f"[green]📡 FTP server started at ftp://{self.host}:{self.port}[/green]")
        
    def stop(self):
            try:
                if self.server:
                    self.server.close_all()   # correct call
                    self.running = False
                console.print("[yellow]🛑 FTP server closed[/yellow]")
            except Exception as e:
                console.print(f"[red]⚠ Failed to stop FTP server: {e}[/red]")
