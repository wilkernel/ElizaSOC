#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper de compatibilidade para clamav_scanner
Redireciona para a nova implementação em src/infrastructure/scanners/clamav_scanner.py
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
    from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
    from src.application.use_cases.scan_file_use_case import ScanFileUseCase
    
    # Criar instâncias globais para compatibilidade
    _scanner = ClamAVScanner()
    _repo = InMemoryFileScanRepository()
    _use_case = ScanFileUseCase(_scanner, _repo)
    
    def scan_file(filepath, quarantine=True):
        """Wrapper para compatibilidade com código antigo"""
        result = _use_case.execute(filepath, quarantine=quarantine)
        # Converter para formato antigo
        return {
            'filepath': result.filepath,
            'filename': result.filename,
            'infected': result.is_infected(),
            'virus_name': result.threat_name,
            'file_size': result.file_size,
            'file_hash': result.file_hash,
            'scan_time': result.scan_time.isoformat(),
            'scanner': result.scanner,
            'quarantined': result.quarantined,
        }
    
    def scan_directory(directory, recursive=True):
        """Wrapper para compatibilidade"""
        results = _use_case.execute_directory(directory, recursive=recursive)
        return [scan_file(r.filepath, quarantine=False) for r in results]
    
    def get_recent_scans(limit=100):
        """Wrapper para compatibilidade"""
        scans = _repo.find_all(limit=limit)
        return [{'result': r.to_dict()} for r in scans]
    
    def get_infected_files(limit=100):
        """Wrapper para compatibilidade"""
        infected = _repo.find_infected(limit=limit)
        return [r.to_dict() for r in infected]
    
except ImportError as e:
    # Se não conseguir importar, definir funções que retornam erro
    def scan_file(filepath, quarantine=True):
        return {'error': f'ClamAV scanner não disponível: {e}'}
    
    def scan_directory(directory, recursive=True):
        return [{'error': 'ClamAV scanner não disponível'}]
    
    def get_recent_scans(limit=100):
        return []
    
    def get_infected_files(limit=100):
        return []

if __name__ == '__main__':
    # CLI mode para compatibilidade
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = scan_file(filepath)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Uso: python3 clamav_scanner.py <arquivo>")

