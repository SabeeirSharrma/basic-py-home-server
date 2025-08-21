from pyftpdlib.servers import FTPServer as PyFTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
import os

ftp_credentials = {
    "user": "admin",
    "pass": "12345"
}

def set_ftp_credentials(user, password, file="settings.txt"):
    ftp_credentials["user"] = user
    ftp_credentials["pass"] = password

    # update settings.txt
    lines = []
    if os.path.exists(file):
        with open(file, "r") as f:
            lines = f.readlines()

    with open(file, "w") as f:
        found_user, found_pass = False, False
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
    def __init__(self, host="127.0.0.1", port=21, user="admin", password="12345"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.server = None

    def start(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.user, self.password or "", ".", perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = PyFTPServer((self.host, self.port), handler)
        print(f"[FTPServer] Running on {self.host}:{self.port}")
        self.server.serve_forever()

    def stop(self):
        if self.server:
            print("[FTPServer] Stopping...")
            self.server.close_all()
