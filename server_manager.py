import threading

class ServerManager:
    def __init__(self):
        self.servers = []
        self.threads = []

    def add_server(self, server):
        self.servers.append(server)

    def start_all(self):
        for server in self.servers:
            thread = threading.Thread(target=server.start, daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop_all(self):
        for server in self.servers:
            if hasattr(server, "stop"):
                server.stop()
