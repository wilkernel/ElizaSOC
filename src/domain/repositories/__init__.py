"""
Repositórios (Ports) - Interfaces para acesso a dados
"""
from .alert_repository import AlertRepository
from .file_scan_repository import FileScanRepository
from .event_repository import EventRepository
from .ioc_repository import IOCRepository

__all__ = [
    "AlertRepository",
    "FileScanRepository",
    "EventRepository",
    "IOCRepository",
]

