#!/bin/bash
# Script para configurar ClamAV após instalação
# Autor: Wilker Junio Coelho Pimenta

echo "🔧 Configurando ClamAV..."

# Parar serviços que podem estar usando o log
echo "1/4 - Parando serviços ClamAV..."
sudo systemctl stop clamav-freshclam 2>/dev/null || true
sudo pkill -f freshclam 2>/dev/null || true

# Remover locks
echo "2/4 - Removendo arquivos de lock..."
sudo rm -f /var/log/clamav/freshclam.log.lock 2>/dev/null || true

# Atualizar assinaturas
echo "3/4 - Atualizando assinaturas de vírus..."
echo "   (Isso pode demorar alguns minutos na primeira vez)"
sudo freshclam

# Habilitar atualizações automáticas
echo "4/4 - Configurando atualizações automáticas..."
sudo systemctl enable clamav-freshclam
sudo systemctl start clamav-freshclam

echo ""
echo "✅ ClamAV configurado!"
echo ""
echo "Para testar, execute:"
echo "  echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\$H+H*' > /tmp/eicar.com"
echo "  clamscan /tmp/eicar.com"
echo ""
echo "O arquivo EICAR deve ser detectado como vírus (é um arquivo de teste inofensivo)."

