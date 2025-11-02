"""
Entidade SecurityEvent - Representa um evento de segurança
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class EventType(Enum):
    """Tipos de eventos de segurança"""
    ALERT = "alert"
    FLOW = "flow"
    DNS = "dns"
    FILE_EXTRACT = "file_extract"
    HTTP = "http"
    TLS = "tls"
    FILE_SCAN = "file_scan"
    THREAT_INTEL = "threat_intel"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    CORRELATION = "correlation"
    AUTOMATED_RESPONSE = "automated_response"


@dataclass
class SecurityEvent:
    """
    Entidade SecurityEvent - Evento de segurança do sistema
    
    Atributos:
        id: Identificador único do evento
        event_type: Tipo do evento
        timestamp: Data e hora do evento
        source: Fonte do evento (Suricata, ClamAV, etc)
        data: Dados do evento
        metadata: Metadados adicionais
        related_events: IDs de eventos relacionados
        processed: Se o evento já foi processado
    """
    id: str
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_events: List[str] = field(default_factory=list)
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
            "related_events": self.related_events,
            "processed": self.processed,
        }
    
    def add_related_event(self, event_id: str) -> None:
        """Adiciona um evento relacionado"""
        if event_id not in self.related_events:
            self.related_events.append(event_id)
    
    def is_alert(self) -> bool:
        """Verifica se é um evento de alerta"""
        return self.event_type == EventType.ALERT

