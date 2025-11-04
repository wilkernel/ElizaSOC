# Scripts de Teste para ElizaSOC

## Gerar Alertas de Teste

O script `generate_test_alerts.py` permite gerar alertas de teste no formato do Suricata para testar o sistema sem ter tráfego real de rede.

### Uso Básico

```bash
# Gerar 10 alertas de teste
python3 scripts/generate_test_alerts.py

# Gerar 50 alertas com intervalo de 2 segundos
python3 scripts/generate_test_alerts.py -n 50 -i 2

# Gerar apenas alertas (sem flows ou DNS)
python3 scripts/generate_test_alerts.py -t alert -n 20

# Gerar eventos continuamente (até pressionar Ctrl+C)
python3 scripts/generate_test_alerts.py --continuous -i 0.5

# Especificar arquivo de saída customizado
python3 scripts/generate_test_alerts.py -f /tmp/eve_test.json -n 10
```

### Opções

- `-n, --num`: Número de eventos a gerar (padrão: 10)
- `-t, --type`: Tipo de evento (alert, flow, dns, all) - padrão: all
- `-i, --interval`: Intervalo entre eventos em segundos (padrão: 1.0)
- `-f, --file`: Caminho do arquivo eve.json (padrão: /var/log/suricata/eve.json)
- `--continuous`: Gerar eventos continuamente até interromper (Ctrl+C)

### Exemplos Práticos

#### 1. Testar o Dashboard com Dados de Teste

```bash
# Gerar 100 alertas de uma vez
python3 scripts/generate_test_alerts.py -n 100 -i 0.1

# Depois abra o dashboard e verifique:
# - Cards de estatísticas atualizados
# - Gráficos com dados
# - Tabela de alertas preenchida
```

#### 2. Testar Monitoramento em Tempo Real

```bash
# Terminal 1: Iniciar o dashboard
python3 app.py

# Terminal 2: Gerar eventos continuamente
python3 scripts/generate_test_alerts.py --continuous -i 2

# No dashboard:
# 1. Vá para a aba "Logs em Tempo Real"
# 2. Clique em "Iniciar Monitoramento"
# 3. Você verá os alertas aparecendo em tempo real
```

#### 3. Testar Protocolos Específicos

```bash
# Gerar apenas alertas HTTP/HTTPS
python3 scripts/generate_test_alerts.py -t alert -n 50 -i 0.5

# Depois clique nos cards de protocolo no dashboard para ver:
# - Estatísticas específicas do protocolo
# - Gráficos filtrados
# - Alertas relacionados
```

#### 4. Criar Arquivo de Teste Local

```bash
# Criar arquivo de teste sem precisar de sudo
python3 scripts/generate_test_alerts.py -f ~/eve_test.json -n 100

# Depois, se necessário, copiar para o local do Suricata:
sudo cp ~/eve_test.json /var/log/suricata/eve.json.backup
```

### Permissões

Se o arquivo `/var/log/suricata/eve.json` não existir ou você não tiver permissão:

```bash
# Opção 1: Criar arquivo com permissões corretas
sudo touch /var/log/suricata/eve.json
sudo chmod 644 /var/log/suricata/eve.json
sudo chown suricata:suricata /var/log/suricata/eve.json

# Opção 2: Executar script com sudo (cuidado!)
sudo python3 scripts/generate_test_alerts.py -n 10

# Opção 3: Usar arquivo local
python3 scripts/generate_test_alerts.py -f ~/eve_test.json -n 10
```

### Verificar Dados Gerados

```bash
# Ver últimas linhas do arquivo
tail -n 20 /var/log/suricata/eve.json

# Contar alertas
grep -c '"event_type":"alert"' /var/log/suricata/eve.json

# Ver último alerta
tail -n 1 /var/log/suricata/eve.json | python3 -m json.tool
```

### Troubleshooting

#### Erro: "Arquivo não encontrado"
- Verifique se o caminho está correto: `/var/log/suricata/eve.json`
- Use `-f` para especificar um caminho diferente

#### Erro: "Sem permissão"
- Execute com `sudo` ou ajuste as permissões do arquivo
- Ou use um arquivo local com `-f ~/eve_test.json`

#### Stream não funciona
- Verifique se o arquivo existe e está acessível
- Verifique se o dashboard está rodando
- Abra o console do navegador (F12) para ver erros
- Certifique-se de que o arquivo tem novas linhas sendo adicionadas

### Tipos de Eventos Gerados

1. **Alertas**: Eventos de segurança detectados
   - Assinaturas de phishing, malware, trojans
   - Diferentes severidades (1-4)
   - Múltiplos protocolos (TCP, UDP, HTTP, HTTPS, etc.)

2. **Flows**: Conexões de rede
   - Tráfego TCP/UDP
   - Estatísticas de bytes e pacotes

3. **DNS**: Consultas DNS
   - Resolução de nomes
   - Diferentes tipos de registro

### Integração com Suricata Real

Se você tem o Suricata rodando, o script pode adicionar eventos de teste ao arquivo real:

```bash
# Gerar alguns alertas de teste junto com os reais
python3 scripts/generate_test_alerts.py -n 10 -i 5

# Isso adiciona eventos ao arquivo sem interromper o Suricata
```

**Nota**: Os eventos de teste são indistinguíveis dos eventos reais no dashboard, então use com cuidado em ambientes de produção.

