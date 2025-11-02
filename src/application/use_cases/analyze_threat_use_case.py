"""
Use Case: Analyze Threat
Caso de uso para análise de ameaças com Threat Intelligence
"""
from typing import Optional, Dict, Any

from src.domain.services.threat_intelligence_service import ThreatIntelligenceService
from src.domain.entities.threat_intelligence import IOC
from src.domain.entities.alert import Alert


class AnalyzeThreatUseCase:
    """
    Caso de uso para análise de ameaças
    Enriquece alertas com informações de Threat Intelligence
    """
    
    def __init__(self, threat_intelligence_service: ThreatIntelligenceService):
        """
        Inicializa o caso de uso
        
        Args:
            threat_intelligence_service: Serviço de Threat Intelligence
        """
        self.threat_intelligence_service = threat_intelligence_service
    
    def execute(self, alert: Alert) -> Alert:
        """
        Enriquece alerta com informações de Threat Intelligence
        
        Args:
            alert: Alerta a enriquecer
            
        Returns:
            Alerta enriquecido
        """
        # Converter alerta para dict
        alert_dict = alert.to_dict()
        
        # Enriquecer com Threat Intelligence
        enriched = self.threat_intelligence_service.enrich_alert_with_ioc(alert_dict)
        
        # Atualizar metadados do alerta
        alert.metadata.update(enriched.get("metadata", {}))
        if "threat_intel" in enriched:
            alert.metadata["threat_intel"] = enriched["threat_intel"]
        
        return alert
    
    def check_ip(self, ip: str) -> Optional[IOC]:
        """
        Verifica IP contra Threat Intelligence
        
        Args:
            ip: IP a verificar
            
        Returns:
            IOC se encontrado
        """
        return self.threat_intelligence_service.check_ip(ip)
    
    def check_domain(self, domain: str) -> Optional[IOC]:
        """
        Verifica domínio contra Threat Intelligence
        
        Args:
            domain: Domínio a verificar
            
        Returns:
            IOC se encontrado
        """
        return self.threat_intelligence_service.check_domain(domain)
    
    def check_hash(self, file_hash: str) -> Optional[IOC]:
        """
        Verifica hash contra Threat Intelligence
        
        Args:
            file_hash: Hash a verificar
            
        Returns:
            IOC se encontrado
        """
        return self.threat_intelligence_service.check_hash(file_hash)

