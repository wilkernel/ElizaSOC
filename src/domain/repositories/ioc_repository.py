"""
Interface IOCRepository - Contrato para repositório de IOCs
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.threat_intelligence import IOC, IOCType, IOCSource


class IOCRepository(ABC):
    """Interface para repositório de IOCs (Indicadores de Comprometimento)"""
    
    @abstractmethod
    def save(self, ioc: IOC) -> IOC:
        """Salva um IOC"""
        pass
    
    @abstractmethod
    def find_by_id(self, ioc_id: str) -> Optional[IOC]:
        """Busca IOC por ID"""
        pass
    
    @abstractmethod
    def find_by_value(self, value: str) -> List[IOC]:
        """Busca IOCs por valor"""
        pass
    
    @abstractmethod
    def find_by_type(self, ioc_type: IOCType, limit: int = 100) -> List[IOC]:
        """Busca IOCs por tipo"""
        pass
    
    @abstractmethod
    def find_active(self) -> List[IOC]:
        """Busca apenas IOCs ativos"""
        pass
    
    @abstractmethod
    def match_ioc(self, value: str, ioc_type: IOCType) -> Optional[IOC]:
        """Verifica se um valor corresponde a algum IOC"""
        pass

