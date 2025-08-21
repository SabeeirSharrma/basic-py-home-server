import threading

class ServerManager:
    def __init__(self):
        self.servers = []
        self.threads = []

    def add_server(self, server):
        self.servers.append(server)

    def start_all(self):
        for server in self.servers:
            t = threading.Thread(target=server.start, daemon=True)
            t.start()
            self.threads.append(t)

    def stop_all(self):
        for server in self.servers:
            server.stop()
        for t in self.threads:
            t.join(timeout=1)
