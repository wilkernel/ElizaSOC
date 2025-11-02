"""
Entidades de Domínio
"""
from .alert import Alert, AlertSeverity, AlertCategory
from .file_scan import FileScanResult, ScanStatus
from .event import SecurityEvent, EventType
from .threat_intelligence import IOC, IOCType, IOCSource

__all__ = [
    "Alert",
    "AlertSeverity",
    "AlertCategory",
    "FileScanResult",
    "ScanStatus",
    "SecurityEvent",
    "EventType",
    "IOC",
    "IOCType",
    "IOCSource",
]

