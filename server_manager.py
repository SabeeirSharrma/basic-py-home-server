class ServerManager:
    def __init__(self):
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def start_all(self):
        for server in self.servers:
            server.start()

    def stop_all(self):
        for server in self.servers:
            server.stop()
