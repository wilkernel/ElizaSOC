"""
Interface BehavioralAnalyzer - Contrato para serviço de análise comportamental
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..entities.event import SecurityEvent
from ..entities.alert import Alert


class BehavioralAnalyzer(ABC):
    """Interface para serviço de análise comportamental e detecção de anomalias"""
    
    @abstractmethod
    def analyze_events(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Analisa eventos para detectar comportamentos anômalos
        
        Args:
            events: Lista de eventos a analisar
            
        Returns:
            Lista de alertas gerados por anomalias
        """
        pass
    
    @abstractmethod
    def detect_zero_day(self, event: SecurityEvent) -> bool:
        """
        Detecta possível ameaça zero-day
        
        Args:
            event: Evento a analisar
            
        Returns:
            True se possível zero-day, False caso contrário
        """
        pass
    
    @abstractmethod
    def train_model(self, training_data: List[Dict[str, Any]]) -> None:
        """
        Treina modelo de machine learning
        
        Args:
            training_data: Dados de treinamento
        """
        pass

