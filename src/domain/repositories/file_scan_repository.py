"""
Interface FileScanRepository - Contrato para repositório de escaneamentos
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.file_scan import FileScanResult, ScanStatus


class FileScanRepository(ABC):
    """Interface para repositório de escaneamentos de arquivos"""
    
    @abstractmethod
    def save(self, scan_result: FileScanResult) -> FileScanResult:
        """Salva resultado de escaneamento"""
        pass
    
    @abstractmethod
    def find_by_id(self, scan_id: str) -> Optional[FileScanResult]:
        """Busca escaneamento por ID"""
        pass
    
    @abstractmethod
    def find_by_hash(self, file_hash: str) -> List[FileScanResult]:
        """Busca escaneamentos por hash do arquivo"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[ScanStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[FileScanResult]:
        """Busca escaneamentos com filtros"""
        pass
    
    @abstractmethod
    def find_infected(self, limit: int = 100) -> List[FileScanResult]:
        """Busca apenas arquivos infectados"""
        pass

