"""
Controller de Alertas - API REST
Refatorado seguindo Clean Architecture
"""
from flask import Blueprint, jsonify, request
from typing import Optional
from datetime import datetime

from src.domain.entities.alert import AlertCategory, AlertSeverity
from src.domain.repositories.alert_repository import AlertRepository


alerts_bp = Blueprint('alerts', __name__)


def register_alerts_routes(bp: Blueprint, alert_repository: AlertRepository):
    """Registra rotas de alertas"""
    
    @bp.route('/api/alerts', methods=['GET'])
    def get_alerts():
        """GET /api/alerts - Lista alertas com filtros opcionais"""
        try:
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            # Filtros opcionais
            category = None
            if request.args.get('category'):
                try:
                    category = AlertCategory(request.args.get('category'))
                except ValueError:
                    pass
            
            severity = None
            if request.args.get('severity'):
                try:
                    severity = AlertSeverity(int(request.args.get('severity')))
                except (ValueError, TypeError):
                    pass
            
            # Buscar alertas
            alerts = alert_repository.find_all(
                limit=limit,
                offset=offset,
                category=category,
                severity=severity,
            )
            
            return jsonify({
                'alerts': [alert.to_dict() for alert in alerts],
                'count': len(alerts),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/alerts/<alert_id>', methods=['GET'])
    def get_alert(alert_id: str):
        """GET /api/alerts/<id> - Busca alerta por ID"""
        try:
            alert = alert_repository.find_by_id(alert_id)
            
            if not alert:
                return jsonify({'error': 'Alerta não encontrado'}), 404
            
            return jsonify(alert.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/alerts/stats', methods=['GET'])
    def get_alerts_stats():
        """GET /api/alerts/stats - Estatísticas de alertas"""
        try:
            total = alert_repository.count()
            phishing = alert_repository.count(category=AlertCategory.PHISHING)
            malware = alert_repository.count(category=AlertCategory.MALWARE)
            critical = alert_repository.count(severity=AlertSeverity.CRITICAL)
            
            return jsonify({
                'total': total,
                'phishing': phishing,
                'malware': malware,
                'critical': critical,
                'timestamp': datetime.utcnow().isoformat(),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/alerts/phishing', methods=['GET'])
    def get_phishing_alerts():
        """GET /api/alerts/phishing - Lista apenas alertas de phishing"""
        try:
            limit = int(request.args.get('limit', 100))
            
            alerts = alert_repository.find_all(
                limit=limit,
                category=AlertCategory.PHISHING,
            )
            
            return jsonify({
                'alerts': [alert.to_dict() for alert in alerts],
                'count': len(alerts),
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
