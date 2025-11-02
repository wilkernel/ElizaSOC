"""
Implementação In-Memory do FileScanRepository
Para uso em testes e desenvolvimento
"""
from typing import List, Optional
from datetime import datetime

from src.domain.repositories.file_scan_repository import FileScanRepository
from src.domain.entities.file_scan import FileScanResult, ScanStatus


class InMemoryFileScanRepository(FileScanRepository):
    """Implementação in-memory do repositório de escaneamentos"""
    
    def __init__(self):
        """Inicializa repositório vazio"""
        self._scans: dict[str, FileScanResult] = {}
    
    def save(self, scan_result: FileScanResult) -> FileScanResult:
        """Salva resultado de escaneamento"""
        self._scans[scan_result.id] = scan_result
        return scan_result
    
    def find_by_id(self, scan_id: str) -> Optional[FileScanResult]:
        """Busca escaneamento por ID"""
        return self._scans.get(scan_id)
    
    def find_by_hash(self, file_hash: str) -> List[FileScanResult]:
        """Busca escaneamentos por hash do arquivo"""
        return [
            scan for scan in self._scans.values()
            if scan.file_hash == file_hash
        ]
    
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[ScanStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[FileScanResult]:
        """Busca escaneamentos com filtros"""
        results = list(self._scans.values())
        
        # Aplicar filtros
        if status:
            results = [r for r in results if r.status == status]
        
        if start_date:
            results = [r for r in results if r.scan_time >= start_date]
        
        if end_date:
            results = [r for r in results if r.scan_time <= end_date]
        
        # Ordenar por timestamp (mais recentes primeiro)
        results.sort(key=lambda x: x.scan_time, reverse=True)
        
        # Aplicar paginação
        return results[offset:offset + limit]
    
    def find_infected(self, limit: int = 100) -> List[FileScanResult]:
        """Busca apenas arquivos infectados"""
        infected = [
            scan for scan in self._scans.values()
            if scan.status == ScanStatus.INFECTED
        ]
        infected.sort(key=lambda x: x.scan_time, reverse=True)
        return infected[:limit]
    
    def clear(self) -> None:
        """Limpa todos os escaneamentos (útil para testes)"""
        self._scans.clear()

