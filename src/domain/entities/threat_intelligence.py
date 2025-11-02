"""
Entidade IOC - Representa um Indicador de Comprometimento (IOC)
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class IOCType(Enum):
    """Tipos de IOCs"""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"  # MD5, SHA1, SHA256
    EMAIL = "email"
    FILENAME = "filename"
    USER_AGENT = "user_agent"


class IOCSource(Enum):
    """Fontes de Threat Intelligence"""
    ABUSE_CH = "abuse_ch"
    ALIENVAULT_OTX = "alienvault_otx"
    VIRUSTOTAL = "virustotal"
    EMERGING_THREATS = "emerging_threats"
    CUSTOM = "custom"
    INTERNAL = "internal"


@dataclass
class IOC:
    """
    Entidade IOC - Indicador de Comprometimento
    
    Atributos:
        id: Identificador único do IOC
        ioc_type: Tipo do IOC
        value: Valor do IOC (IP, domínio, hash, etc)
        source: Fonte do IOC
        threat_type: Tipo de ameaça (malware, phishing, etc)
        confidence: Nível de confiança (0-100)
        first_seen: Primeira vez que foi visto
        last_seen: Última vez que foi visto
        metadata: Metadados adicionais
        active: Se o IOC está ativo
    """
    id: str
    ioc_type: IOCType
    value: str
    source: IOCSource
    threat_type: str
    confidence: int  # 0-100
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte IOC para dicionário"""
        return {
            "id": self.id,
            "ioc_type": self.ioc_type.value,
            "value": self.value,
            "source": self.source.value,
            "threat_type": self.threat_type,
            "confidence": self.confidence,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata,
            "active": self.active,
        }
    
    def matches(self, value: str) -> bool:
        """Verifica se um valor corresponde a este IOC"""
        return self.value.lower() == value.lower()
    
    def is_high_confidence(self) -> bool:
        """Verifica se o IOC tem alta confiança"""
        return self.confidence >= 70
    
    def update_last_seen(self) -> None:
        """Atualiza o timestamp de última visualização"""
        self.last_seen = datetime.utcnow()

