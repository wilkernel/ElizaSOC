"""
Implementação ThreatIntelligenceService - Serviço de Threat Intelligence
"""
import re
from typing import Optional
from datetime import datetime

from src.domain.services.threat_intelligence_service import ThreatIntelligenceService
from src.domain.entities.threat_intelligence import IOC, IOCType, IOCSource
from src.domain.repositories.ioc_repository import IOCRepository


class SimpleThreatIntelligenceService(ThreatIntelligenceService):
    """
    Implementação simples de Threat Intelligence Service
    Valida contra IOCs armazenados no repositório
    """
    
    def __init__(self, ioc_repository: IOCRepository):
        """
        Inicializa o serviço
        
        Args:
            ioc_repository: Repositório de IOCs
        """
        self.ioc_repository = ioc_repository
    
    def check_ip(self, ip: str) -> Optional[IOC]:
        """
        Verifica reputação de um IP
        
        Args:
            ip: Endereço IP a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        return self.ioc_repository.match_ioc(ip, IOCType.IP)
    
    def check_domain(self, domain: str) -> Optional[IOC]:
        """
        Verifica reputação de um domínio
        
        Args:
            domain: Domínio a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        # Normalizar domínio (remover http/https, www, etc)
        normalized = self._normalize_domain(domain)
        return self.ioc_repository.match_ioc(normalized, IOCType.DOMAIN)
    
    def check_hash(self, file_hash: str) -> Optional[IOC]:
        """
        Verifica hash de arquivo
        
        Args:
            file_hash: Hash SHA256 do arquivo
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        return self.ioc_repository.match_ioc(file_hash.lower(), IOCType.HASH)
    
    def check_url(self, url: str) -> Optional[IOC]:
        """
        Verifica URL
        
        Args:
            url: URL a verificar
            
        Returns:
            IOC se encontrado, None caso contrário
        """
        # Extrair domínio da URL
        domain = self._extract_domain_from_url(url)
        if domain:
            result = self.check_domain(domain)
            if result:
                return result
        
        # Verificar URL completa
        return self.ioc_repository.match_ioc(url, IOCType.URL)
    
    def update_feeds(self) -> int:
        """
        Atualiza feeds de Threat Intelligence
        
        Por enquanto, apenas retorna 0.
        Em implementação futura, irá buscar de feeds externos.
        
        Returns:
            Número de IOCs atualizados
        """
        # TODO: Implementar atualização de feeds externos
        # - Abuse.ch APIs
        # - AlienVault OTX
        # - VirusTotal
        # - Emerging Threats
        
        return 0
    
    def _normalize_domain(self, domain: str) -> str:
        """
        Normaliza domínio para comparação
        
        Args:
            domain: Domínio a normalizar
            
        Returns:
            Domínio normalizado
        """
        # Remover protocolo
        domain = re.sub(r'^https?://', '', domain)
        # Remover www
        domain = re.sub(r'^www\.', '', domain)
        # Remover porta
        domain = re.sub(r':\d+$', '', domain)
        # Remover caminho
        domain = domain.split('/')[0]
        # Converter para minúsculas
        domain = domain.lower().strip()
        
        return domain
    
    def _extract_domain_from_url(self, url: str) -> Optional[str]:
        """
        Extrai domínio de uma URL
        
        Args:
            url: URL completa
            
        Returns:
            Domínio extraído ou None
        """
        try:
            # Regex simples para extrair domínio
            match = re.match(r'https?://([^/]+)', url)
            if match:
                return self._normalize_domain(match.group(1))
            
            # Se não tem protocolo, assume que já é um domínio
            if '/' in url:
                return self._normalize_domain(url.split('/')[0])
            
            return self._normalize_domain(url)
        except Exception:
            return None
    
    def enrich_alert_with_ioc(self, alert_data: dict) -> dict:
        """
        Enriquece dados de alerta com informações de Threat Intelligence
        
        Args:
            alert_data: Dados do alerta
            
        Returns:
            Dados do alerta enriquecidos
        """
        enriched = alert_data.copy()
        
        # Verificar IP de origem
        src_ip = alert_data.get("src_ip")
        if src_ip:
            ioc = self.check_ip(src_ip)
            if ioc:
                enriched["threat_intel"] = {
                    "ioc_id": ioc.id,
                    "ioc_type": ioc.ioc_type.value,
                    "threat_type": ioc.threat_type,
                    "confidence": ioc.confidence,
                    "source": ioc.source.value,
                }
        
        # Verificar IP de destino
        dest_ip = alert_data.get("dest_ip")
        if dest_ip and "threat_intel" not in enriched:
            ioc = self.check_ip(dest_ip)
            if ioc:
                enriched["threat_intel"] = {
                    "ioc_id": ioc.id,
                    "ioc_type": ioc.ioc_type.value,
                    "threat_type": ioc.threat_type,
                    "confidence": ioc.confidence,
                    "source": ioc.source.value,
                }
        
        # Verificar domínio se houver
        host = alert_data.get("host") or alert_data.get("domain")
        if host:
            ioc = self.check_domain(host)
            if ioc and "threat_intel" not in enriched:
                enriched["threat_intel"] = {
                    "ioc_id": ioc.id,
                    "ioc_type": ioc.ioc_type.value,
                    "threat_type": ioc.threat_type,
                    "confidence": ioc.confidence,
                    "source": ioc.source.value,
                }
        
        return enriched

