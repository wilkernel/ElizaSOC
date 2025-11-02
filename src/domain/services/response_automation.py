"""
Interface ResponseAutomation - Contrato para serviço de resposta automatizada
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

from ..entities.alert import Alert
from ..entities.file_scan import FileScanResult


class ResponseAutomation(ABC):
    """Interface para serviço de resposta automatizada a incidentes"""
    
    @abstractmethod
    def handle_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Processa resposta automatizada para um alerta
        
        Args:
            alert: Alerta a processar
            
        Returns:
            Dicionário com ações realizadas
        """
        pass
    
    @abstractmethod
    def block_ip(self, ip: str, reason: str) -> bool:
        """
        Bloqueia um IP
        
        Args:
            ip: IP a bloquear
            reason: Razão do bloqueio
            
        Returns:
            True se bem-sucedido
        """
        pass
    
    @abstractmethod
    def block_domain(self, domain: str, reason: str) -> bool:
        """
        Bloqueia um domínio
        
        Args:
            domain: Domínio a bloquear
            reason: Razão do bloqueio
            
        Returns:
            True se bem-sucedido
        """
        pass
    
    @abstractmethod
    def quarantine_file_result(self, scan_result: FileScanResult) -> bool:
        """
        Coloca arquivo em quarentena baseado no resultado do escaneamento
        
        Args:
            scan_result: Resultado do escaneamento
            
        Returns:
            True se bem-sucedido
        """
        pass
    
    @abstractmethod
    def isolate_endpoint(self, endpoint_id: str, reason: str) -> bool:
        """
        Isola um endpoint da rede
        
        Args:
            endpoint_id: Identificador do endpoint
            reason: Razão do isolamento
            
        Returns:
            True se bem-sucedido
        """
        pass

