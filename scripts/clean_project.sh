#!/usr/bin/env bash
# Script de limpeza do projeto ElizaSOC
# Remove artefatos de build, cache, e arquivos temporários

set -e

echo "🧹 Limpando projeto ElizaSOC..."

# Remover diretórios __pycache__
echo "Removendo __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remover arquivos .pyc
echo "Removendo arquivos .pyc..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Remover caches de pytest
echo "Removendo caches de pytest..."
rm -rf .pytest_cache 2>/dev/null || true

# Remover cobertura HTML
echo "Removendo relatórios de cobertura..."
rm -rf htmlcov .coverage 2>/dev/null || true

# Remover ambientes virtuais
echo "Removendo ambientes virtuais..."
rm -rf venv .venv env ENV 2>/dev/null || true

# Remover arquivos temporários
echo "Removendo arquivos temporários..."
rm -rf *.zip *.tar.gz *.egg-info dist build 2>/dev/null || true

# Remover logs temporários (manter logs/ mas limpar conteúdo antigo)
if [ -d "logs" ]; then
    echo "Limpando logs antigos..."
    find logs -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
fi

# Remover arquivos de backup
echo "Removendo arquivos de backup..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.bak.*" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true

# Remover .gitignore.save se existir
rm -f .gitignore.save 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo ""
echo "📊 Status do repositório:"
git status --short 2>/dev/null || echo "(não é um repositório git)"
