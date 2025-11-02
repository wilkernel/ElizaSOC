"""
Entidade Alert - Representa um alerta de segurança
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class AlertSeverity(Enum):
    """Níveis de severidade de alertas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertCategory(Enum):
    """Categorias de alertas"""
    PHISHING = "phishing"
    MALWARE = "malware"
    VIRUS = "virus"
    TROJAN = "trojan"
    RANSOMWARE = "ransomware"
    SUSPICIOUS = "suspicious"
    INTRUSION = "intrusion"
    DATA_EXFILTRATION = "data_exfiltration"
    C2_COMMUNICATION = "c2_communication"
    UNKNOWN = "unknown"


@dataclass
class Alert:
    """
    Entidade Alert - Representa um alerta de segurança detectado
    
    Atributos:
        id: Identificador único do alerta
        timestamp: Data e hora do alerta
        signature: Assinatura/regra que disparou o alerta
        category: Categoria do alerta
        severity: Severidade do alerta
        src_ip: IP de origem
        dest_ip: IP de destino
        src_port: Porta de origem
        dest_port: Porta de destino
        protocol: Protocolo usado (TCP, UDP, etc)
        metadata: Metadados adicionais do alerta
        correlated: Se o alerta foi correlacionado com outros eventos
        processed: Se o alerta já foi processado
    """
    id: str
    timestamp: datetime
    signature: str
    category: AlertCategory
    severity: AlertSeverity
    src_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    src_port: Optional[int] = None
    dest_port: Optional[int] = None
    protocol: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlated: bool = False
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "signature": self.signature,
            "category": self.category.value,
            "severity": self.severity.value,
            "src_ip": self.src_ip,
            "dest_ip": self.dest_ip,
            "src_port": self.src_port,
            "dest_port": self.dest_port,
            "protocol": self.protocol,
            "metadata": self.mark_private_ips(),
            "correlated": self.correlated,
            "processed": self.processed,
        }
    
    def mark_private_ips(self) -> Dict[str, Any]:
        """Ofusca IPs privados nos metadados"""
        def mask_ip(ip: Optional[str]) -> Optional[str]:
            if not ip:
                return ip
            parts = ip.split('.')
            if len(parts) != 4:
                return ip
            try:
                octets = [int(p) for p in parts]
                # RFC 1918 private IPs
                if (octets[0] == 192 and octets[1] == 168) or \
                   (octets[0] == 10) or \
                   (octets[0] == 172 and 16 <= octets[1] <= 31):
                    return f"*.{parts[-1]}"
            except (ValueError, IndexError):
                pass
            return ip
        
        masked_metadata = self.metadata.copy()
        if "src_ip" in masked_metadata:
            masked_metadata["src_ip"] = mask_ip(masked_metadata["src_ip"])
        if "dest_ip" in masked_metadata:
            masked_metadata["dest_ip"] = mask_ip(masked_metadata["dest_ip"])
        return masked_metadata
    
    def is_phishing(self) -> bool:
        """Verifica se o alerta é relacionado a phishing"""
        return self.category == AlertCategory.PHISHING
    
    def is_malware(self) -> bool:
        """Verifica se o alerta é relacionado a malware"""
        return self.category in [
            AlertCategory.MALWARE,
            AlertCategory.VIRUS,
            AlertCategory.TROJAN,
            AlertCategory.RANSOMWARE,
        ]
    
    def is_critical(self) -> bool:
        """Verifica se o alerta é crítico"""
        return self.severity == AlertSeverity.CRITICAL

