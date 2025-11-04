#!/usr/bin/env python3
"""
Script para gerar alertas de teste no formato do Suricata eve.json
Útil para testar o sistema quando não há tráfego real de rede
"""
import json
import time
import random
from datetime import datetime, timedelta
import os

# Caminho do arquivo eve.json do Suricata
EVE_JSON_PATH = "/var/log/suricata/eve.json"

# Protocolos e assinaturas de teste
PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'DNS', 'SMTP', 'SSH', 'FTP']
SIGNATURES = [
    'ET MALWARE Phishing Site',
    'ET TROJAN Suspicious Activity',
    'ET POLICY Suspicious Request',
    'ET SCAN Potential Port Scan',
    'ET DROP Dshield Block Listed',
    'GPL ICMP PING',
    'GPL ATTACK_RESPONSE id check returned root',
    'ET POLICY SSH connection attempt',
    'ET CURRENT_EVENTS Malicious Domain',
    'ET MALWARE Known Malware C2',
]

# IPs de teste (públicos e privados)
TEST_IPS = [
    '192.168.1.100',
    '10.0.0.50',
    '172.16.0.25',
    '203.0.113.10',
    '198.51.100.20',
    '192.0.2.30',
]

def generate_test_alert(protocol=None, signature=None):
    """Gera um alerta de teste no formato do Suricata"""
    if protocol is None:
        protocol = random.choice(PROTOCOLS)
    if signature is None:
        signature = random.choice(SIGNATURES)
    
    # Timestamp atual
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # IPs aleatórios
    src_ip = random.choice(TEST_IPS)
    dest_ip = random.choice(TEST_IPS)
    
    # Evitar mesmo IP origem e destino
    while src_ip == dest_ip:
        dest_ip = random.choice(TEST_IPS)
    
    # Portas baseadas no protocolo
    port_mapping = {
        'HTTP': (80, 80),
        'HTTPS': (443, 443),
        'SSH': (22, 22),
        'FTP': (21, 21),
        'SMTP': (25, 25),
        'DNS': (53, 53),
    }
    
    if protocol in port_mapping:
        src_port, dest_port = port_mapping[protocol]
    else:
        src_port = random.randint(10000, 65535)
        dest_port = random.randint(1, 1024)
    
    # Severidade aleatória
    severity = random.choice([1, 2, 3, 4])
    
    # Determinar se é phishing
    is_phishing = any(keyword in signature.upper() for keyword in ['PHISHING', 'MALWARE', 'TROJAN'])
    
    alert = {
        "timestamp": timestamp,
        "event_type": "alert",
        "src_ip": src_ip,
        "src_port": src_port,
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "proto": protocol,
        "alert": {
            "action": "allowed",
            "gid": 1,
            "signature_id": random.randint(2000000, 2999999),
            "rev": 1,
            "signature": signature,
            "category": "A Network Trojan was detected" if is_phishing else "Potentially Bad Traffic",
            "severity": severity
        },
        "app_proto": "http" if protocol in ['HTTP', 'HTTPS'] else "failed",
        "flow_id": random.randint(1000000, 9999999),
        "in_iface": "eth0"
    }
    
    return alert

def generate_test_flow(protocol=None):
    """Gera um flow de teste"""
    if protocol is None:
        protocol = random.choice(PROTOCOLS)
    
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    alert = {
        "timestamp": timestamp,
        "event_type": "flow",
        "src_ip": random.choice(TEST_IPS),
        "src_port": random.randint(10000, 65535),
        "dest_ip": random.choice(TEST_IPS),
        "dest_port": random.randint(1, 1024),
        "proto": protocol,
        "app_proto": "http" if protocol in ['HTTP', 'HTTPS'] else "failed",
        "flow_id": random.randint(1000000, 9999999),
        "in_iface": "eth0",
        "bytes_toserver": random.randint(100, 10000),
        "bytes_toclient": random.randint(100, 10000),
        "packets_toserver": random.randint(1, 100),
        "packets_toclient": random.randint(1, 100)
    }
    
    return alert

def generate_test_dns():
    """Gera uma consulta DNS de teste"""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    domains = [
        'example.com',
        'suspicious-site.com',
        'test-domain.net',
        'malicious-url.org',
    ]
    
    alert = {
        "timestamp": timestamp,
        "event_type": "dns",
        "src_ip": random.choice(TEST_IPS),
        "src_port": random.randint(10000, 65535),
        "dest_ip": random.choice(TEST_IPS),
        "dest_port": 53,
        "proto": "UDP",
        "dns": {
            "type": "query",
            "id": random.randint(1, 65535),
            "rrname": random.choice(domains),
            "rrtype": "A",
            "rcode": "NOERROR",
            "rd": random.choice([True, False])
        }
    }
    
    return alert

def append_to_eve_json(data, file_path=EVE_JSON_PATH):
    """Adiciona um evento ao arquivo eve.json"""
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Adicionar ao arquivo (append mode)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        print(f"✓ Evento adicionado: {data.get('event_type')} - {data.get('alert', {}).get('signature', 'N/A')}")
        return True
    except PermissionError:
        print(f"✗ Erro: Sem permissão para escrever em {file_path}")
        print(f"  Execute com sudo ou ajuste as permissões do arquivo")
        return False
    except Exception as e:
        print(f"✗ Erro ao adicionar evento: {e}")
        return False

def main():
    """Gera eventos de teste"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera alertas de teste para o Suricata')
    parser.add_argument('-n', '--num', type=int, default=10, help='Número de alertas a gerar (padrão: 10)')
    parser.add_argument('-t', '--type', choices=['alert', 'flow', 'dns', 'all'], default='all',
                        help='Tipo de evento a gerar (padrão: all)')
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='Intervalo entre eventos em segundos (padrão: 1.0)')
    parser.add_argument('-f', '--file', default=EVE_JSON_PATH,
                        help=f'Caminho do arquivo eve.json (padrão: {EVE_JSON_PATH})')
    parser.add_argument('--continuous', action='store_true',
                        help='Gerar eventos continuamente')
    
    args = parser.parse_args()
    
    print(f"Gerando eventos de teste...")
    print(f"Arquivo: {args.file}")
    print(f"Tipo: {args.type}")
    print(f"Quantidade: {'Contínuo' if args.continuous else args.num}")
    print("-" * 50)
    
    count = 0
    
    try:
        while True:
            if args.type in ['alert', 'all']:
                alert = generate_test_alert()
                append_to_eve_json(alert, args.file)
                count += 1
            
            if args.type in ['flow', 'all']:
                flow = generate_test_flow()
                append_to_eve_json(flow, args.file)
                count += 1
            
            if args.type in ['dns', 'all']:
                dns = generate_test_dns()
                append_to_eve_json(dns, args.file)
                count += 1
            
            if not args.continuous and count >= args.num:
                break
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    
    print(f"\n✓ Total de eventos gerados: {count}")

if __name__ == '__main__':
    main()

