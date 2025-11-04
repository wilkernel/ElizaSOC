# 🚀 Guia Rápido de Testes - ElizaSOC

## Teste Rápido (5 minutos)

### 1. Iniciar o Dashboard

```bash
# Terminal 1
python3 app.py
```

Aguarde a mensagem indicando que o servidor está rodando em `http://localhost:5000`

### 2. Gerar Dados de Teste

```bash
# Terminal 2 - Gerar 20 alertas rapidamente
./test_system.sh generate 20 0.1

# OU usar o script Python diretamente
python3 scripts/generate_test_alerts.py -n 20 -i 0.1
```

### 3. Verificar no Dashboard

1. Abra `http://localhost:5000` no navegador
2. Verifique os **cards de estatísticas** no topo (devem mostrar números)
3. Veja os **gráficos** na seção de métricas
4. Vá para a aba **"Todos os Alertas"** - deve ter dados

### 4. Testar Monitoramento em Tempo Real

```bash
# Terminal 2 - Gerar alertas continuamente
./test_system.sh continuous 1

# OU
python3 scripts/generate_test_alerts.py --continuous -i 1
```

No Dashboard:
1. Vá para a aba **"Logs em Tempo Real"**
2. Clique em **"Iniciar Monitoramento"**
3. Você deve ver: **"✓ Conectado ao stream de logs"**
4. Os alertas aparecerão em tempo real conforme são gerados

### 5. Testar Protocolos Individuais

1. Vá para a aba **"Protocolos Monitorados"**
2. Clique em qualquer card (ex: TCP, HTTP/HTTPS, DNS)
3. Um modal abrirá mostrando:
   - Estatísticas específicas do protocolo
   - Gráficos filtrados
   - Tabelas com top assinaturas e IPs
   - Alertas recentes

## Comandos Úteis

### Script Helper (Recomendado)

```bash
# Gerar dados de teste
./test_system.sh generate 50 0.5

# Gerar continuamente
./test_system.sh continuous 1

# Ver estatísticas
./test_system.sh stats

# Verificar se dashboard está rodando
./test_system.sh check

# Teste completo automatizado
./test_system.sh test
```

### Script Python Direto

```bash
# Gerar 10 alertas
python3 scripts/generate_test_alerts.py

# Gerar 100 alertas rapidamente
python3 scripts/generate_test_alerts.py -n 100 -i 0.1

# Gerar apenas alertas (sem flows/DNS)
python3 scripts/generate_test_alerts.py -t alert -n 50

# Gerar continuamente
python3 scripts/generate_test_alerts.py --continuous -i 2

# Salvar em arquivo local (sem sudo)
python3 scripts/generate_test_alerts.py -f ~/eve_test.json -n 20
```

## Troubleshooting

### Problema: "Arquivo não encontrado" ou "Sem permissão"

**Solução 1 - Usar arquivo local:**
```bash
python3 scripts/generate_test_alerts.py -f ~/eve_test.json -n 20
```

**Solução 2 - Criar arquivo com permissões:**
```bash
sudo touch /var/log/suricata/eve.json
sudo chmod 644 /var/log/suricata/eve.json
sudo python3 scripts/generate_test_alerts.py -n 10
```

### Problema: Stream não funciona

1. Verifique se o arquivo existe:
   ```bash
   ls -la /var/log/suricata/eve.json
   ```

2. Verifique se há novos alertas sendo adicionados:
   ```bash
   tail -f /var/log/suricata/eve.json
   ```

3. Abra o console do navegador (F12) e verifique erros

4. Certifique-se de que o dashboard está rodando

### Problema: Dashboard não mostra dados

1. Verifique se os alertas foram gerados:
   ```bash
   ./test_system.sh stats
   ```

2. Verifique se o arquivo está no local correto:
   - Padrão: `/var/log/suricata/eve.json`
   - Ou o caminho configurado no código

3. Recarregue a página do dashboard (Ctrl+F5)

## Estrutura de Teste Completo

### Cenário 1: Teste Básico
```bash
# Terminal 1
python3 app.py

# Terminal 2
./test_system.sh generate 30 0.3
```

### Cenário 2: Teste de Streaming
```bash
# Terminal 1
python3 app.py

# Terminal 2
./test_system.sh continuous 1

# No navegador: Aba "Logs em Tempo Real" → "Iniciar Monitoramento"
```

### Cenário 3: Teste de Protocolos
```bash
# Terminal 2
./test_system.sh generate 100 0.1

# No navegador: Aba "Protocolos Monitorados" → Clicar em qualquer card
```

## Verificação Rápida

Execute este comando para verificar se tudo está OK:

```bash
./test_system.sh test
```

Isso irá:
1. ✅ Verificar Python
2. ✅ Gerar dados de teste
3. ✅ Mostrar estatísticas
4. ✅ Verificar se dashboard está rodando

## Próximos Passos

Depois de testar com dados simulados:

1. **Configurar Suricata real** para monitorar tráfego de rede
2. **Verificar regras do Suricata** em `/etc/suricata/rules/`
3. **Monitorar logs reais** do Suricata
4. **Integrar com dados de produção**

## Recursos Adicionais

- **Documentação completa**: `scripts/README_TESTES.md`
- **Scripts de setup**: `scripts/setup/`
- **Documentação do dashboard**: `docs/DASHBOARD_README.md`

