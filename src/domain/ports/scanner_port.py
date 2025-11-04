"""
ScannerPort - Interface para serviços de escaneamento de arquivos
Seguindo padrão Ports & Adapters (Hexagonal Architecture)
"""
from abc import ABC, abstractmethod
from typing import List

from ..entities.file_scan import FileScanResult


class ScannerPort(ABC):
    """
    Port (interface) para serviço de escaneamento de arquivos
    Define o contrato que adapters devem implementar
    """
    
    @abstractmethod
    def scan(self, filepath: str, quarantine: bool = True) -> dict:
        """
        Escaneia um arquivo
        
        Args:
            filepath: Caminho do arquivo a escanear
            quarantine: Se True, coloca em quarentena se infectado
            
        Returns:
            dict: Resultado do escaneamento com formato padronizado
                {
                    'filepath': str,
                    'infected': bool,
                    'virus_name': Optional[str],
                    'file_size': int,
                    'file_hash': str,
                    'scan_time': str (ISO format),
                    'scanner': str,
                    'quarantined': bool,
                }
        """
        pass
    
    @abstractmethod
    def scan_directory(self, directory: str, recursive: bool = True) -> List[dict]:
        """
        Escaneia um diretório
        
        Args:
            directory: Diretório a escanear
            recursive: Se True, escaneia recursivamente
            
        Returns:
            List[dict]: Lista de resultados de escaneamento
        """
        pass
