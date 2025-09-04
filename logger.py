# logger.py
import queue
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
import threading

console = Console()
log_queue = queue.Queue()
logs = []
stop_event = threading.Event()

def log(msg: str, style: str = "white"):
    """Thread-safe logging function"""
    log_queue.put((msg, style))

def log_worker():
    """Worker that renders logs in a Rich Live panel"""
    with Live(console=console, refresh_per_second=10, screen=False) as live:
        while not stop_event.is_set():
            try:
                msg, style = log_queue.get(timeout=0.1)
                logs.append(f"[{style}]{msg}[/{style}]")
                log_view = "\n".join(logs[-15:])  # keep last 15
                live.update(
                    Panel(
                        Align.left(log_view),
                        title="📜 Logs",
                        border_style="cyan",
                        padding=(1, 2)
                    )
                )
            except queue.Empty:
                continue
