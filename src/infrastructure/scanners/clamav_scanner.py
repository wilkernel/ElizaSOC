"""
Implementação ClamAV Scanner - Refatorada seguindo Clean Architecture e SOLID
"""
import subprocess
import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.domain.services.file_scanner import FileScanner
from src.domain.entities.file_scan import FileScanResult, ScanStatus


class ClamAVScanner(FileScanner):
    """
    Implementação ClamAV Scanner
    Segue princípios SOLID:
    - Single Responsibility: Apenas escaneamento com ClamAV
    - Open/Closed: Pode ser estendido via herança ou composição
    - Dependency Inversion: Implementa interface FileScanner
    """
    
    def __init__(self, quarantine_dir: Optional[str] = None, timeout: int = 300):
        """
        Inicializa o scanner ClamAV
        
        Args:
            quarantine_dir: Diretório de quarentena (opcional)
            timeout: Timeout para escaneamento em segundos
        """
        self.quarantine_dir = quarantine_dir or self._get_default_quarantine_dir()
        self.timeout = timeout
        self._ensure_directories()
    
    def _get_default_quarantine_dir(self) -> str:
        """Obtém diretório de quarentena padrão"""
        # Tenta usar diretório do sistema, fallback para local
        system_quarantine = "/var/quarantine"
        if os.access(os.path.dirname(system_quarantine), os.W_OK):
            return system_quarantine
        
        # Fallback para diretório local
        local_quarantine = os.path.join(
            os.path.dirname(__file__),
            "../../../quarantine"
        )
        return os.path.abspath(local_quarantine)
    
    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existem"""
        try:
            os.makedirs(self.quarantine_dir, exist_ok=True)
        except (PermissionError, OSError):
            # Se não conseguir criar, tentará novamente na quarentena
            pass
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """
        Calcula SHA256 de um arquivo
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Hash SHA256 do arquivo
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise IOError(f"Erro ao calcular hash: {str(e)}")
    
    def _execute_clamscan(self, filepath: str) -> tuple:
        """
        Executa ClamAV scan e retorna resultado
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Tupla (is_infected, virus_name)
        """
        try:
            result = subprocess.run(
                ['clamscan', '--stdout', '--no-summary', filepath],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            is_infected = result.returncode == 1
            virus_name = None
            
            if is_infected:
                # Extrair nome do vírus da saída
                for line in result.stdout.split('\n'):
                    if 'FOUND' in line:
                        # Formato: /path/to/file: VirusName FOUND
                        parts = line.split('FOUND')
                        if len(parts) > 1:
                            virus_part = parts[0].strip()
                            # Remover caminho do arquivo
                            if ':' in virus_part:
                                virus_name = virus_part.split(':')[-1].strip()
                            else:
                                virus_name = virus_part
                        break
            
            return is_infected, virus_name
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Timeout ao escanear arquivo: {filepath}")
        except FileNotFoundError:
            raise RuntimeError("ClamAV não está instalado ou não está no PATH")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar ClamAV: {str(e)}")
    
    def scan_file(self, filepath: str, quarantine: bool = True) -> FileScanResult:
        """
        Escaneia um arquivo com ClamAV
        
        Args:
            filepath: Caminho do arquivo a escanear
            quarantine: Se True, coloca em quarentena se infectado
            
        Returns:
            FileScanResult: Resultado do escaneamento
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        if not os.path.isfile(filepath):
            raise ValueError(f"Caminho não é um arquivo: {filepath}")
        
        try:
            # Executar escaneamento
            is_infected, virus_name = self._execute_clamscan(filepath)
            
            # Obter informações do arquivo
            file_size = os.path.getsize(filepath)
            file_hash = self._calculate_file_hash(filepath)
            
            # Determinar status
            if is_infected:
                status = ScanStatus.INFECTED
            else:
                status = ScanStatus.CLEAN
            
            # Criar resultado
            scan_result = FileScanResult(
                id=str(uuid.uuid4()),
                filepath=filepath,
                filename=os.path.basename(filepath),
                file_hash=file_hash,
                file_size=file_size,
                status=status,
                scan_time=datetime.utcnow(),
                scanner="ClamAV",
                threat_name=virus_name,
                quarantined=False,
            )
            
            # Quarentena se necessário
            if quarantine and scan_result.should_quarantine():
                quarantine_success = self.quarantine_file(filepath)
                scan_result.quarantined = quarantine_success
                if quarantine_success:
                    scan_result.quarantine_path = self._get_quarantine_path(filepath, file_hash)
            
            return scan_result
            
        except Exception as e:
            # Retornar resultado de erro
            return FileScanResult(
                id=str(uuid.uuid4()),
                filepath=filepath,
                filename=os.path.basename(filepath),
                file_hash=self._calculate_file_hash(filepath) if os.path.exists(filepath) else "",
                file_size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                status=ScanStatus.ERROR,
                scan_time=datetime.utcnow(),
                scanner="ClamAV",
                metadata={"error": str(e)},
            )
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[FileScanResult]:
        """
        Escaneia um diretório
        
        Args:
            directory: Diretório a escanear
            recursive: Se True, escaneia recursivamente
            
        Returns:
            Lista de resultados de escaneamento
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Caminho não é um diretório: {directory}")
        
        results = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        if os.path.isfile(filepath):
                            result = self.scan_file(filepath, quarantine=False)
                            results.append(result)
            else:
                for item in os.listdir(directory):
                    filepath = os.path.join(directory, item)
                    if os.path.isfile(filepath):
                        result = self.scan_file(filepath, quarantine=False)
                        results.append(result)
        except Exception as e:
            # Adicionar resultado de erro
            results.append(
                FileScanResult(
                    id=str(uuid.uuid4()),
                    filepath=directory,
                    filename=os.path.basename(directory),
                    file_hash="",
                    file_size=0,
                    status=ScanStatus.ERROR,
                    scan_time=datetime.utcnow(),
                    scanner="ClamAV",
                    metadata={"error": str(e)},
                )
            )
        
        return results
    
    def quarantine_file(self, filepath: str) -> bool:
        """
        Coloca arquivo em quarentena
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        if not os.path.exists(filepath):
            return False
        
        try:
            file_hash = self._calculate_file_hash(filepath)
            quarantine_path = self._get_quarantine_path(filepath, file_hash)
            
            # Garantir que diretório de quarentena existe
            os.makedirs(os.path.dirname(quarantine_path), exist_ok=True)
            
            # Mover arquivo
            os.rename(filepath, quarantine_path)
            
            # Remover permissões de execução
            os.chmod(quarantine_path, 0o000)
            
            return True
            
        except Exception:
            return False
    
    def _get_quarantine_path(self, filepath: str, file_hash: str) -> str:
        """
        Gera caminho de quarentena para um arquivo
        
        Args:
            filepath: Caminho original do arquivo
            file_hash: Hash do arquivo
            
        Returns:
            Caminho de quarentena
        """
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        quarantine_filename = f"{timestamp}_{file_hash[:16]}_{filename}"
        return os.path.join(self.quarantine_dir, quarantine_filename)

