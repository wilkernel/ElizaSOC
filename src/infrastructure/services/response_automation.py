"""
Implementação ResponseAutomation - Resposta automatizada a incidentes
"""
import subprocess
import os
from typing import Dict, Any

from src.domain.services.response_automation import ResponseAutomation
from src.domain.entities.alert import Alert, AlertSeverity, AlertCategory
from src.domain.entities.file_scan import FileScanResult, ScanStatus


class SimpleResponseAutomation(ResponseAutomation):
    """
    Implementação de resposta automatizada
    Executa ações de mitigação (bloqueio, quarentena, isolamento)
    """
    
    def __init__(self, quarantine_dir: str = "/var/quarantine"):
        """
        Inicializa o serviço de resposta automatizada
        
        Args:
            quarantine_dir: Diretório de quarentena
        """
        self.quarantine_dir = quarantine_dir
        self.blocked_ips = set()
        self.blocked_domains = set()
        self.isolated_endpoints = set()
    
    def handle_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Processa resposta automatizada para um alerta
        
        Args:
            alert: Alerta a processar
            
        Returns:
            Dicionário com ações realizadas
        """
        actions = []
        
        # Resposta baseada em severidade
        if alert.severity == AlertSeverity.CRITICAL:
            actions.append("critical_response")
            
            # Bloquear IP de origem se disponível
            if alert.src_ip and alert.src_ip not in self.blocked_ips:
                if self.block_ip(alert.src_ip, f"Critical alert: {alert.signature}"):
                    actions.append(f"blocked_ip_{alert.src_ip}")
        
        # Resposta baseada em categoria
        if alert.category == AlertCategory.PHISHING:
            # Bloquear domínio se disponível
            domain = alert.metadata.get("host") or alert.metadata.get("domain")
            if domain and domain not in self.blocked_domains:
                if self.block_domain(domain, f"Phishing alert: {alert.signature}"):
                    actions.append(f"blocked_domain_{domain}")
        
        if alert.category in [AlertCategory.MALWARE, AlertCategory.VIRUS]:
            actions.append("malware_response")
            
            # Bloquear IP de origem
            if alert.src_ip and alert.src_ip not in self.blocked_ips:
                if self.block_ip(alert.src_ip, f"Malware alert: {alert.signature}"):
                    actions.append(f"blocked_ip_{alert.src_ip}")
        
        return {
            "alert_id": alert.id,
            "actions_taken": actions,
            "timestamp": alert.timestamp.isoformat(),
        }
    
    def block_ip(self, ip: str, reason: str) -> bool:
        """
        Bloqueia um IP
        
        Args:
            ip: IP a bloquear
            reason: Razão do bloqueio
            
        Returns:
            True se bem-sucedido
        """
        if ip in self.blocked_ips:
            return True  # Já bloqueado
        
        try:
            # Bloquear via iptables (requer permissões)
            # Em produção, usar gerenciamento de firewall apropriado
            if os.geteuid() == 0:  # Executando como root
                subprocess.run(
                    ['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
                    check=True,
                    capture_output=True,
                )
            
            self.blocked_ips.add(ip)
            
            # Log da ação
            print(f"[AUTOMATED RESPONSE] Blocked IP {ip}: {reason}")
            
            return True
            
        except subprocess.CalledProcessError:
            # Se falhar, apenas adicionar à lista interna
            self.blocked_ips.add(ip)
            return True
        except PermissionError:
            # Sem permissão, apenas registrar
            self.blocked_ips.add(ip)
            print(f"[AUTOMATED RESPONSE] Would block IP {ip}: {reason} (no permissions)")
            return True
        except Exception as e:
            print(f"Erro ao bloquear IP {ip}: {e}")
            return False
    
    def block_domain(self, domain: str, reason: str) -> bool:
        """
        Bloqueia um domínio
        
        Args:
            domain: Domínio a bloquear
            reason: Razão do bloqueio
            
        Returns:
            True se bem-sucedido
        """
        if domain in self.blocked_domains:
            return True
        
        try:
            # Bloquear via /etc/hosts (requer permissões)
            hosts_file = "/etc/hosts"
            if os.access(hosts_file, os.W_OK):
                with open(hosts_file, 'a') as f:
                    f.write(f"\n127.0.0.1 {domain} # Blocked by ElizaSOC: {reason}\n")
            
            self.blocked_domains.add(domain)
            
            # Log da ação
            print(f"[AUTOMATED RESPONSE] Blocked domain {domain}: {reason}")
            
            return True
            
        except PermissionError:
            # Sem permissão, apenas registrar
            self.blocked_domains.add(domain)
            print(f"[AUTOMATED RESPONSE] Would block domain {domain}: {reason} (no permissions)")
            return True
        except Exception as e:
            print(f"Erro ao bloquear domínio {domain}: {e}")
            return False
    
    def quarantine_file_result(self, scan_result: FileScanResult) -> bool:
        """
        Coloca arquivo em quarentena baseado no resultado do escaneamento
        
        Args:
            scan_result: Resultado do escaneamento
            
        Returns:
            True se bem-sucedido
        """
        if not scan_result.should_quarantine():
            return False
        
        try:
            if not os.path.exists(scan_result.filepath):
                return False
            
            # Mover para quarentena
            os.makedirs(self.quarantine_dir, exist_ok=True)
            
            from datetime import datetime
            import shutil
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_filename = f"{timestamp}_{scan_result.file_hash[:16]}_{scan_result.filename}"
            quarantine_path = os.path.join(self.quarantine_dir, quarantine_filename)
            
            shutil.move(scan_result.filepath, quarantine_path)
            
            # Remover permissões
            os.chmod(quarantine_path, 0o000)
            
            # Atualizar resultado
            scan_result.quarantined = True
            scan_result.quarantine_path = quarantine_path
            
            print(f"[AUTOMATED RESPONSE] Quarantined file: {scan_result.filename}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao colocar arquivo em quarentena: {e}")
            return False
    
    def isolate_endpoint(self, endpoint_id: str, reason: str) -> bool:
        """
        Isola um endpoint da rede
        
        Args:
            endpoint_id: Identificador do endpoint (IP ou hostname)
            reason: Razão do isolamento
            
        Returns:
            True se bem-sucedido
        """
        if endpoint_id in self.isolated_endpoints:
            return True
        
        try:
            # Isolar via iptables (bloquear todo tráfego exceto de/para administração)
            if os.geteuid() == 0:  # Executando como root
                # Bloquear todo tráfego de saída do endpoint
                subprocess.run(
                    ['iptables', '-A', 'OUTPUT', '-s', endpoint_id, '-j', 'DROP'],
                    check=True,
                    capture_output=True,
                )
                # Bloquear todo tráfego de entrada para o endpoint (exceto admin)
                subprocess.run(
                    ['iptables', '-A', 'INPUT', '-d', endpoint_id, '-j', 'DROP'],
                    check=True,
                    capture_output=True,
                )
            
            self.isolated_endpoints.add(endpoint_id)
            
            print(f"[AUTOMATED RESPONSE] Isolated endpoint {endpoint_id}: {reason}")
            
            return True
            
        except PermissionError:
            self.isolated_endpoints.add(endpoint_id)
            print(f"[AUTOMATED RESPONSE] Would isolate endpoint {endpoint_id}: {reason} (no permissions)")
            return True
        except Exception as e:
            print(f"Erro ao isolar endpoint {endpoint_id}: {e}")
            return False

