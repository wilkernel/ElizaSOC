"""
ThreatIntelligencePort - Interface para serviços de Threat Intelligence
Seguindo padrão Ports & Adapters (Hexagonal Architecture)
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime

from ..entities.threat_intelligence import IOC, IOCType


class ThreatIntelligencePort(ABC):
    """
    Port (interface) para serviços de Threat Intelligence
    Define o contrato que adapters devem implementar
    """
    
    @abstractmethod
    def check_ioc(self, ioc_value: str, ioc_type: IOCType) -> Optional[IOC]:
        """
        Verifica reputação de um IOC (Indicator of Compromise)
        
        Args:
            ioc_value: Valor do IOC (IP, domínio, hash, URL)
            ioc_type: Tipo do IOC
            
        Returns:
            IOC se encontrado (indicando ameaça), None se seguro
        """
        pass
    
    @abstractmethod
    def check_multiple_iocs(self, iocs: List[IOC]) -> List[Optional[IOC]]:
        """
        Verifica reputação de múltiplos IOCs
        
        Args:
            iocs: Lista de IOCs para verificar
            
        Returns:
            Lista de IOCs encontrados (None para IOCs seguros)
        """
        pass
    
    @abstractmethod
    def add_ioc(self, ioc: IOC) -> bool:
        """
        Adiciona um IOC à base de conhecimento
        
        Args:
            ioc: IOC a ser adicionado
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        pass
    
    @abstractmethod
    def search_ioc(self, ioc_value: str, ioc_type: Optional[IOCType] = None) -> Optional[IOC]:
        """
        Busca um IOC na base de conhecimento
        
        Args:
            ioc_value: Valor do IOC
            ioc_type: Tipo do IOC (opcional, para busca mais precisa)
            
        Returns:
            IOC encontrado ou None
        """
        pass
    
    @abstractmethod
    def get_threat_info(self, threat_name: str) -> Optional[Dict]:
        """
        Obtém informações sobre uma ameaça conhecida
        
        Args:
            threat_name: Nome da ameaça (ex: "EICAR-Test")
            
        Returns:
            Dicionário com informações da ameaça ou None
        """
        pass
