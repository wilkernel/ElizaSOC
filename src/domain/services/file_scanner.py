"""
Interface FileScanner - Contrato para serviço de escaneamento de arquivos
"""
from abc import ABC, abstractmethod
from typing import Optional

from ..entities.file_scan import FileScanResult


class FileScanner(ABC):
    """Interface para serviço de escaneamento de arquivos"""
    
    @abstractmethod
    def scan_file(self, filepath: str, quarantine: bool = True) -> FileScanResult:
        """
        Escaneia um arquivo
        
        Args:
            filepath: Caminho do arquivo a escanear
            quarantine: Se True, coloca em quarentena se infectado
            
        Returns:
            FileScanResult: Resultado do escaneamento
        """
        pass
    
    @abstractmethod
    def scan_directory(self, directory: str, recursive: bool = True) -> list[FileScanResult]:
        """
        Escaneia um diretório
        
        Args:
            directory: Diretório a escanear
            recursive: Se True, escaneia recursivamente
            
        Returns:
            Lista de resultados de escaneamento
        """
        pass
    
    @abstractmethod
    def quarantine_file(self, filepath: str) -> bool:
        """
        Coloca arquivo em quarentena
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        pass

