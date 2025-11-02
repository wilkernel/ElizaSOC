"""
Use Case: Response Automation
Caso de uso para resposta automatizada a incidentes
"""
from typing import Dict, Any

from src.domain.services.response_automation import ResponseAutomation
from src.domain.entities.alert import Alert
from src.domain.entities.file_scan import FileScanResult


class ResponseAutomationUseCase:
    """
    Caso de uso para resposta automatizada
    Coordena ações de mitigação
    """
    
    def __init__(self, response_automation: ResponseAutomation):
        """
        Inicializa o caso de uso
        
        Args:
            response_automation: Serviço de resposta automatizada
        """
        self.response_automation = response_automation
    
    def execute_for_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Executa resposta automatizada para um alerta
        
        Args:
            alert: Alerta a processar
            
        Returns:
            Resultado das ações
        """
        return self.response_automation.handle_alert(alert)
    
    def execute_for_file_scan(self, scan_result: FileScanResult) -> bool:
        """
        Executa resposta automatizada para resultado de escaneamento
        
        Args:
            scan_result: Resultado do escaneamento
            
        Returns:
            True se bem-sucedido
        """
        if scan_result.should_quarantine():
            return self.response_automation.quarantine_file_result(scan_result)
        return False

