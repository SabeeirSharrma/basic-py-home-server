from rich.console import Console
import threading, queue

console = Console()
log_queue = queue.Queue()

def log_message(msg: str):
    """Thread-safe logger"""
    log_queue.put(msg)

def log_worker():
    """Continuously print logs as they arrive"""
    while True:
        msg = log_queue.get()
        console.print(msg)

# Start the logger thread on import
threading.Thread(target=log_worker, daemon=True).start()
