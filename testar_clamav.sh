#!/bin/bash
# Testa ClamAV com arquivo EICAR (arquivo de teste padrão da indústria)

echo "🧪 Testando ClamAV..."

# Criar arquivo EICAR (arquivo de teste padrão - inofensivo mas detectado como vírus)
TEST_FILE="/tmp/eicar.com"
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > "$TEST_FILE"

echo "📁 Arquivo de teste criado: $TEST_FILE"
echo ""

# Escanear
echo "🔍 Escaneando arquivo..."
clamscan "$TEST_FILE"

SCAN_RESULT=$?

echo ""
if [ $SCAN_RESULT -eq 1 ]; then
    echo "✅ SUCESSO! ClamAV detectou o arquivo de teste corretamente."
    echo "   (Código de retorno 1 = vírus detectado - comportamento esperado)"
elif [ $SCAN_RESULT -eq 0 ]; then
    echo "⚠️  ATENÇÃO: ClamAV não detectou o arquivo de teste."
    echo "   Verifique se as assinaturas estão atualizadas: sudo freshclam"
else
    echo "❌ ERRO durante o escaneamento."
fi

# Limpar
rm -f "$TEST_FILE"
echo ""
echo "🧹 Arquivo de teste removido."

