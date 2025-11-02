"""
Implementação BehavioralAnalyzer - Análise comportamental e detecção de anomalias
Usa machine learning para detectar padrões anômalos e zero-day
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

from src.domain.services.behavioral_analyzer import BehavioralAnalyzer
from src.domain.entities.event import SecurityEvent, EventType
from src.domain.entities.alert import Alert, AlertCategory, AlertSeverity
from src.domain.repositories.event_repository import EventRepository

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    IsolationForest = None
    StandardScaler = None
    np = None


class SimpleBehavioralAnalyzer(BehavioralAnalyzer):
    """
    Implementação de análise comportamental
    Usa Isolation Forest para detecção de anomalias
    """
    
    def __init__(self, event_repository: EventRepository):
        """
        Inicializa o analisador comportamental
        
        Args:
            event_repository: Repositório de eventos para análise histórica
        """
        self.event_repository = event_repository
        self.model = None
        if ML_AVAILABLE:
            self.scaler = StandardScaler()
        else:
            self.scaler = None
        self.is_trained = False
    
    def analyze_events(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Analisa eventos para detectar comportamentos anômalos
        
        Args:
            events: Lista de eventos a analisar
            
        Returns:
            Lista de alertas gerados por anomalias
        """
        if not events:
            return []
        
        alerts = []
        
        # 1. Análise de frequência (detecção de DDoS, scans)
        frequency_alerts = self._detect_frequency_anomalies(events)
        alerts.extend(frequency_alerts)
        
        # 2. Análise de padrões (domínios suspeitos, portas incomuns)
        pattern_alerts = self._detect_pattern_anomalies(events)
        alerts.extend(pattern_alerts)
        
        # 3. Análise ML (se modelo treinado)
        if self.is_trained and ML_AVAILABLE:
            ml_alerts = self._detect_ml_anomalies(events)
            alerts.extend(ml_alerts)
        
        return alerts
    
    def detect_zero_day(self, event: SecurityEvent) -> bool:
        """
        Detecta possível ameaça zero-day
        
        Args:
            event: Evento a analisar
            
        Returns:
            True se possível zero-day, False caso contrário
        """
        # Critérios para zero-day:
        # 1. Assinatura desconhecida/novel
        # 2. Padrão nunca visto antes
        # 3. Comportamento semelhante a ameaças conhecidas mas não detectado
        
        signature = str(event.data.get("signature", "")).upper()
        
        # Verificar se assinatura indica padrão desconhecido
        unknown_keywords = ["UNKNOWN", "NEW", "SUSPICIOUS", "UNUSUAL"]
        if any(keyword in signature for keyword in unknown_keywords):
            # Verificar histórico - nunca visto antes?
            historical = self.event_repository.find_all(
                limit=1000,
                start_date=event.timestamp - timedelta(days=30),
            )
            
            # Se nenhum evento similar no histórico, possível zero-day
            similar_count = sum(
                1 for h in historical
                if h.event_type == event.event_type
                and abs((h.timestamp - event.timestamp).total_seconds()) < 3600
            )
            
            if similar_count == 0:
                return True
        
        return False
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> None:
        """
        Treina modelo de machine learning
        
        Args:
            training_data: Dados de treinamento
        """
        if not ML_AVAILABLE:
            return
        
        if not training_data:
            return
        
        try:
            # Extrair features
            X = []
            for sample in training_data:
                features = []
                # Features numéricas
                for key in sorted(sample.keys()):
                    if key != "label" and isinstance(sample[key], (int, float)):
                        features.append(float(sample[key]))
                if features:
                    X.append(features)
            
            if not X:
                return
            
            X = np.array(X)
            
            # Normalizar features
            if self.scaler is None:
                self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Treinar Isolation Forest
            self.model = IsolationForest(
                contamination=0.1,  # Espera 10% de anomalias
                random_state=42,
                n_estimators=100,
            )
            self.model.fit(X_scaled)
            self.is_trained = True
            
        except Exception as e:
            # Em caso de erro, continuar sem ML
            print(f"Erro ao treinar modelo: {e}")
            self.is_trained = False
    
    def _detect_frequency_anomalies(self, events: List[SecurityEvent]) -> List[Alert]:
        """Detecta anomalias de frequência (DDoS, port scans, etc)"""
        alerts = []
        
        if len(events) < 10:
            return alerts
        
        # Agrupar eventos por IP e janela de tempo
        ip_counter = Counter()
        time_windows = {}
        
        for event in events:
            src_ip = event.data.get("src_ip")
            if src_ip:
                ip_counter[src_ip] += 1
                
                # Janela de 1 minuto
                window_key = (src_ip, event.timestamp.replace(second=0, microsecond=0))
                time_windows[window_key] = time_windows.get(window_key, 0) + 1
        
        # Detectar IPs com alta frequência (possível ataque)
        for ip, count in ip_counter.items():
            if count > 50:  # Threshold configurável
                alert = Alert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    signature=f"High frequency activity from {ip} ({count} events)",
                    category=AlertCategory.SUSPICIOUS,
                    severity=AlertSeverity.HIGH,
                    src_ip=ip,
                    metadata={
                        "event_count": count,
                        "anomaly_type": "frequency",
                        "related_events": [e.id for e in events if e.data.get("src_ip") == ip],
                    },
                    correlated=False,
                )
                alerts.append(alert)
        
        # Detectar janelas de tempo com alta atividade
        for (ip, window_time), count in time_windows.items():
            if count > 20:  # Muitos eventos em 1 minuto
                alert = Alert(
                    id=str(uuid.uuid4()),
                    timestamp=window_time,
                    signature=f"Burst activity from {ip} ({count} events/min)",
                    category=AlertCategory.SUSPICIOUS,
                    severity=AlertSeverity.MEDIUM,
                    src_ip=ip,
                    metadata={
                        "events_per_minute": count,
                        "anomaly_type": "burst",
                    },
                    correlated=False,
                )
                alerts.append(alert)
        
        return alerts
    
    def _detect_pattern_anomalies(self, events: List[SecurityEvent]) -> List[Alert]:
        """Detecta anomalias de padrão (domínios suspeitos, portas incomuns)"""
        alerts = []
        
        # Portas comuns (HTTP, HTTPS, SSH, DNS, etc)
        common_ports = {80, 443, 22, 53, 25, 587, 993, 995, 3306, 5432}
        
        for event in events:
            # Detectar portas não usuais
            dest_port = event.data.get("dest_port")
            if dest_port and dest_port not in common_ports and 1 <= dest_port <= 65535:
                # Porta não comum pode ser suspeita
                if dest_port in {4444, 5555, 6666, 31337, 12345}:  # Portas conhecidamente suspeitas
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        timestamp=event.timestamp,
                        signature=f"Connection to unusual port {dest_port}",
                        category=AlertCategory.SUSPICIOUS,
                        severity=AlertSeverity.MEDIUM,
                        src_ip=event.data.get("src_ip"),
                        dest_port=dest_port,
                        metadata={
                            "unusual_port": dest_port,
                            "anomaly_type": "unusual_port",
                            "event_id": event.id,
                        },
                        correlated=False,
                    )
                    alerts.append(alert)
            
            # Detectar domínios com padrões suspeitos
            host = event.data.get("host") or event.data.get("query")
            if host and self._is_suspicious_domain(host):
                alert = Alert(
                    id=str(uuid.uuid4()),
                    timestamp=event.timestamp,
                    signature=f"Suspicious domain pattern: {host}",
                    category=AlertCategory.PHISHING,
                    severity=AlertSeverity.HIGH,
                    metadata={
                        "suspicious_domain": host,
                        "anomaly_type": "domain_pattern",
                        "event_id": event.id,
                    },
                    correlated=False,
                )
                alerts.append(alert)
        
        return alerts
    
    def _detect_ml_anomalies(self, events: List[SecurityEvent]) -> List[Alert]:
        """Detecta anomalias usando modelo ML"""
        alerts = []
        
        if not self.model or not self.is_trained:
            return alerts
        
        try:
            # Extrair features dos eventos
            features_list = []
            for event in events:
                features = self._extract_features(event)
                if features:
                    features_list.append((event, features))
            
            if not features_list:
                return alerts
            
            # Preparar dados
            X = np.array([f for _, f in features_list])
            if self.scaler is None:
                return alerts
            X_scaled = self.scaler.transform(X)
            
            # Predizer anomalias
            predictions = self.model.predict(X_scaled)
            
            # Criar alertas para anomalias detectadas
            for (event, _), prediction in zip(features_list, predictions):
                if prediction == -1:  # -1 = anomalia, 1 = normal
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        timestamp=event.timestamp,
                        signature="ML-detected behavioral anomaly",
                        category=AlertCategory.SUSPICIOUS,
                        severity=AlertSeverity.MEDIUM,
                        src_ip=event.data.get("src_ip"),
                        metadata={
                            "anomaly_type": "ml_behavioral",
                            "event_id": event.id,
                            "ml_confidence": "high",
                        },
                        correlated=False,
                    )
                    alerts.append(alert)
        
        except Exception as e:
            # Em caso de erro, não gerar alertas
            print(f"Erro na detecção ML: {e}")
        
        return alerts
    
    def _extract_features(self, event: SecurityEvent) -> Optional[List[float]]:
        """Extrai features numéricas de um evento"""
        features = []
        
        # Feature 1: Porta de destino (se disponível)
        dest_port = event.data.get("dest_port", 0)
        features.append(float(dest_port))
        
        # Feature 2: Comprimento do hostname/URL
        host = event.data.get("host") or event.data.get("query") or ""
        features.append(float(len(host)))
        
        # Feature 3: Número de pontos no domínio
        features.append(float(host.count('.')))
        
        # Feature 4: Timestamp como feature (hora do dia)
        hour = event.timestamp.hour
        features.append(float(hour))
        
        return features if features else None
    
    def _is_suspicious_domain(self, domain: str) -> bool:
        """Verifica se domínio tem padrão suspeito"""
        if not domain:
            return False
        
        domain_lower = domain.lower()
        
        # Padrões suspeitos
        suspicious_patterns = [
            len(domain) > 50,  # Domínios muito longos
            domain.count('.') > 5,  # Muitos subdomínios
            any(c.isdigit() for c in domain.split('.')[0]),  # Números no início
            'typo' in domain_lower or 'phish' in domain_lower,  # Palavras-chave
        ]
        
        return any(suspicious_patterns)

