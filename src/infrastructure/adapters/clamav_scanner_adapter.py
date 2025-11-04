"""
ClamAVScannerAdapter - Adapter que implementa ScannerPort usando ClamAVScanner
Seguindo padrão Ports & Adapters (Hexagonal Architecture)
"""
from typing import List
from datetime import datetime

from src.domain.ports.scanner_port import ScannerPort
from src.infrastructure.scanners.clamav_scanner import ClamAVScanner


class ClamAVScannerAdapter(ScannerPort):
    """
    Adapter que implementa ScannerPort usando ClamAVScanner
    Converte entre a interface FileScanner e ScannerPort
    """
    
    def __init__(self, quarantine_dir: str = None, timeout: int = 300):
        """
        Inicializa o adapter
        
        Args:
            quarantine_dir: Diretório de quarentena
            timeout: Timeout para escaneamento
        """
        self._scanner = ClamAVScanner(quarantine_dir=quarantine_dir, timeout=timeout)
    
    def scan(self, filepath: str, quarantine: bool = True) -> dict:
        """
        Escaneia um arquivo (implementa ScannerPort)
        
        Args:
            filepath: Caminho do arquivo
            quarantine: Se True, coloca em quarentena se infectado
            
        Returns:
            dict: Resultado no formato padronizado
        """
        # Usar o scanner interno
        result = self._scanner.scan_file(filepath, quarantine=quarantine)
        
        # Converter FileScanResult para dict (formato do port)
        return {
            'filepath': result.filepath,
            'filename': result.filename,
            'infected': result.is_infected(),
            'virus_name': result.threat_name,
            'file_size': result.file_size,
            'file_hash': result.file_hash,
            'scan_time': result.scan_time.isoformat() if isinstance(result.scan_time, datetime) else str(result.scan_time),
            'scanner': result.scanner,
            'quarantined': result.quarantined,
        }
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[dict]:
        """
        Escaneia um diretório (implementa ScannerPort)
        
        Args:
            directory: Diretório a escanear
            recursive: Se True, escaneia recursivamente
            
        Returns:
            List[dict]: Lista de resultados
        """
        # Usar o scanner interno
        results = self._scanner.scan_directory(directory, recursive=recursive)
        
        # Converter para lista de dicts
        return [
            {
                'filepath': r.filepath,
                'filename': r.filename,
                'infected': r.is_infected(),
                'virus_name': r.threat_name,
                'file_size': r.file_size,
                'file_hash': r.file_hash,
                'scan_time': r.scan_time.isoformat() if isinstance(r.scan_time, datetime) else str(r.scan_time),
                'scanner': r.scanner,
                'quarantined': r.quarantined,
            }
            for r in results
        ]
