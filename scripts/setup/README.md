# Scripts de setup

Aqui estão scripts de configuração e teste utilizados para preparar o sistema (Suricata, ClamAV). Eles foram copiados para este diretório para facilitar manutenção e separação das rotinas de runtime do dashboard.

Arquivos incluídos:
- `configurar_suricata.sh` - ajustar suricata.yaml e reiniciar o serviço
- `configurar_clamav.sh` - configurar e atualizar o clamav
- `testar_clamav.sh` - teste rápido EICAR para validar ClamAV
- `testar_integracao_clamav.sh` - teste completo da integração ClamAV + dashboard

Estes scripts podem exigir sudo para executar operações em /etc, /var e systemctl.
