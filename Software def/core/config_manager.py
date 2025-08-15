"""
Gerenciador de Configurações de Usuário
"""
from typing import Dict, Any, Optional
from models.user_config import UserConfig
from core.database_manager import DatabaseManager
from utils.logger import SystemLogger

class ConfigManager:
    """Gerenciador centralizado de configurações"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = SystemLogger('config_manager')
        self._current_config: Optional[UserConfig] = None
        self._cache_enabled = True
    
    def load_config(self, user_id: str = "default", force_reload: bool = False) -> UserConfig:
        """Carrega configurações do usuário"""
        try:
            # Usar cache se disponível e não forçar reload
            if not force_reload and self._current_config and self._current_config.user_id == user_id:
                return self._current_config
            
            # Carregar do banco
            config = self.db_manager.get_user_config(user_id)
            
            # Atualizar cache
            if self._cache_enabled:
                self._current_config = config
            
            self.logger.info(f"Configurações carregadas para usuário: {user_id}")
            return config
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            # Retornar configuração padrão em caso de erro
            return UserConfig(user_id=user_id)
    
    def save_config(self, config: UserConfig) -> bool:
        """Salva configurações do usuário"""
        try:
            # Validar configuração
            erros = config.validar()
            if erros:
                self.logger.warning(f"Configurações inválidas: {erros}")
                return False
            
            # Salvar no banco
            success = self.db_manager.save_user_config(config)
            
            # Atualizar cache
            if success and self._cache_enabled:
                self._current_config = config
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def update_config(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza configurações específicas"""
        try:
            # Carregar configuração atual
            config = self.load_config(user_id)
            
            # Aplicar atualizações
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                else:
                    self.logger.warning(f"Campo de configuração desconhecido: {key}")
            
            # Atualizar data de modificação
            from datetime import datetime
            config.data_atualizacao = datetime.now()
            
            # Salvar configuração atualizada
            return self.save_config(config)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configurações: {e}")
            return False
    
    def reset_config(self, user_id: str = "default") -> bool:
        """Reseta configurações para valores padrão"""
        try:
            success = self.db_manager.reset_user_config(user_id)
            
            # Limpar cache
            if success:
                self._current_config = None
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar configurações: {e}")
            return False
    
    def get_config_value(self, user_id: str, key: str, default=None):
        """Obtém valor específico de configuração"""
        try:
            config = self.load_config(user_id)
            return getattr(config, key, default)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter valor de configuração: {e}")
            return default
    
    def apply_to_calculator(self, calculator, user_id: str = "default"):
        """Aplica configurações na calculadora de ICMS"""
        try:
            config = self.load_config(user_id)
            config.aplicar_configuracoes_calculo(calculator)
            self.logger.info("Configurações aplicadas na calculadora")
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar configurações: {e}")
    
    def get_interface_config(self, user_id: str = "default") -> Dict[str, Any]:
        """Retorna configurações específicas da interface"""
        try:
            config = self.load_config(user_id)
            return config.get_configuracoes_interface()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter configurações de interface: {e}")
            return {
                'tema': 'light',
                'idioma': 'pt-BR',
                'mostrar_tooltips': True,
                'mostrar_detalhes_calculo': True,
                'auto_salvar_calculos': True
            }
    
    def get_export_config(self, user_id: str = "default") -> Dict[str, Any]:
        """Retorna configurações específicas de exportação"""
        try:
            config = self.load_config(user_id)
            return config.get_configuracoes_exportacao()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter configurações de exportação: {e}")
            return {
                'formato_padrao': 'xlsx',
                'incluir_graficos': True,
                'incluir_observacoes': True
            }
    
    def enable_cache(self, enabled: bool = True):
        """Habilita/desabilita cache de configurações"""
        self._cache_enabled = enabled
        if not enabled:
            self._current_config = None
    
    def clear_cache(self):
        """Limpa cache de configurações"""
        self._current_config = None