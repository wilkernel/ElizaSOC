"""
Interface ThreatIntelligenceService - Contrato para serviço de Threat Intelligence
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.threat_intelligence import IOC, IOCType


class ThreatIntelligenceService(ABC):
    """Interface para serviço de Threat Intelligence"""
    
    @abstractmethod
    def check_ip(self, ip: str) -> Optional[IOC]:
        """
        Verifica reputação de um IP
        
        Args:
            ip: Endereço IP a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def check_domain(self, domain: str) -> Optional[IOC]:
        """
        Verifica reputação de um domínio
        
        Args:
            domain: Domínio a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def check_hash(self, file_hash: str) -> Optional[IOC]:
        """
        Verifica hash de arquivo
        
        Args:
            file_hash: Hash SHA256 do arquivo
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def check_url(self, url: str) -> Optional[IOC]:
        """
        Verifica URL
        
        Args:
            url: URL a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def update_feeds(self) -> int:
        """
        Atualiza feeds de Threat Intelligence
        
        Returns:
            Número de IOCs atualizados
        """
        pass

