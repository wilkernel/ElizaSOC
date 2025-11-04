#  Dashboard Web - Monitoramento de Phishing Suricata

Interface web responsiva para visualização em tempo real dos alertas do Suricata.

##  Instalação e Uso

### 1. Instalar Dependências

```bash
pip3 install -r requirements.txt
```

Ou usando o script de inicialização (instala automaticamente):

```bash
bash iniciar_dashboard.sh
```

### 2. Iniciar o Dashboard

**Opção 1 - Script completo (Recomendado):**
```bash
bash start_complete.sh
```
Este script inicia automaticamente todos os serviços necessários (Suricata, ClamAV) e o dashboard.

**Opção 2 - Script unificado:**
```bash
./start.sh refactored
```

**Opção 3 - Manual:**
```bash
python3 app.py
# ou
python3 app.py
```

### 3. Acessar a Interface

Abra seu navegador em: **http://localhost:5000**

Para acessar de outra máquina na rede:
```bash
python3 app.py
```
O servidor já está configurado para aceitar conexões de `0.0.0.0:5000`

##  Funcionalidades

### Dashboard Principal
- **Cards de Estatísticas**: Total de alertas, alertas de phishing, conexões monitoradas, consultas DNS
- **Métricas do Sistema**: CPU, memória e tamanho dos logs em tempo real
- **Gráficos Interativos**:
  - Alertas por hora (últimas 24h) - Gráfico de linha
  - Distribuição por severidade - Gráfico de rosca
  - Top 10 assinaturas de alerta - Gráfico de barras horizontal
  - Distribuição por protocolo - Gráfico de pizza
- **Controle de Serviços**: Painel para iniciar/parar/reiniciar Suricata e ClamAV

### Abas de Visualização
1. **Todos os Alertas**: Tabela completa com todos os alertas recentes
2. **Alertas de Phishing**: Filtro específico para alertas relacionados a phishing/malware/trojan
3. **Logs em Tempo Real**: Stream de alertas conforme são detectados pelo Suricata
4. **Controle de Serviços**: Gerenciamento de Suricata e ClamAV diretamente do dashboard

### Recursos
-  Atualização automática a cada 30 segundos
-  Design responsivo (mobile-friendly)
-  Indicador de status do Suricata
-  Logs em tempo real via Server-Sent Events (SSE)
-  Filtros automáticos para phishing/malware

##  Requisitos

- Python 3.6+
- Flask 3.0.0+
- flask-cors 4.0.0+
- Arquivo `/var/log/suricata/eve.json` acessível para leitura
- Suricata rodando como serviço

##  Permissões

Se encontrar erros de permissão ao acessar o `eve.json`:

```bash
sudo chmod 644 /var/log/suricata/eve.json
# ou
sudo chmod 755 /var/log/suricata
```

##  Interface

O dashboard possui um design moderno com:
- Tema escuro
- Gráficos interativos com Chart.js
- Tabelas responsivas
- Visualização de logs em tempo real
- Indicadores visuais de status

##  Atualização dos Dados

- **Estatísticas**: Atualizadas automaticamente a cada 30 segundos
- **Status do Sistema**: Verificado a cada 10 segundos
- **Logs em Tempo Real**: Via Server-Sent Events (stream contínuo)

##  Troubleshooting

### Porta 5000 já em uso
Altere a porta no arquivo `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
```

### Erro ao ler eve.json
```bash
# Verificar permissões
ls -la /var/log/suricata/eve.json

# Ajustar se necessário
sudo chmod 644 /var/log/suricata/eve.json
```

### Suricata não está rodando
```bash
sudo systemctl status suricata
sudo systemctl start suricata
```

### Dependências não instaladas
```bash
pip3 install --user -r requirements.txt
```

##  Responsividade

O dashboard é totalmente responsivo e funciona em:
-  Desktop
-  Tablet
-  Mobile

##  Segurança

Por padrão, o servidor aceita conexões de qualquer IP (`0.0.0.0`). Para produção:
1. Configure um firewall
2. Use um servidor web (nginx/Apache) como proxy reverso
3. Configure HTTPS com certificado SSL

---

**Desenvolvido por:** Wilker Junio Coelho Pimenta


