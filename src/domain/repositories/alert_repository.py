"""
Interface AlertRepository - Contrato para repositório de alertas
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.alert import Alert, AlertCategory, AlertSeverity


class AlertRepository(ABC):
    """Interface para repositório de alertas"""
    
    @abstractmethod
    def save(self, alert: Alert) -> Alert:
        """Salva um alerta"""
        pass
    
    @abstractmethod
    def find_by_id(self, alert_id: str) -> Optional[Alert]:
        """Busca alerta por ID"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Alert]:
        """Busca alertas com filtros"""
        pass
    
    @abstractmethod
    def find_by_signature(self, signature: str, limit: int = 100) -> List[Alert]:
        """Busca alertas por assinatura"""
        pass
    
    @abstractmethod
    def find_by_ip(self, ip: str, limit: int = 100) -> List[Alert]:
        """Busca alertas por IP"""
        pass
    
    @abstractmethod
    def count(
        self,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> int:
        """Conta alertas com filtros"""
        pass

