"""
Controller de Dashboard - Compatibilidade com app.py original
Para suportar o dashboard web que lê logs do Suricata
"""
import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from flask import Blueprint, jsonify, request, Response

# Path do arquivo de log do Suricata
EVE_JSON_PATH = "/var/log/suricata/eve.json"

dashboard_bp = Blueprint('dashboard', __name__)


def is_phishing_alert(signature):
    """Verifica se um alerta é relacionado a phishing/malware"""
    keywords = ['PHISHING', 'TROJAN', 'MALWARE', 'SUSPICIOUS', 'MALICIOUS', 'BLACKLIST']
    return any(keyword in signature.upper() for keyword in keywords)


def is_private_ip(ip):
    """Verifica se um IP é privado (RFC 1918)"""
    if not ip or not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        octets = [int(p) for p in parts]
        # 192.168.0.0/16
        if octets[0] == 192 and octets[1] == 168:
            return True
        # 10.0.0.0/8
        if octets[0] == 10:
            return True
        # 172.16.0.0/12
        if octets[0] == 172 and 16 <= octets[1] <= 31:
            return True
    except:
        pass
    return False


def mask_ip(ip):
    """Ofusca IPs privados mantendo apenas informação útil para análise"""
    if not ip or ip == 'N/A' or ip == 'Unknown':
        return ip
    
    if is_private_ip(ip):
        parts = ip.split('.')
        # Mostrar apenas último octeto: 192.168.1.100 -> *.100
        return f"*.{parts[-1]}"
    else:
        return ip


def parse_eve_json(file_path, limit=None, filter_phishing=False):
    """Lê e parseia o arquivo eve.json do Suricata"""
    alerts = []
    flows = []
    dns_queries = []
    
    if not os.path.exists(file_path):
        return alerts, flows, dns_queries
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Ler apenas as últimas linhas para performance
            if limit:
                lines = lines[-limit:]
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    event_type = data.get('event_type', '')
                    
                    if event_type == 'alert':
                        signature = data.get('alert', {}).get('signature', '')
                        if filter_phishing and not is_phishing_alert(signature):
                            continue
                        
                        alert = {
                            'timestamp': data.get('timestamp', ''),
                            'signature': signature,
                            'category': data.get('alert', {}).get('category', ''),
                            'severity': data.get('alert', {}).get('severity', 0),
                            'src_ip': mask_ip(data.get('src_ip', '')),
                            'dest_ip': mask_ip(data.get('dest_ip', '')),
                            'src_port': data.get('src_port', 0),
                            'dest_port': data.get('dest_port', 0),
                            'proto': data.get('proto', ''),
                            'is_phishing': is_phishing_alert(signature)
                        }
                        alerts.append(alert)
                    
                    elif event_type == 'flow':
                        flows.append(data)
                    
                    elif event_type == 'dns':
                        dns_queries.append(data)
                
                except json.JSONDecodeError:
                    continue
    
    except PermissionError:
        pass
    except Exception as e:
        pass
    
    return alerts, flows, dns_queries


def get_statistics():
    """Calcula estatísticas dos alertas"""
    alerts, flows, dns_queries = parse_eve_json(EVE_JSON_PATH, limit=50000)
    
    stats = {
        'total_alerts': len(alerts),
        'phishing_alerts': sum(1 for a in alerts if a.get('is_phishing', False)),
        'total_flows': len(flows),
        'total_dns': len(dns_queries),
        'severity_distribution': Counter(a.get('severity', 0) for a in alerts),
        'proto_distribution': Counter(a.get('proto', 'UNKNOWN') for a in alerts),
        'alerts_by_hour': defaultdict(int),
        'top_signatures': Counter(a.get('signature', 'Unknown') for a in alerts),
        'top_src_ips': Counter(mask_ip(a.get('src_ip', 'Unknown')) for a in alerts if a.get('src_ip')),
        'top_dest_ips': Counter(mask_ip(a.get('dest_ip', 'Unknown')) for a in alerts if a.get('dest_ip')),
    }
    
    # Adicionar distribuição de protocolos de flows e DNS para ter visibilidade completa
    proto_dist_all = stats['proto_distribution'].copy()
    for flow in flows:
        proto = flow.get('proto', 'UNKNOWN')
        if proto:
            proto_dist_all[proto] += 1
    for dns in dns_queries:
        proto = dns.get('proto', 'UNKNOWN')
        if proto:
            proto_dist_all[proto] += 1
    stats['proto_distribution'] = proto_dist_all
    
    # Agrupar alertas por hora
    for alert in alerts:
        try:
            dt = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
            hour_key = dt.strftime('%Y-%m-%d %H:00')
            stats['alerts_by_hour'][hour_key] += 1
        except:
            pass
    
    return stats, alerts


def register_dashboard_routes(bp: Blueprint):
    """Registra rotas do dashboard"""
    
    @bp.route('/api/stats')
    def api_stats():
        """API para estatísticas gerais"""
        try:
            stats, alerts = get_statistics()
            
            # Preparar dados para os gráficos
            severity_data = dict(stats['severity_distribution'])
            proto_data = dict(stats['proto_distribution'])
            
            # Top 10 signatures
            top_signatures = dict(stats['top_signatures'].most_common(10))
            
            # Top 10 IPs de origem
            top_src_ips = dict(stats['top_src_ips'].most_common(10))
            
            # Alerts por hora (últimas 24 horas)
            now = datetime.now()
            hours_24 = {}
            for i in range(24):
                hour = now - timedelta(hours=i)
                hour_key = hour.strftime('%Y-%m-%d %H:00')
                hours_24[hour_key] = stats['alerts_by_hour'].get(hour_key, 0)
            
            # Ordenar por hora
            sorted_hours = sorted(hours_24.items(), key=lambda x: x[0])
            
            # Verificar ClamAV disponível
            clamav_available = False
            try:
                from clamav_scanner import get_recent_scans, get_infected_files
                clamav_available = True
                infected = get_infected_files(limit=1000)
                recent_scans = get_recent_scans(limit=1000)
                virus_stats = {
                    'total_scanned': len(recent_scans),
                    'total_infected': len(infected),
                    'clamav_available': clamav_available
                }
            except ImportError:
                virus_stats = {
                    'total_scanned': 0,
                    'total_infected': 0,
                    'clamav_available': False
                }
            
            return jsonify({
                'total_alerts': stats['total_alerts'],
                'phishing_alerts': stats['phishing_alerts'],
                'total_flows': stats['total_flows'],
                'total_dns': stats['total_dns'],
                'severity': severity_data,
                'protocols': proto_data,
                'top_signatures': top_signatures,
                'top_src_ips': top_src_ips,
                'alerts_by_hour': dict(sorted_hours[-24:]),
                'virus_stats': virus_stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/alerts/recent')
    def api_recent_alerts():
        """API para alertas recentes (últimos 50)"""
        try:
            alerts, _, _ = parse_eve_json(EVE_JSON_PATH, limit=1000)
            alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return jsonify({
                'alerts': alerts[:50],
                'count': len(alerts[:50])
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/phishing')
    def api_phishing():
        """API específica para alertas de phishing"""
        try:
            alerts, _, _ = parse_eve_json(EVE_JSON_PATH, limit=10000, filter_phishing=True)
            alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return jsonify({
                'alerts': alerts[:100],
                'count': len(alerts)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/api/logs/stream')
    def stream_logs():
        """Stream de logs em tempo real"""
        def generate():
            file_path = EVE_JSON_PATH
            if not os.path.exists(file_path):
                yield f"data: {json.dumps({'error': 'Arquivo não encontrado'})}\n\n"
                return
            
            # Função para sanitizar dados do log
            def sanitize_log_data(data):
                """Remove informações sensíveis do log antes de enviar"""
                if isinstance(data, dict):
                    sanitized = data.copy()
                    if 'src_ip' in sanitized:
                        sanitized['src_ip'] = mask_ip(sanitized['src_ip'])
                    if 'dest_ip' in sanitized:
                        sanitized['dest_ip'] = mask_ip(sanitized['dest_ip'])
                    return sanitized
                return data
            
            # Ler última posição
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.seek(0, 2)  # Ir para o final do arquivo
                
                while True:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            f.seek(0, 2)
                            while True:
                                line = f.readline()
                                if line:
                                    try:
                                        data = json.loads(line.strip())
                                        if data.get('event_type') == 'alert':
                                            sanitized_data = sanitize_log_data(data)
                                            yield f"data: {json.dumps(sanitized_data)}\n\n"
                                    except:
                                        pass
                                else:
                                    time.sleep(1)
                    except:
                        time.sleep(5)
            except:
                yield f"data: {json.dumps({'error': 'Erro ao ler arquivo'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    @bp.route('/api/status')
    def api_status_dashboard():
        """API para status do sistema (compatível com dashboard)"""
        try:
            file_exists = os.path.exists(EVE_JSON_PATH)
            file_size = 0
            file_modified = None
            
            if file_exists:
                stat = os.stat(EVE_JSON_PATH)
                file_size = stat.st_size
                file_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Verificar se Suricata está rodando
            suricata_running = False
            try:
                result = os.popen('systemctl is-active suricata 2>/dev/null').read().strip()
                suricata_running = result == 'active'
            except:
                pass
            
            return jsonify({
                'suricata_running': suricata_running,
                'eve_json_exists': file_exists,
                'eve_json_size': file_size,
                'eve_json_modified': file_modified,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

