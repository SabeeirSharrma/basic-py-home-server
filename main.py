import os
from server_manager import ServerManager
from servers.web_server import WebServer


def read_settings(filename="settings.txt"):
    """Read host and port from settings.txt"""
    settings = {"host": "127.0.0.1", "port": 8080}  # defaults

    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "host":
                    settings["host"] = value
                elif key == "port":
                    try:
                        settings["port"] = int(value)
                    except ValueError:
                        print(f"Invalid port in settings.txt, using default {settings['port']}")

    return settings


def main():
    settings = read_settings()

    manager = ServerManager()
    web_server = WebServer(
        host=settings["host"],
        port=settings["port"],
        web_root="htdocs"
    )
    manager.add_server(web_server)

    print(f"Starting web server on {settings['host']}:{settings['port']} (type 'stop' to quit)")
    manager.start_all()

    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "stop":
                print("Stopping all servers...")
                manager.stop_all()
                break
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Stopping servers...")
        manager.stop_all()


if __name__ == "__main__":
    main()
