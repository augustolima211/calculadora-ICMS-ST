"""
Validadores para a calculadora fiscal
"""
import re
from typing import List, Any

class Validators:
    """Classe com métodos de validação"""
    
    @staticmethod
    def validar_ncm(ncm: str) -> bool:
        """Valida formato do NCM"""
        if not ncm:
            return False
        
        # Remove espaços e caracteres especiais
        ncm_limpo = re.sub(r'[^0-9]', '', str(ncm))
        
        # NCM deve ter 8 dígitos
        return len(ncm_limpo) == 8 and ncm_limpo.isdigit()
    
    @staticmethod
    def normalizar_ncm(ncm: str) -> str:
        """Normaliza NCM removendo caracteres especiais"""
        return re.sub(r'[^0-9]', '', str(ncm))
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ"""
        if not cnpj:
            return False
        
        # Remove caracteres especiais
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        # CNPJ deve ter 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Validação básica (não implementa dígito verificador)
        return cnpj.isdigit()
    
    @staticmethod
    def validar_chave_nfe(chave: str) -> bool:
        """Valida chave da NFe"""
        if not chave:
            return False
        
        # Remove espaços
        chave = chave.strip()
        
        # Chave deve ter 44 dígitos
        return len(chave) == 44 and chave.isdigit()
    
    @staticmethod
    def validar_valor_monetario(valor: Any) -> bool:
        """Valida se o valor é um número válido para valores monetários"""
        try:
            valor_float = float(valor)
            return valor_float >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_percentual(valor: Any, min_val: float = 0, max_val: float = 100) -> bool:
        """Valida se o valor é um percentual válido"""
        try:
            valor_float = float(valor)
            return min_val <= valor_float <= max_val
        except (ValueError, TypeError):
            return False