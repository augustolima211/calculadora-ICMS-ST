"""
Modelo para Figura Tributária
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class FiguraTributaria:
    """Representa uma figura tributária para cálculo de ICMS ST"""
    ncm: str
    descricao: str
    tipo_tributacao: str  # 'st' ou 'tributado'
    aliquota_icms_12: float = 12.0
    aliquota_icms_4: float = 4.0
    mva_ajustado_12: float = 0.0
    mva_ajustado_4: float = 0.0
    reducao_bc_icms_st: float = 0.0
    reducao_bc_icms_proprio: float = 0.0
    observacoes: Optional[str] = None
    origem_dados: str = 'manual'
    ativo: bool = True
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    def __post_init__(self):
        if self.data_criacao is None:
            self.data_criacao = datetime.now()
        if self.data_atualizacao is None:
            self.data_atualizacao = datetime.now()
    
    def validar(self) -> list:
        """Valida a figura tributária e retorna lista de erros"""
        erros = []
        
        # Validar NCM
        if not self.ncm or len(self.ncm) != 8 or not self.ncm.isdigit():
            erros.append("NCM deve ter 8 dígitos numéricos")
        
        # Validar descrição
        if not self.descricao or not self.descricao.strip():
            erros.append("Descrição é obrigatória")
        
        # Validar tipo de tributação
        if self.tipo_tributacao not in ['st', 'tributado']:
            erros.append("Tipo de tributação deve ser 'st' ou 'tributado'")
        
        # Validar alíquotas
        if not (0 <= self.aliquota_icms_12 <= 100):
            erros.append("Alíquota ICMS 12% deve estar entre 0 e 100")
        
        if not (0 <= self.aliquota_icms_4 <= 100):
            erros.append("Alíquota ICMS 4% deve estar entre 0 e 100")
        
        # Validar MVAs
        if not (0 <= self.mva_ajustado_12 <= 1000):
            erros.append("MVA ajustado 12% deve estar entre 0 e 1000")
        
        if not (0 <= self.mva_ajustado_4 <= 1000):
            erros.append("MVA ajustado 4% deve estar entre 0 e 1000")
        
        # Validar reduções
        if not (0 <= self.reducao_bc_icms_st <= 100):
            erros.append("Redução BC ICMS ST deve estar entre 0 e 100")
        
        if not (0 <= self.reducao_bc_icms_proprio <= 100):
            erros.append("Redução BC ICMS próprio deve estar entre 0 e 100")
        
        return erros