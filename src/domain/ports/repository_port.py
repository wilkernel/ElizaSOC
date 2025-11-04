"""
RepositoryPort - Interface genérica para repositórios
Seguindo padrão Ports & Adapters (Hexagonal Architecture)
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


class RepositoryPort(ABC, Generic[T]):
    """
    Port (interface) genérico para repositórios
    Define operações básicas de persistência
    """
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Salva uma entidade
        
        Args:
            entity: Entidade a ser salva
            
        Returns:
            Entidade salva (pode incluir ID gerado)
        """
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """
        Busca entidade por ID
        
        Args:
            entity_id: ID da entidade
            
        Returns:
            Entidade encontrada ou None
        """
        pass
    
    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[T]:
        """
        Busca todas as entidades com filtros opcionais
        
        Args:
            limit: Limite de resultados
            offset: Offset para paginação
            start_date: Data inicial para filtro
            end_date: Data final para filtro
            
        Returns:
            Lista de entidades
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Conta total de entidades
        
        Returns:
            Total de entidades
        """
        pass
