"""
Implementação EventCorrelator - Correlação de eventos de segurança
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.domain.services.event_correlator import EventCorrelator
from src.domain.entities.event import SecurityEvent, EventType
from src.domain.entities.alert import Alert, AlertCategory, AlertSeverity
from src.domain.repositories.event_repository import EventRepository


class SimpleEventCorrelator(EventCorrelator):
    """
    Implementação simples de correlação de eventos
    Segue princípios SOLID e Clean Architecture
    """
    
    def __init__(self, event_repository: EventRepository):
        """
        Inicializa o correlator
        
        Args:
            event_repository: Repositório de eventos
        """
        self.event_repository = event_repository
    
    def correlate_events(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Correlaciona eventos relacionados e gera alertas
        
        Args:
            events: Lista de eventos a correlacionar
            
        Returns:
            Lista de alertas correlacionados
        """
        if not events:
            return []
        
        alerts = []
        
        # Agrupar eventos por critérios de correlação
        correlated_groups = self._group_events(events)
        
        # Gerar alertas para cada grupo correlacionado
        for group in correlated_groups:
            if len(group) > 1:  # Apenas grupos com múltiplos eventos
                alert = self._create_correlated_alert(group)
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _group_events(self, events: List[SecurityEvent]) -> List[List[SecurityEvent]]:
        """
        Agrupa eventos relacionados por IP, tempo, domínio e hash
        
        Args:
            events: Lista de eventos
            
        Returns:
            Lista de grupos de eventos relacionados
        """
        groups = []
        processed = set()
        time_window = timedelta(seconds=300)  # 5 minutos
        
        # Primeiro, agrupar eventos relacionados diretamente
        for event in events:
            if event.id in processed:
                continue
            
            group = [event]
            processed.add(event.id)
            
            # Buscar eventos relacionados diretamente
            for other_event in events:
                if other_event.id in processed:
                    continue
                
                if self._are_related(event, other_event, time_window):
                    group.append(other_event)
                    processed.add(other_event.id)
            
            # Se grupo tem mais de 1 evento, tentar expandir com eventos relacionados indiretamente
            if len(group) > 1:
                # Buscar eventos relacionados aos do grupo (correlação transitiva)
                changed = True
                while changed:
                    changed = False
                    for group_event in group:
                        for other_event in events:
                            if other_event.id in processed:
                                continue
                            if self._are_related(group_event, other_event, time_window):
                                group.append(other_event)
                                processed.add(other_event.id)
                                changed = True
            
            groups.append(group)
        
        return groups
    
    def _are_related(
        self,
        event1: SecurityEvent,
        event2: SecurityEvent,
        time_window: timedelta
    ) -> bool:
        """
        Verifica se dois eventos estão relacionados
        
        Args:
            event1: Primeiro evento
            event2: Segundo evento
            time_window: Janela de tempo máxima
            
        Returns:
            True se relacionados, False caso contrário
        """
        # Verificar janela de tempo
        time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
        if time_diff > time_window.total_seconds():
            return False
        
        # Verificar IPs relacionados
        ip1 = event1.data.get("src_ip") or event1.data.get("dest_ip")
        ip2 = event2.data.get("src_ip") or event2.data.get("dest_ip")
        
        if ip1 and ip2 and ip1 == ip2:
            return True
        
        # Verificar domínios relacionados
        domain1 = event1.data.get("host") or event1.data.get("query")
        domain2 = event2.data.get("host") or event2.data.get("query")
        
        if domain1 and domain2 and domain1 == domain2:
            return True
        
        # Verificar hashes de arquivo relacionados
        hash1 = event1.data.get("file_hash")
        hash2 = event2.data.get("file_hash")
        
        if hash1 and hash2 and hash1.lower() == hash2.lower():
            return True
        
        # Verificar se eventos compartilham o mesmo IP e estão relacionados por tipo
        # (ex: HTTP download + FILE_EXTRACT + FILE_SCAN)
        if ip1 and ip2 and ip1 == ip2:
            # Eventos de download seguidos de scan são relacionados
            if (event1.event_type == EventType.HTTP and event2.event_type == EventType.FILE_EXTRACT) or \
               (event1.event_type == EventType.FILE_EXTRACT and event2.event_type == EventType.FILE_SCAN) or \
               (event1.event_type == EventType.HTTP and event2.event_type == EventType.FILE_SCAN):
                return True
        
        return False
    
    def _create_correlated_alert(self, events: List[SecurityEvent]) -> Alert:
        """
        Cria um alerta a partir de eventos correlacionados
        
        Args:
            events: Grupo de eventos relacionados
            
        Returns:
            Alert correlacionado
        """
        if not events:
            return None
        
        # Determinar categoria e severidade baseado nos eventos
        category, severity, signature = self._analyze_events(events)
        
        # Usar dados do primeiro evento como base
        first_event = events[0]
        data = first_event.data.copy()
        
        # Adicionar informações de correlação
        data["correlated_events"] = [e.id for e in events]
        data["correlation_count"] = len(events)
        
        alert = Alert(
            id=str(uuid.uuid4()),
            timestamp=first_event.timestamp,
            signature=signature,
            category=category,
            severity=severity,
            src_ip=data.get("src_ip"),
            dest_ip=data.get("dest_ip"),
            src_port=data.get("src_port"),
            dest_port=data.get("dest_port"),
            protocol=data.get("proto"),
            metadata=data,
            correlated=True,
        )
        
        return alert
    
    def _analyze_events(
        self,
        events: List[SecurityEvent]
    ) -> tuple:
        """
        Analisa eventos para determinar categoria, severidade e assinatura
        
        Args:
            events: Lista de eventos
            
        Returns:
            Tupla (category, severity, signature)
        """
        # Contar tipos de eventos
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Detectar padrões de phishing
        if any(e.event_type == EventType.ALERT and "PHISHING" in str(e.data.get("signature", "")) for e in events):
            return AlertCategory.PHISHING, AlertSeverity.HIGH, f"Correlated Phishing Campaign ({len(events)} events)"
        
        # Detectar padrões de malware
        # Verificar se algum evento indica arquivo infectado
        has_infected = any(
            (e.event_type == EventType.FILE_SCAN and e.data.get("infected")) or
            (e.event_type == EventType.FILE_SCAN and e.data.get("infected") is True) or
            ("infected" in str(e.data).lower() and "true" in str(e.data.get("infected", "")).lower())
            for e in events
        )
        
        if has_infected:
            return AlertCategory.MALWARE, AlertSeverity.CRITICAL, f"Correlated Malware Detection ({len(events)} events)"
        
        # Detectar padrões de download seguido de extração e scan
        event_types = [e.event_type for e in events]
        if EventType.HTTP in event_types and EventType.FILE_EXTRACT in event_types and EventType.FILE_SCAN in event_types:
            return AlertCategory.MALWARE, AlertSeverity.HIGH, f"Suspicious File Download Pattern ({len(events)} events)"
        
        # Detectar padrões de comunicação C2
        if EventType.DNS in event_types and EventType.HTTP in event_types:
            return AlertCategory.C2_COMMUNICATION, AlertSeverity.HIGH, f"Suspicious C2 Communication Pattern ({len(events)} events)"
        
        # Padrão genérico suspeito
        return AlertCategory.SUSPICIOUS, AlertSeverity.MEDIUM, f"Correlated Suspicious Activity ({len(events)} events)"
    
    def find_related_events(
        self,
        event: SecurityEvent,
        time_window_seconds: int = 300
    ) -> List[SecurityEvent]:
        """
        Encontra eventos relacionados dentro de uma janela de tempo
        
        Args:
            event: Evento de referência
            time_window_seconds: Janela de tempo em segundos
            
        Returns:
            Lista de eventos relacionados
        """
        # Buscar eventos no repositório dentro da janela de tempo
        start_time = event.timestamp - timedelta(seconds=time_window_seconds)
        end_time = event.timestamp + timedelta(seconds=time_window_seconds)
        
        all_events = self.event_repository.find_all(
            limit=1000,
            start_date=start_time,
            end_date=end_time,
        )
        
        # Filtrar eventos relacionados
        related = []
        time_window = timedelta(seconds=time_window_seconds)
        
        for other_event in all_events:
            if other_event.id == event.id:
                continue
            
            if self._are_related(event, other_event, time_window):
                related.append(other_event)
        
        return related

