"""
Exceções customizadas para a calculadora fiscal
"""

class CalculadoraFiscalError(Exception):
    """Exceção base para erros da calculadora fiscal"""
    pass

class ValidationError(CalculadoraFiscalError):
    """Erro de validação de dados"""
    pass

class CalculationError(CalculadoraFiscalError):
    """Erro durante cálculos"""
    pass

class DatabaseError(CalculadoraFiscalError):
    """Erro de banco de dados"""
    pass

class XMLProcessingError(CalculadoraFiscalError):
    """Erro no processamento de XML"""
    pass