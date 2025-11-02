"""
Use Case: Scan File
Implementa o caso de uso de escaneamento de arquivo seguindo Clean Architecture
"""
from typing import Optional

from src.domain.services.file_scanner import FileScanner
from src.domain.repositories.file_scan_repository import FileScanRepository
from src.domain.entities.file_scan import FileScanResult


class ScanFileUseCase:
    """
    Caso de uso para escaneamento de arquivo
    Coordena o scanner e o repositório
    """
    
    def __init__(
        self,
        file_scanner: FileScanner,
        file_scan_repository: FileScanRepository,
    ):
        """
        Inicializa o caso de uso
        
        Args:
            file_scanner: Serviço de escaneamento
            file_scan_repository: Repositório de escaneamentos
        """
        self.file_scanner = file_scanner
        self.file_scan_repository = file_scan_repository
    
    def execute(self, filepath: str, quarantine: bool = True) -> FileScanResult:
        """
        Executa o escaneamento de arquivo
        
        Args:
            filepath: Caminho do arquivo
            quarantine: Se True, coloca em quarentena se infectado
            
        Returns:
            FileScanResult: Resultado do escaneamento
        """
        # Escanear arquivo
        scan_result = self.file_scanner.scan_file(filepath, quarantine=quarantine)
        
        # Salvar resultado no repositório
        saved_result = self.file_scan_repository.save(scan_result)
        
        return saved_result
    
    def execute_directory(self, directory: str, recursive: bool = True) -> list[FileScanResult]:
        """
        Executa escaneamento de diretório
        
        Args:
            directory: Diretório a escanear
            recursive: Se True, escaneia recursivamente
            
        Returns:
            Lista de resultados
        """
        # Escanear diretório
        scan_results = self.file_scanner.scan_directory(directory, recursive=recursive)
        
        # Salvar todos os resultados
        saved_results = []
        for result in scan_results:
            saved_result = self.file_scan_repository.save(result)
            saved_results.append(saved_result)
        
        return saved_results

