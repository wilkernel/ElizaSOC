"""
Domain Ports - Interfaces que o domínio define (Ports no padrão Ports & Adapters)
"""

from .scanner_port import ScannerPort
from .repository_port import RepositoryPort
from .threat_intelligence_port import ThreatIntelligencePort

__all__ = [
    "ScannerPort",
    "RepositoryPort",
    "ThreatIntelligencePort",
]
