#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Escaneamento com ClamAV
Autor: Wilker Junio Coelho Pimenta
"""

import subprocess
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Diretório de quarentena (tentar /var/quarantine, fallback para local)
QUARANTINE_DIR = "/var/quarantine"
LOCAL_QUARANTINE_DIR = os.path.join(os.path.dirname(__file__), "quarantine")
SCAN_LOG_PATH = os.path.join(os.path.dirname(__file__), "logs/clamav_scans.log")

def ensure_directories():
    """Garante que os diretórios necessários existem"""
    # Tentar criar diretório de quarentena (pode falhar se sem permissão)
    try:
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
        quarantine_dir = QUARANTINE_DIR
    except PermissionError:
        # Fallback para diretório local
        os.makedirs(LOCAL_QUARANTINE_DIR, exist_ok=True)
        quarantine_dir = LOCAL_QUARANTINE_DIR
    
    os.makedirs(os.path.dirname(SCAN_LOG_PATH), exist_ok=True)
    return quarantine_dir

def calculate_hash(filepath):
    """Calcula SHA256 de um arquivo"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None

def scan_file(filepath, quarantine=True):
    """
    Escaneia arquivo com ClamAV
    
    Args:
        filepath: Caminho do arquivo a escanear
        quarantine: Se True, move para quarentena se infectado
    
    Returns:
        dict: Resultado do escaneamento
    """
    if not os.path.exists(filepath):
        return {'error': 'Arquivo não encontrado'}
    
    try:
        # Executar ClamAV scan
        result = subprocess.run(
            ['clamscan', '--stdout', '--no-summary', filepath],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        is_infected = result.returncode == 1
        virus_name = None
        file_size = os.path.getsize(filepath)
        file_hash = calculate_hash(filepath)
        
        # Extrair nome do vírus se detectado
        if is_infected:
            for line in result.stdout.split('\n'):
                if 'FOUND' in line:
                    parts = line.split('FOUND')
                    if len(parts) > 1:
                        # Formato: /path/to/file: VirusName FOUND
                        virus_part = parts[0].strip()
                        virus_name = virus_part.split(':')[-1].strip()
        
        scan_result = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'infected': is_infected,
            'virus_name': virus_name,
            'file_size': file_size,
            'file_hash': file_hash,
            'scan_time': datetime.now().isoformat(),
            'scanner': 'ClamAV',
            'quarantined': False
        }
        
        # Se infectado e quarentena habilitada
        if is_infected and quarantine:
            quarantine_result = quarantine_file(filepath, file_hash)
            scan_result['quarantined'] = quarantine_result['success']
            scan_result['quarantine_path'] = quarantine_result.get('quarantine_path')
        
        # Log do escaneamento
        log_scan(scan_result)
        
        return scan_result
        
    except subprocess.TimeoutExpired:
        return {'error': 'Timeout durante escaneamento'}
    except Exception as e:
        return {'error': str(e)}

def quarantine_file(filepath, file_hash=None):
    """
    Move arquivo para quarentena
    
    Args:
        filepath: Caminho do arquivo
        file_hash: Hash do arquivo (opcional)
    
    Returns:
        dict: Resultado da quarentena
    """
    quarantine_dir = ensure_directories()
    
    try:
        if not file_hash:
            file_hash = calculate_hash(filepath)
        
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        quarantine_filename = f"{timestamp}_{file_hash[:16]}_{filename}"
        quarantine_path = os.path.join(quarantine_dir, quarantine_filename)
        
        # Mover arquivo
        os.rename(filepath, quarantine_path)
        
        # Remover permissões de execução
        os.chmod(quarantine_path, 0o000)
        
        return {
            'success': True,
            'quarantine_path': quarantine_path,
            'original_path': filepath
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def scan_directory(directory, recursive=True):
    """
    Escaneia todos os arquivos de um diretório
    
    Args:
        directory: Diretório a escanear
        recursive: Se True, escaneia recursivamente
    
    Returns:
        list: Lista de resultados
    """
    results = []
    
    if not os.path.isdir(directory):
        return results
    
    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.isfile(filepath):
                        result = scan_file(filepath)
                        results.append(result)
        else:
            for item in os.listdir(directory):
                filepath = os.path.join(directory, item)
                if os.path.isfile(filepath):
                    result = scan_file(filepath)
                    results.append(result)
    except Exception as e:
        return [{'error': f'Erro ao escanear diretório: {str(e)}'}]
    
    return results

def log_scan(scan_result):
    """Registra resultado do escaneamento em log"""
    ensure_directories()
    try:
        with open(SCAN_LOG_PATH, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'result': scan_result
            }
            f.write(json.dumps(log_entry) + '\n')
    except:
        pass

def get_recent_scans(limit=100):
    """Recupera escaneamentos recentes do log"""
    scans = []
    
    if not os.path.exists(SCAN_LOG_PATH):
        return scans
    
    try:
        with open(SCAN_LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Pegar últimas linhas
            for line in lines[-limit:]:
                try:
                    entry = json.loads(line.strip())
                    scans.append(entry)
                except:
                    continue
    except:
        pass
    
    return scans

def get_infected_files(limit=100):
    """Recupera apenas arquivos infectados"""
    all_scans = get_recent_scans(limit * 10)  # Buscar mais para filtrar
    infected = []
    
    for scan_entry in all_scans:
        result = scan_entry.get('result', {})
        if result.get('infected'):
            infected.append(result)
        if len(infected) >= limit:
            break
    
    return infected

if __name__ == '__main__':
    # Teste básico
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = scan_file(filepath)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Uso: python3 clamav_scanner.py <arquivo>")

