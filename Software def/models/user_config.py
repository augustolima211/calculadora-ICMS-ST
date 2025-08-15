"""
Modelo para Configurações de Usuário
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, ROUND_CEILING, ROUND_FLOOR

@dataclass
class UserConfig:
    """Configurações personalizáveis do usuário"""
    
    # Identificação
    user_id: str = "default"
    nome_usuario: str = "Usuário Padrão"
    
    # Configurações de Cálculo
    precisao_decimal: int = 2
    tipo_arredondamento: str = "ROUND_HALF_UP"  # ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, etc.
    aliquota_icms_padrao_12: float = 12.0
    aliquota_icms_padrao_4: float = 4.0
    considerar_reducao_bc_automatica: bool = True
    aplicar_mva_ajustado_automatico: bool = True
    
    # Configurações de Interface
    tema: str = "light"  # light, dark
    idioma: str = "pt-BR"  # pt-BR, en-US
    mostrar_tooltips: bool = True
    mostrar_detalhes_calculo: bool = True
    auto_salvar_calculos: bool = True
    
    # Configurações de Exportação
    formato_exportacao_padrao: str = "xlsx"  # xlsx, csv, pdf
    incluir_graficos_exportacao: bool = True
    incluir_observacoes_exportacao: bool = True
    
    # Configurações de Sistema
    backup_automatico: bool = False
    intervalo_backup_dias: int = 7
    manter_historico_dias: int = 365
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Configurações de Validação
    validar_ncm_automatico: bool = True
    alertar_figura_nao_encontrada: bool = True
    alertar_valores_zerados: bool = True
    
    # Configurações Avançadas
    usar_cache_figuras: bool = True
    timeout_conexao_segundos: int = 30
    max_itens_por_calculo: int = 1000
    
    # Metadados
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    versao_config: str = "1.0"
    
    def __post_init__(self):
        if self.data_criacao is None:
            self.data_criacao = datetime.now()
        if self.data_atualizacao is None:
            self.data_atualizacao = datetime.now()
    
    def get_decimal_rounding(self):
        """Retorna o tipo de arredondamento do Decimal"""
        rounding_map = {
            "ROUND_HALF_UP": ROUND_HALF_UP,
            "ROUND_DOWN": ROUND_DOWN,
            "ROUND_UP": ROUND_UP,
            "ROUND_CEILING": ROUND_CEILING,
            "ROUND_FLOOR": ROUND_FLOOR
        }
        return rounding_map.get(self.tipo_arredondamento, ROUND_HALF_UP)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configurações para dicionário"""
        return {
            'user_id': self.user_id,
            'nome_usuario': self.nome_usuario,
            'precisao_decimal': self.precisao_decimal,
            'tipo_arredondamento': self.tipo_arredondamento,
            'aliquota_icms_padrao_12': self.aliquota_icms_padrao_12,
            'aliquota_icms_padrao_4': self.aliquota_icms_padrao_4,
            'considerar_reducao_bc_automatica': self.considerar_reducao_bc_automatica,
            'aplicar_mva_ajustado_automatico': self.aplicar_mva_ajustado_automatico,
            'tema': self.tema,
            'idioma': self.idioma,
            'mostrar_tooltips': self.mostrar_tooltips,
            'mostrar_detalhes_calculo': self.mostrar_detalhes_calculo,
            'auto_salvar_calculos': self.auto_salvar_calculos,
            'formato_exportacao_padrao': self.formato_exportacao_padrao,
            'incluir_graficos_exportacao': self.incluir_graficos_exportacao,
            'incluir_observacoes_exportacao': self.incluir_observacoes_exportacao,
            'backup_automatico': self.backup_automatico,
            'intervalo_backup_dias': self.intervalo_backup_dias,
            'manter_historico_dias': self.manter_historico_dias,
            'log_level': self.log_level,
            'validar_ncm_automatico': self.validar_ncm_automatico,
            'alertar_figura_nao_encontrada': self.alertar_figura_nao_encontrada,
            'alertar_valores_zerados': self.alertar_valores_zerados,
            'usar_cache_figuras': self.usar_cache_figuras,
            'timeout_conexao_segundos': self.timeout_conexao_segundos,
            'max_itens_por_calculo': self.max_itens_por_calculo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'versao_config': self.versao_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserConfig':
        """Cria configuração a partir de dicionário"""
        # Converter datas
        if data.get('data_criacao'):
            data['data_criacao'] = datetime.fromisoformat(data['data_criacao'])
        if data.get('data_atualizacao'):
            data['data_atualizacao'] = datetime.fromisoformat(data['data_atualizacao'])
        
        return cls(**data)
    
    def validar(self) -> list:
        """Valida as configurações e retorna lista de erros"""
        erros = []
        
        # Validar precisão decimal
        if not isinstance(self.precisao_decimal, int) or self.precisao_decimal < 0 or self.precisao_decimal > 10:
            erros.append("Precisão decimal deve ser um número inteiro entre 0 e 10")
        
        # Validar alíquotas
        if not (0 <= self.aliquota_icms_padrao_12 <= 100):
            erros.append("Alíquota ICMS 12% deve estar entre 0 e 100")
        
        if not (0 <= self.aliquota_icms_padrao_4 <= 100):
            erros.append("Alíquota ICMS 4% deve estar entre 0 e 100")
        
        # Validar tema
        if self.tema not in ["light", "dark"]:
            erros.append("Tema deve ser 'light' ou 'dark'")
        
        # Validar idioma
        if self.idioma not in ["pt-BR", "en-US"]:
            erros.append("Idioma deve ser 'pt-BR' ou 'en-US'")
        
        # Validar formato de exportação
        if self.formato_exportacao_padrao not in ["xlsx", "csv", "pdf"]:
            erros.append("Formato de exportação deve ser 'xlsx', 'csv' ou 'pdf'")
        
        # Validar log level
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            erros.append("Log level deve ser 'DEBUG', 'INFO', 'WARNING' ou 'ERROR'")
        
        # Validar intervalos
        if self.intervalo_backup_dias < 1:
            erros.append("Intervalo de backup deve ser pelo menos 1 dia")
        
        if self.manter_historico_dias < 1:
            erros.append("Período de histórico deve ser pelo menos 1 dia")
        
        if self.timeout_conexao_segundos < 1:
            erros.append("Timeout de conexão deve ser pelo menos 1 segundo")
        
        if self.max_itens_por_calculo < 1:
            erros.append("Máximo de itens por cálculo deve ser pelo menos 1")
        
        return erros
    
    def aplicar_configuracoes_calculo(self, calculadora):
        """Aplica configurações na calculadora de ICMS"""
        # Configurar precisão e arredondamento
        calculadora.precisao_decimal = self.precisao_decimal
        calculadora.tipo_arredondamento = self.get_decimal_rounding()
        
        # Configurar alíquotas padrão
        calculadora.aliquota_icms_12_padrao = self.aliquota_icms_padrao_12
        calculadora.aliquota_icms_4_padrao = self.aliquota_icms_padrao_4
        
        # Configurar comportamentos automáticos
        calculadora.aplicar_reducao_automatica = self.considerar_reducao_bc_automatica
        calculadora.aplicar_mva_automatico = self.aplicar_mva_ajustado_automatico
    
    def get_configuracoes_interface(self) -> Dict[str, Any]:
        """Retorna configurações específicas da interface"""
        return {
            'tema': self.tema,
            'idioma': self.idioma,
            'mostrar_tooltips': self.mostrar_tooltips,
            'mostrar_detalhes_calculo': self.mostrar_detalhes_calculo,
            'auto_salvar_calculos': self.auto_salvar_calculos
        }
    
    def get_configuracoes_exportacao(self) -> Dict[str, Any]:
        """Retorna configurações específicas de exportação"""
        return {
            'formato_padrao': self.formato_exportacao_padrao,
            'incluir_graficos': self.incluir_graficos_exportacao,
            'incluir_observacoes': self.incluir_observacoes_exportacao
        }