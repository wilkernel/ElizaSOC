"""
Controller de Arquivos - API REST
Refatorado seguindo Clean Architecture
"""
from flask import Blueprint, jsonify, request

from src.domain.repositories.file_scan_repository import FileScanRepository
from src.application.use_cases.scan_file_use_case import ScanFileUseCase
from src.domain.entities.file_scan import ScanStatus


files_bp = Blueprint('files', __name__)


def register_files_routes(bp: Blueprint, file_scan_repository: FileScanRepository, scan_use_case: ScanFileUseCase):
    """Registra rotas de arquivos"""
    
    @bp.route('/api/files/scanned', methods=['GET'])
    def get_scanned_files():
        """GET /api/files/scanned - Lista arquivos escaneados"""
        try:
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            scans = file_scan_repository.find_all(limit=limit, offset=offset)
            
            return jsonify({
                'scans': [scan.to_dict() for scan in scans],
                'count': len(scans),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/files/infected', methods=['GET'])
    def get_infected_files():
        """GET /api/files/infected - Lista apenas arquivos infectados"""
        try:
            limit = int(request.args.get('limit', 100))
            
            infected = file_scan_repository.find_infected(limit=limit)
            
            return jsonify({
                'infected': [scan.to_dict() for scan in infected],
                'count': len(infected),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/files/scan', methods=['POST'])
    def scan_file():
        """POST /api/files/scan - Escaneia um arquivo"""
        try:
            data = request.get_json() or {}
            filepath = data.get('filepath') or request.args.get('filepath')
            
            if not filepath:
                return jsonify({'error': 'Caminho do arquivo não fornecido'}), 400
            
            quarantine = data.get('quarantine', True)
            
            # Executar caso de uso
            result = scan_use_case.execute(filepath, quarantine=quarantine)
            
            return jsonify(result.to_dict())
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/files/<scan_id>', methods=['GET'])
    def get_scan_result(scan_id: str):
        """GET /api/files/<scan_id> - Busca resultado de escaneamento por ID"""
        try:
            scan = file_scan_repository.find_by_id(scan_id)
            
            if not scan:
                return jsonify({'error': 'Escaneamento não encontrado'}), 404
            
            return jsonify(scan.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
