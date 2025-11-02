"""
Implementação In-Memory do AlertRepository
Para uso em testes e desenvolvimento
"""
from typing import List, Optional
from datetime import datetime

from src.domain.repositories.alert_repository import AlertRepository
from src.domain.entities.alert import Alert, AlertCategory, AlertSeverity


class InMemoryAlertRepository(AlertRepository):
    """Implementação in-memory do repositório de alertas"""
    
    def __init__(self):
        """Inicializa repositório vazio"""
        self._alerts: dict[str, Alert] = {}
    
    def save(self, alert: Alert) -> Alert:
        """Salva um alerta"""
        self._alerts[alert.id] = alert
        return alert
    
    def find_by_id(self, alert_id: str) -> Optional[Alert]:
        """Busca alerta por ID"""
        return self._alerts.get(alert_id)
    
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
        results = list(self._alerts.values())
        
        # Aplicar filtros
        if category:
            results = [r for r in results if r.category == category]
        
        if severity:
            results = [r for r in results if r.severity == severity]
        
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]
        
        # Ordenar por timestamp (mais recentes primeiro)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Aplicar paginação
        return results[offset:offset + limit]
    
    def find_by_signature(self, signature: str, limit: int = 100) -> List[Alert]:
        """Busca alertas por assinatura"""
        results = [
            alert for alert in self._alerts.values()
            if signature.lower() in alert.signature.lower()
        ]
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def find_by_ip(self, ip: str, limit: int = 100) -> List[Alert]:
        """Busca alertas por IP"""
        results = [
            alert for alert in self._alerts.values()
            if alert.src_ip == ip or alert.dest_ip == ip
        ]
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def count(
        self,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> int:
        """Conta alertas com filtros"""
        results = list(self._alerts.values())
        
        if category:
            results = [r for r in results if r.category == category]
        
        if severity:
            results = [r for r in results if r.severity == severity]
        
        return len(results)
    
    def clear(self) -> None:
        """Limpa todos os alertas (útil para testes)"""
        self._alerts.clear()

