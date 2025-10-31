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

app = Flask(__name__)
CORS(app)

# Configurações
EVE_JSON_PATH = "/var/log/suricata/eve.json"
ALERT_LOG_PATH = os.path.join(os.path.dirname(__file__), "logs/alertas_phishing.log")

# Cache para otimização
last_file_size = 0
cached_alerts = []
cache_timestamp = 0
CACHE_DURATION = 30  # segundos

def is_phishing_alert(signature):
    """Verifica se um alerta é relacionado a phishing/malware"""
    keywords = ['PHISHING', 'TROJAN', 'MALWARE', 'SUSPICIOUS', 'MALICIOUS', 'BLACKLIST']
    return any(keyword in signature.upper() for keyword in keywords)

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
                            'src_ip': data.get('src_ip', ''),
                            'dest_ip': data.get('dest_ip', ''),
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
        print(f"Erro de permissão ao acessar {file_path}")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
    
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
        'top_src_ips': Counter(a.get('src_ip', 'Unknown') for a in alerts if a.get('src_ip')),
        'top_dest_ips': Counter(a.get('dest_ip', 'Unknown') for a in alerts if a.get('dest_ip')),
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
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/stream')
def stream_logs():
    """Stream de logs em tempo real"""
    def generate():
        file_path = EVE_JSON_PATH
        if not os.path.exists(file_path):
            yield f"data: {json.dumps({'error': 'Arquivo não encontrado'})}\n\n"
            return
        
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
                                        yield f"data: {json.dumps(data)}\n\n"
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
    
    print("🚀 Iniciando servidor web do Dashboard de Monitoramento...")
    print("📊 Acesse: http://localhost:5000")
    print("⚠️  Certifique-se de que o arquivo /var/log/suricata/eve.json está acessível")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


