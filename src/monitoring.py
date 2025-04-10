# src/monitoring.py
from prometheus_client import Counter, start_http_server

messages_processed = Counter("messages_processed", "Jami qayta ishlangan xabarlar")

def setup_monitoring():
    start_http_server(8001)  # Metrikalar uchun port