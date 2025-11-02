"""
Implementação In-Memory do IOCRepository
Para uso em testes e desenvolvimento
"""
from typing import List, Optional

from src.domain.repositories.ioc_repository import IOCRepository
from src.domain.entities.threat_intelligence import IOC, IOCType, IOCSource


class InMemoryIOCRepository(IOCRepository):
    """Implementação in-memory do repositório de IOCs"""
    
    def __init__(self):
        """Inicializa repositório vazio"""
        self._iocs: dict[str, IOC] = {}
    
    def save(self, ioc: IOC) -> IOC:
        """Salva um IOC"""
        self._iocs[ioc.id] = ioc
        return ioc
    
    def find_by_id(self, ioc_id: str) -> Optional[IOC]:
        """Busca IOC por ID"""
        return self._iocs.get(ioc_id)
    
    def find_by_value(self, value: str) -> List[IOC]:
        """Busca IOCs por valor"""
        return [
            ioc for ioc in self._iocs.values()
            if ioc.value.lower() == value.lower()
        ]
    
    def find_by_type(self, ioc_type: IOCType, limit: int = 100) -> List[IOC]:
        """Busca IOCs por tipo"""
        results = [
            ioc for ioc in self._iocs.values()
            if ioc.ioc_type == ioc_type
        ]
        return results[:limit]
    
    def find_active(self) -> List[IOC]:
        """Busca apenas IOCs ativos"""
        return [
            ioc for ioc in self._iocs.values()
            if ioc.active
        ]
    
    def match_ioc(self, value: str, ioc_type: IOCType) -> Optional[IOC]:
        """Verifica se um valor corresponde a algum IOC"""
        for ioc in self._iocs.values():
            if ioc.ioc_type == ioc_type and ioc.matches(value) and ioc.active:
                return ioc
        return None
    
    def clear(self) -> None:
        """Limpa todos os IOCs (útil para testes)"""
        self._iocs.clear()

