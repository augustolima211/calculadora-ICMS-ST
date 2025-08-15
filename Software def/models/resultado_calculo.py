"""
Modelos para resultados de cálculo
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ResultadoCalculoItem:
    """Resultado do cálculo para um item específico"""
    codigo_item: str
    descricao: str
    ncm: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    valor_ipi: float = 0.0
    valor_frete: float = 0.0
    valor_frete_fora: float = 0.0
    
    # Dados da figura tributária
    tipo_tributacao: str = 'N/A'
    aliquota_icms: float = 0.0
    mva_ajustado: float = 0.0
    reducao_bc_st: float = 0.0
    reducao_bc_proprio: float = 0.0
    
    # Cálculos ICMS ST
    base_calculo_st: float = 0.0
    valor_icms_st_debito: float = 0.0
    valor_icms_proprio_credito: float = 0.0
    valor_icms_st_recolher: float = 0.0
    valor_icms_st: float = 0.0  # Para compatibilidade
    valor_custo_final: float = 0.0
    
    # Validações
    possui_figura: bool = False
    observacoes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Para compatibilidade
        if self.valor_icms_st == 0.0 and self.valor_icms_st_recolher > 0.0:
            self.valor_icms_st = self.valor_icms_st_recolher

@dataclass
class ResultadoCalculoGeral:
    """Resultado geral do cálculo ICMS ST"""
    origem: str
    chave_nfe: Optional[str]
    total_itens: int
    total_valor_produtos: float
    total_icms_st: float
    total_custo_final: float
    itens_com_st: int
    itens_sem_figura: int
    data_calculo: datetime
    detalhes_itens: List[ResultadoCalculoItem]
    observacoes_gerais: List[str] = field(default_factory=list)
    
    # Novos campos para as fórmulas específicas
    total_icms_st_debito: float = 0.0
    total_icms_proprio_credito: float = 0.0
    total_frete_por_fora: float = 0.0
    
    def __post_init__(self):
        # Calcular totais dos novos campos
        self.total_icms_st_debito = sum(item.valor_icms_st_debito for item in self.detalhes_itens)
        self.total_icms_proprio_credito = sum(item.valor_icms_proprio_credito for item in self.detalhes_itens)
        self.total_frete_por_fora = sum(item.valor_frete_fora for item in self.detalhes_itens)
        
        # Para compatibilidade
        if self.total_icms_st == 0.0:
            self.total_icms_st = sum(item.valor_icms_st_recolher for item in self.detalhes_itens)