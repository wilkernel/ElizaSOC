#!/usr/bin/env python3
"""
Script para validar dependências entre camadas seguindo Clean Architecture

Regras:
- Domain não deve importar de nenhuma outra camada
- Application só pode importar de Domain
- Infrastructure só pode importar de Domain
- Presentation pode importar de Application e Domain (mas não Infrastructure diretamente)
"""
import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DependencyValidator:
    """Validador de dependências entre camadas"""
    
    # Definição das camadas
    LAYERS = {
        'domain': 1,
        'application': 2,
        'infrastructure': 3,
        'presentation': 4,
        'common': 0,  # Camada compartilhada
    }
    
    # Regras de dependência permitidas
    ALLOWED_DEPENDENCIES = {
        'domain': [],  # Domain não depende de nada
        'application': ['domain', 'common'],  # Application depende apenas de Domain e Common
        'infrastructure': ['domain', 'common'],  # Infrastructure depende apenas de Domain e Common
        'presentation': ['application', 'domain', 'common'],  # Presentation pode usar Application, Domain, Common
        'common': [],  # Common não depende de outras camadas
    }
    
    def __init__(self, src_dir: Path):
        self.src_dir = src_dir
        self.violations: List[Tuple[str, str, str]] = []
    
    def get_layer(self, filepath: Path) -> str:
        """Determina a camada de um arquivo"""
        parts = filepath.parts
        if 'src' not in parts:
            return None
        
        idx = parts.index('src')
        if idx + 1 < len(parts):
            layer = parts[idx + 1]
            if layer in self.LAYERS:
                return layer
        return None
    
    def extract_imports(self, filepath: Path) -> Set[str]:
        """Extrai imports de um arquivo Python"""
        imports = set()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except Exception as e:
            print(f"Erro ao processar {filepath}: {e}")
        
        return imports
    
    def is_src_import(self, import_name: str) -> bool:
        """Verifica se import é do src/"""
        return import_name.startswith('src.')
    
    def get_imported_layer(self, import_name: str) -> str:
        """Determina a camada de um import"""
        if not self.is_src_import(import_name):
            return None
        
        parts = import_name.split('.')
        if len(parts) >= 2 and parts[1] in self.LAYERS:
            return parts[1]
        return None
    
    def is_allowed_exception(self, filepath: Path, layer: str, imported_layer: str, import_name: str) -> bool:
        """Verifica se é uma exceção permitida (ex: Dependency Injection no factory)"""
        filename = filepath.name
        
        # app_factory.py na presentation pode importar infrastructure para DI
        if layer == 'presentation' and filename == 'app_factory.py' and imported_layer == 'infrastructure':
            return True
        
        # Adapters podem importar de outros adapters/scanners na mesma camada
        if layer == 'infrastructure' and imported_layer == 'infrastructure':
            return True
        
        # Presentation pode importar de presentation (mesma camada)
        if layer == 'presentation' and imported_layer == 'presentation':
            return True
        
        return False
    
    def validate_file(self, filepath: Path) -> None:
        """Valida dependências de um arquivo"""
        layer = self.get_layer(filepath)
        if not layer:
            return
        
        imports = self.extract_imports(filepath)
        allowed = self.ALLOWED_DEPENDENCIES.get(layer, [])
        
        for imp in imports:
            imported_layer = self.get_imported_layer(imp)
            if imported_layer and imported_layer not in allowed:
                # Verificar se é exceção permitida
                if not self.is_allowed_exception(filepath, layer, imported_layer, imp):
                    self.violations.append((
                        str(filepath),
                        layer,
                        f"{imported_layer} (via {imp})"
                    ))
    
    def validate(self) -> bool:
        """Valida todas as dependências"""
        for py_file in self.src_dir.rglob('*.py'):
            # Ignorar __pycache__ e arquivos de teste
            if '__pycache__' in py_file.parts or 'test' in py_file.parts:
                continue
            
            self.validate_file(py_file)
        
        return len(self.violations) == 0
    
    def print_report(self) -> None:
        """Imprime relatório de validação"""
        print("\n" + "="*70)
        print("VALIDAÇÃO DE DEPENDÊNCIAS - CLEAN ARCHITECTURE")
        print("="*70)
        
        if not self.violations:
            print("✅ Nenhuma violação encontrada!")
            print("   As dependências seguem as regras da Clean Architecture.")
        else:
            print(f"❌ {len(self.violations)} violação(ões) encontrada(s):\n")
            
            grouped = {}
            for filepath, layer, violation in self.violations:
                if layer not in grouped:
                    grouped[layer] = []
                grouped[layer].append((filepath, violation))
            
            for layer in sorted(grouped.keys()):
                print(f"\n📦 Camada: {layer.upper()}")
                for filepath, violation in grouped[layer]:
                    rel_path = os.path.relpath(filepath, self.src_dir.parent)
                    print(f"   • {rel_path}")
                    print(f"     ⚠️  Depende de: {violation}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Função principal"""
    src_dir = Path(__file__).parent.parent / 'src'
    
    if not src_dir.exists():
        print(f"❌ Diretório src/ não encontrado: {src_dir}")
        return 1
    
    validator = DependencyValidator(src_dir)
    is_valid = validator.validate()
    validator.print_report()
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    exit(main())
