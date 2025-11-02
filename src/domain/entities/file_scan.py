"""
Entidade FileScanResult - Representa resultado de escaneamento de arquivo
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class ScanStatus(Enum):
    """Status do escaneamento"""
    CLEAN = "clean"
    INFECTED = "infected"
    SUSPICIOUS = "suspicious"
    ERROR = "error"
    QUARANTINED = "quarantined"


@dataclass
class FileScanResult:
    """
    Entidade FileScanResult - Resultado de escaneamento de arquivo
    
    Atributos:
        id: Identificador único do escaneamento
        filepath: Caminho do arquivo escaneado
        filename: Nome do arquivo
        file_hash: Hash SHA256 do arquivo
        file_size: Tamanho do arquivo em bytes
        status: Status do escaneamento
        threat_name: Nome da ameaça detectada (se houver)
        scanner: Scanner utilizado (ClamAV, VirusTotal, etc)
        scan_time: Data e hora do escaneamento
        quarantined: Se o arquivo foi colocado em quarentena
        quarantine_path: Caminho de quarentena (se aplicável)
        metadata: Metadados adicionais
    """
    id: str
    filepath: str
    filename: str
    file_hash: str
    file_size: int
    status: ScanStatus
    scan_time: datetime
    scanner: str
    threat_name: Optional[str] = None
    quarantined: bool = False
    quarantine_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário"""
        return {
            "id": self.id,
            "filepath": self.filepath,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "status": self.status.value,
            "threat_name": self.threat_name,
            "scanner": self.scanner,
            "scan_time": self.scan_time.isoformat(),
            "quarantined": self.quarantined,
            "quarantine_path": self.quarantine_path,
            "metadata": self.metadata,
        }
    
    def is_infected(self) -> bool:
        """Verifica se o arquivo está infectado"""
        return self.status == ScanStatus.INFECTED
    
    def should_quarantine(self) -> bool:
        """Verifica se o arquivo deve ser colocado em quarentena"""
        return self.is_infected() or self.status == ScanStatus.SUSPICIOUS

