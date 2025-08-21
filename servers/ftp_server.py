import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer as PyFTPServer

class FTPServer:
    def __init__(self, host="127.0.0.1", port=21, user="admin", password="12345"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.server = None
        self.thread = None

        # Ensure FTP root directory exists
        self.directory = os.path.join(os.path.dirname(__file__), "web_files")
        os.makedirs(self.directory, exist_ok=True)

    def start(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.user, self.password, self.directory, perm="elradfmw")  # full access
    

        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = PyFTPServer((self.host, self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"FTP server running on {self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.close_all()
            print("🛑 FTP server stopped")
