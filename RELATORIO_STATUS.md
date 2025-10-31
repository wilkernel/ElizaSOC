# 📊 Relatório de Status do Monitoramento

**Data/Hora da Verificação:** $(date '+%Y-%m-%d %H:%M:%S')

## ✅ Status Atual

### Componentes Verificados

1. **Suricata Service** ✅ ATIVO
   - Serviço rodando corretamente
   - PID: em execução
   - Versão: Suricata 8.0.1 RELEASE

2. **Dependências** ✅ OK
   - `jq` instalado e funcional

3. **Logs do Suricata** ❌ PROBLEMA DE PERMISSÃO
   - Diretório `/var/log/suricata` existe
   - Arquivo `eve.json` NÃO existe
   - Erro nos logs: `Permission denied` ao tentar criar `eve.json`

## ⚠️ Problema Identificado

O Suricata está rodando mas **não consegue criar o arquivo de log** devido a problemas de permissão:

```
E: logopenfile: Error opening file: "/var/log/suricata/eve.json": Permission denied
W: runmodes: output module "eve-log": setup failed
```

## 🔧 Solução

Execute os seguintes comandos para corrigir as permissões:

```bash
# 1. Criar/ajustar diretório de logs com permissões corretas
sudo mkdir -p /var/log/suricata
sudo chown -R suricata:suricata /var/log/suricata
sudo chmod 755 /var/log/suricata

# 2. Reiniciar o serviço Suricata
sudo systemctl restart suricata

# 3. Verificar se o arquivo foi criado
ls -la /var/log/suricata/eve.json

# 4. Executar o monitoramento
bash monitorar_phishing_servico.sh
```

**OU** execute o script de configuração completo:

```bash
sudo bash configurar_suricata.sh
```

## 📝 Próximos Passos

Após corrigir as permissões:

1. **Monitoramento Básico:**
   ```bash
   bash monitorar_phishing_servico.sh
   ```

2. **Monitoramento Contínuo com E-mail:**
   ```bash
   bash alertas_email.sh &
   ```

3. **Verificar Status Novamente:**
   ```bash
   bash verificar_status.sh
   ```

## 🔍 Verificação Adicional

Para verificar se o problema foi resolvido:

```bash
# Verificar status do serviço
systemctl status suricata

# Verificar se o arquivo existe e tem conteúdo
sudo ls -lh /var/log/suricata/eve.json

# Testar leitura do arquivo (primeiras linhas)
sudo head -5 /var/log/suricata/eve.json | jq .
```

---

**Nota:** Este relatório foi gerado automaticamente pelo script `verificar_status.sh`

