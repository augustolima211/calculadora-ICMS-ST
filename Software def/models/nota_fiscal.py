"""
Modelos para Nota Fiscal Eletrônica
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class ItemNFe:
    """Representa um item da Nota Fiscal Eletrônica"""
    codigo: str
    descricao: str
    ncm: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    valor_ipi: float = 0.0
    valor_frete: float = 0.0
    
    def __post_init__(self):
        # Validações básicas
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        if self.valor_unitario <= 0:
            raise ValueError("Valor unitário deve ser maior que zero")
        if len(self.ncm) != 8 or not self.ncm.isdigit():
            raise ValueError(f"NCM inválido: {self.ncm}")
    
    def validar(self) -> list:
        """Valida o item e retorna lista de erros"""
        erros = []
        
        if not self.codigo or not self.codigo.strip():
            erros.append("Código do item é obrigatório")
        
        if not self.descricao or not self.descricao.strip():
            erros.append("Descrição do item é obrigatória")
        
        if self.quantidade <= 0:
            erros.append("Quantidade deve ser maior que zero")
        
        if self.valor_unitario <= 0:
            erros.append("Valor unitário deve ser maior que zero")
        
        if len(self.ncm) != 8 or not self.ncm.isdigit():
            erros.append("NCM deve ter 8 dígitos numéricos")
        
        return erros