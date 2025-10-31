#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Web para Monitoramento de Phishing com Suricata
Autor: Wilker Junio Coelho Pimenta
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS
import time
import sys

# Importar módulo ClamAV
try:
    from clamav_scanner import scan_file, get_recent_scans, get_infected_files, scan_directory
    CLAMAV_AVAILABLE = True
except ImportError:
    CLAMAV_AVAILABLE = False
    print("⚠️  Módulo clamav_scanner não encontrado. Funcionalidades de escaneamento desabilitadas.")

app = Flask(__name__)

# Configurações de Segurança
# CORS: Permitir apenas localhost em desenvolvimento
# Em produção, configurar com domínios específicos
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Configurações
EVE_JSON_PATH = "/var/log/suricata/eve.json"
ALERT_LOG_PATH = os.path.join(os.path.dirname(__file__), "logs/alertas_phishing.log")

# Modo de produção (alterar para True em produção)
PRODUCTION_MODE = os.getenv('FLASK_ENV') != 'development'

# Cache para otimização
last_file_size = 0
cached_alerts = []
cache_timestamp = 0
CACHE_DURATION = 30  # segundos

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
        # IPs públicos podem ser mostrados (são externos mesmo)
        # Mas você pode ofuscar também se preferir
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
        if not PRODUCTION_MODE:
            print("Erro de permissão ao acessar arquivo de log")
    except Exception as e:
        if not PRODUCTION_MODE:
            print(f"Erro ao ler arquivo de log")
    
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
    
    # Agrupar alertas por hora
    for alert in alerts:
        try:
            dt = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
            hour_key = dt.strftime('%Y-%m-%d %H:00')
            stats['alerts_by_hour'][hour_key] += 1
        except:
            pass
    
    return stats, alerts

@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('index.html')

@app.route('/api/stats')
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
        
        # Estatísticas de vírus (se ClamAV disponível)
        virus_stats = {
            'total_scanned': 0,
            'total_infected': 0,
            'clamav_available': CLAMAV_AVAILABLE
        }
        
        if CLAMAV_AVAILABLE:
            try:
                infected = get_infected_files(limit=1000)
                recent_scans = get_recent_scans(limit=1000)
                virus_stats['total_scanned'] = len(recent_scans)
                virus_stats['total_infected'] = len(infected)
            except:
                pass
        
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
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """API para listar alertas recentes"""
    try:
        limit = int(request.args.get('limit', 100))
        filter_phishing = request.args.get('phishing_only', 'false').lower() == 'true'
        
        alerts, _, _ = parse_eve_json(EVE_JSON_PATH, limit=limit, filter_phishing=filter_phishing)
        
        # Ordenar por timestamp (mais recentes primeiro)
        alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'alerts': alerts[:limit],
            'count': len(alerts)
        })
    except Exception as e:
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/recent')
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
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/phishing')
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
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/logs/stream')
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

@app.route('/api/status')
def api_status():
    """API para status do sistema"""
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
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/viruses')
def api_viruses():
    """API para listar vírus detectados"""
    if not CLAMAV_AVAILABLE:
        return jsonify({'error': 'ClamAV não disponível', 'viruses': []}), 503
    
    try:
        limit = int(request.args.get('limit', 50))
        infected = get_infected_files(limit=limit)
        
        # Ordenar por timestamp (mais recentes primeiro)
        infected.sort(key=lambda x: x.get('scan_time', ''), reverse=True)
        
        return jsonify({
            'viruses': infected[:limit],
            'count': len(infected)
        })
    except Exception as e:
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/files/scanned')
def api_files_scanned():
    """API para listar arquivos escaneados"""
    if not CLAMAV_AVAILABLE:
        return jsonify({'error': 'ClamAV não disponível', 'scans': []}), 503
    
    try:
        limit = int(request.args.get('limit', 100))
        scans = get_recent_scans(limit=limit)
        
        # Extrair apenas resultados
        scan_results = [entry.get('result', {}) for entry in scans]
        scan_results.sort(key=lambda x: x.get('scan_time', ''), reverse=True)
        
        return jsonify({
            'scans': scan_results[:limit],
            'count': len(scan_results)
        })
    except Exception as e:
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

@app.route('/api/files/scan', methods=['POST'])
def api_scan_file():
    """API para escanear um arquivo específico"""
    if not CLAMAV_AVAILABLE:
        return jsonify({'error': 'ClamAV não disponível'}), 503
    
    try:
        data = request.get_json()
        filepath = data.get('filepath') if data else request.args.get('filepath')
        
        if not filepath:
            return jsonify({'error': 'Caminho do arquivo não fornecido'}), 400
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Escanear arquivo
        result = scan_file(filepath, quarantine=True)
        
        return jsonify(result)
    except Exception as e:
        if PRODUCTION_MODE:
            return jsonify({'error': 'Erro ao processar requisição'}), 500
        else:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
    
    print("🚀 Iniciando servidor web do Dashboard de Monitoramento...")
    print("📊 Acesse: http://localhost:5000")
    if not PRODUCTION_MODE:
        print("⚠️  Modo desenvolvimento - Certifique-se de que o arquivo de log está acessível")
    else:
        print("🔒 Modo produção ativo")
    
    # Desabilitar debug em produção
    app.run(host='0.0.0.0', port=5000, debug=not PRODUCTION_MODE, threaded=True)


