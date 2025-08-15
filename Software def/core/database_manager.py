"""
Gerenciador do banco de dados SQLite
"""
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from config.database import get_connection, init_database
from models.figura_tributaria import FiguraTributaria
from models.resultado_calculo import ResultadoCalculoGeral, ResultadoCalculoItem
from models.user_config import UserConfig
from utils.logger import SystemLogger
from utils.exceptions import DatabaseError

class DatabaseManager:
    """Gerenciador do banco de dados"""
    
    def __init__(self):
        self.logger = SystemLogger('database_manager')
        # Inicializar banco se necessário
        init_database()
    
    def init_database(self):
        """Inicializa o banco de dados (método wrapper)"""
        try:
            init_database()
            self.logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro na inicialização do banco: {e}")
            raise
    
    def save_figura_tributaria(self, figura: FiguraTributaria) -> bool:
        """Salva figura tributária no banco"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO figuras_tributarias (
                    ncm, descricao, tipo_tributacao, aliquota_icms_12, aliquota_icms_4,
                    mva_ajustado_12, mva_ajustado_4, reducao_bc_icms_st, reducao_bc_icms_proprio,
                    observacoes, origem_dados, ativo, data_atualizacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                figura.ncm, figura.descricao, figura.tipo_tributacao,
                figura.aliquota_icms_12, figura.aliquota_icms_4,
                figura.mva_ajustado_12, figura.mva_ajustado_4,
                figura.reducao_bc_icms_st, figura.reducao_bc_icms_proprio,
                figura.observacoes, figura.origem_dados, figura.ativo,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Figura tributária salva: NCM {figura.ncm}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar figura tributária: {e}")
            raise DatabaseError(f"Falha ao salvar figura: {e}")
    
    def get_figura_tributaria(self, ncm: str) -> Optional[FiguraTributaria]:
        """Busca figura tributária por NCM"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ncm, descricao, tipo_tributacao, aliquota_icms_12, aliquota_icms_4,
                       mva_ajustado_12, mva_ajustado_4, reducao_bc_icms_st, reducao_bc_icms_proprio,
                       observacoes, origem_dados, ativo, data_criacao, data_atualizacao
                FROM figuras_tributarias 
                WHERE ncm = ? AND ativo = 1
            """, (ncm,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return FiguraTributaria(
                    ncm=row[0],
                    descricao=row[1],
                    tipo_tributacao=row[2],
                    aliquota_icms_12=row[3],
                    aliquota_icms_4=row[4],
                    mva_ajustado_12=row[5],
                    mva_ajustado_4=row[6],
                    reducao_bc_icms_st=row[7],
                    reducao_bc_icms_proprio=row[8],
                    observacoes=row[9],
                    origem_dados=row[10],
                    ativo=bool(row[11]),
                    data_criacao=datetime.fromisoformat(row[12]) if row[12] else None,
                    data_atualizacao=datetime.fromisoformat(row[13]) if row[13] else None
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar figura tributária: {e}")
            return None
    
    def get_all_figuras_tributarias(self) -> Dict[str, FiguraTributaria]:
        """Retorna todas as figuras tributárias ativas"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ncm, descricao, tipo_tributacao, aliquota_icms_12, aliquota_icms_4,
                       mva_ajustado_12, mva_ajustado_4, reducao_bc_icms_st, reducao_bc_icms_proprio,
                       observacoes, origem_dados, ativo, data_criacao, data_atualizacao
                FROM figuras_tributarias 
                WHERE ativo = 1
                ORDER BY ncm
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            figuras = {}
            for row in rows:
                figura = FiguraTributaria(
                    ncm=row[0],
                    descricao=row[1],
                    tipo_tributacao=row[2],
                    aliquota_icms_12=row[3],
                    aliquota_icms_4=row[4],
                    mva_ajustado_12=row[5],
                    mva_ajustado_4=row[6],
                    reducao_bc_icms_st=row[7],
                    reducao_bc_icms_proprio=row[8],
                    observacoes=row[9],
                    origem_dados=row[10],
                    ativo=bool(row[11]),
                    data_criacao=datetime.fromisoformat(row[12]) if row[12] else None,
                    data_atualizacao=datetime.fromisoformat(row[13]) if row[13] else None
                )
                figuras[figura.ncm] = figura
            
            return figuras
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar figuras tributárias: {e}")
            return {}
    
    def save_calculo(self, resultado: ResultadoCalculoGeral) -> int:
        """Salva resultado de cálculo no banco"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Salvar cálculo principal
            cursor.execute("""
                INSERT INTO calculos_icms_st (
                    origem, chave_nfe, total_itens, total_valor_produtos,
                    total_icms_st_debito, total_icms_proprio_credito, total_icms_st_recolher,
                    total_custo_final, total_frete_por_fora, itens_com_st, itens_sem_figura,
                    observacoes_gerais, data_calculo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resultado.origem, resultado.chave_nfe, resultado.total_itens,
                resultado.total_valor_produtos, resultado.total_icms_st_debito,
                resultado.total_icms_proprio_credito, resultado.total_icms_st,
                resultado.total_custo_final, resultado.total_frete_por_fora,
                resultado.itens_com_st, resultado.itens_sem_figura,
                '\n'.join(resultado.observacoes_gerais), resultado.data_calculo
            ))
            
            calculo_id = cursor.lastrowid
            
            # Salvar itens do cálculo
            for item in resultado.detalhes_itens:
                cursor.execute("""
                    INSERT INTO itens_calculo (
                        calculo_id, codigo_item, descricao, ncm, quantidade, valor_unitario,
                        valor_total, valor_ipi, valor_frete, valor_frete_fora, tipo_tributacao,
                        aliquota_icms, mva_ajustado, reducao_bc_st, reducao_bc_proprio,
                        base_calculo_st, valor_icms_st_debito, valor_icms_proprio_credito,
                        valor_icms_st_recolher, valor_custo_final, possui_figura, observacoes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    calculo_id, item.codigo_item, item.descricao, item.ncm,
                    item.quantidade, item.valor_unitario, item.valor_total,
                    item.valor_ipi, item.valor_frete, item.valor_frete_fora,
                    item.tipo_tributacao, item.aliquota_icms, item.mva_ajustado,
                    item.reducao_bc_st, item.reducao_bc_proprio, item.base_calculo_st,
                    item.valor_icms_st_debito, item.valor_icms_proprio_credito,
                    item.valor_icms_st_recolher, item.valor_custo_final,
                    item.possui_figura, '\n'.join(item.observacoes)
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cálculo salvo com ID: {calculo_id}")
            return calculo_id
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar cálculo: {e}")
            raise DatabaseError(f"Falha ao salvar cálculo: {e}")
    
    def get_estatisticas(self) -> Dict[str, any]:
        """Retorna estatísticas do banco"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Contar figuras
            cursor.execute("SELECT COUNT(*) FROM figuras_tributarias WHERE ativo = 1")
            total_figuras = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM figuras_tributarias WHERE ativo = 1 AND tipo_tributacao = 'st'")
            figuras_st = cursor.fetchone()[0]
            
            # Contar cálculos
            cursor.execute("SELECT COUNT(*) FROM calculos_icms_st")
            total_calculos = cursor.fetchone()[0]
            
            # Últimos cálculos
            cursor.execute("""
                SELECT data_calculo, total_icms_st_recolher 
                FROM calculos_icms_st 
                ORDER BY data_calculo DESC 
                LIMIT 5
            """)
            ultimos_calculos = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_figuras': total_figuras,
                'figuras_st': figuras_st,
                'total_calculos': total_calculos,
                'ultimos_calculos': ultimos_calculos
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar estatísticas: {e}")
            return {}
    
    def save_user_config(self, config: UserConfig) -> bool:
        """Salva configurações de usuário no banco"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_configs (
                    user_id TEXT PRIMARY KEY,
                    nome_usuario TEXT NOT NULL,
                    precisao_decimal INTEGER DEFAULT 2,
                    tipo_arredondamento TEXT DEFAULT 'ROUND_HALF_UP',
                    aliquota_icms_padrao_12 REAL DEFAULT 12.0,
                    aliquota_icms_padrao_4 REAL DEFAULT 4.0,
                    considerar_reducao_bc_automatica BOOLEAN DEFAULT 1,
                    aplicar_mva_ajustado_automatico BOOLEAN DEFAULT 1,
                    tema TEXT DEFAULT 'light',
                    idioma TEXT DEFAULT 'pt-BR',
                    mostrar_tooltips BOOLEAN DEFAULT 1,
                    mostrar_detalhes_calculo BOOLEAN DEFAULT 1,
                    auto_salvar_calculos BOOLEAN DEFAULT 1,
                    formato_exportacao_padrao TEXT DEFAULT 'xlsx',
                    incluir_graficos_exportacao BOOLEAN DEFAULT 1,
                    incluir_observacoes_exportacao BOOLEAN DEFAULT 1,
                    backup_automatico BOOLEAN DEFAULT 0,
                    intervalo_backup_dias INTEGER DEFAULT 7,
                    manter_historico_dias INTEGER DEFAULT 365,
                    log_level TEXT DEFAULT 'INFO',
                    validar_ncm_automatico BOOLEAN DEFAULT 1,
                    alertar_figura_nao_encontrada BOOLEAN DEFAULT 1,
                    alertar_valores_zerados BOOLEAN DEFAULT 1,
                    usar_cache_figuras BOOLEAN DEFAULT 1,
                    timeout_conexao_segundos INTEGER DEFAULT 30,
                    max_itens_por_calculo INTEGER DEFAULT 1000,
                    data_criacao TEXT,
                    data_atualizacao TEXT,
                    versao_config TEXT DEFAULT '1.0'
                )
            """)
            
            # Salvar configurações
            config_dict = config.to_dict()
            cursor.execute("""
                INSERT OR REPLACE INTO user_configs (
                    user_id, nome_usuario, precisao_decimal, tipo_arredondamento,
                    aliquota_icms_padrao_12, aliquota_icms_padrao_4,
                    considerar_reducao_bc_automatica, aplicar_mva_ajustado_automatico,
                    tema, idioma, mostrar_tooltips, mostrar_detalhes_calculo,
                    auto_salvar_calculos, formato_exportacao_padrao,
                    incluir_graficos_exportacao, incluir_observacoes_exportacao,
                    backup_automatico, intervalo_backup_dias, manter_historico_dias,
                    log_level, validar_ncm_automatico, alertar_figura_nao_encontrada,
                    alertar_valores_zerados, usar_cache_figuras,
                    timeout_conexao_segundos, max_itens_por_calculo,
                    data_criacao, data_atualizacao, versao_config
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config_dict['user_id'], config_dict['nome_usuario'],
                config_dict['precisao_decimal'], config_dict['tipo_arredondamento'],
                config_dict['aliquota_icms_padrao_12'], config_dict['aliquota_icms_padrao_4'],
                config_dict['considerar_reducao_bc_automatica'], config_dict['aplicar_mva_ajustado_automatico'],
                config_dict['tema'], config_dict['idioma'],
                config_dict['mostrar_tooltips'], config_dict['mostrar_detalhes_calculo'],
                config_dict['auto_salvar_calculos'], config_dict['formato_exportacao_padrao'],
                config_dict['incluir_graficos_exportacao'], config_dict['incluir_observacoes_exportacao'],
                config_dict['backup_automatico'], config_dict['intervalo_backup_dias'],
                config_dict['manter_historico_dias'], config_dict['log_level'],
                config_dict['validar_ncm_automatico'], config_dict['alertar_figura_nao_encontrada'],
                config_dict['alertar_valores_zerados'], config_dict['usar_cache_figuras'],
                config_dict['timeout_conexao_segundos'], config_dict['max_itens_por_calculo'],
                config_dict['data_criacao'], config_dict['data_atualizacao'],
                config_dict['versao_config']
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Configurações salvas para usuário: {config.user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            raise DatabaseError(f"Falha ao salvar configurações: {e}")
    
    def get_user_config(self, user_id: str = "default") -> UserConfig:
        """Busca configurações de usuário por ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, nome_usuario, precisao_decimal, tipo_arredondamento,
                       aliquota_icms_padrao_12, aliquota_icms_padrao_4,
                       considerar_reducao_bc_automatica, aplicar_mva_ajustado_automatico,
                       tema, idioma, mostrar_tooltips, mostrar_detalhes_calculo,
                       auto_salvar_calculos, formato_exportacao_padrao,
                       incluir_graficos_exportacao, incluir_observacoes_exportacao,
                       backup_automatico, intervalo_backup_dias, manter_historico_dias,
                       log_level, validar_ncm_automatico, alertar_figura_nao_encontrada,
                       alertar_valores_zerados, usar_cache_figuras,
                       timeout_conexao_segundos, max_itens_por_calculo,
                       data_criacao, data_atualizacao, versao_config
                FROM user_configs 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return UserConfig(
                    user_id=row[0],
                    nome_usuario=row[1],
                    precisao_decimal=row[2],
                    tipo_arredondamento=row[3],
                    aliquota_icms_padrao_12=row[4],
                    aliquota_icms_padrao_4=row[5],
                    considerar_reducao_bc_automatica=bool(row[6]),
                    aplicar_mva_ajustado_automatico=bool(row[7]),
                    tema=row[8],
                    idioma=row[9],
                    mostrar_tooltips=bool(row[10]),
                    mostrar_detalhes_calculo=bool(row[11]),
                    auto_salvar_calculos=bool(row[12]),
                    formato_exportacao_padrao=row[13],
                    incluir_graficos_exportacao=bool(row[14]),
                    incluir_observacoes_exportacao=bool(row[15]),
                    backup_automatico=bool(row[16]),
                    intervalo_backup_dias=row[17],
                    manter_historico_dias=row[18],
                    log_level=row[19],
                    validar_ncm_automatico=bool(row[20]),
                    alertar_figura_nao_encontrada=bool(row[21]),
                    alertar_valores_zerados=bool(row[22]),
                    usar_cache_figuras=bool(row[23]),
                    timeout_conexao_segundos=row[24],
                    max_itens_por_calculo=row[25],
                    data_criacao=datetime.fromisoformat(row[26]) if row[26] else None,
                    data_atualizacao=datetime.fromisoformat(row[27]) if row[27] else None,
                    versao_config=row[28]
                )
            else:
                # Retornar configuração padrão se não encontrar
                config_padrao = UserConfig(user_id=user_id)
                self.save_user_config(config_padrao)  # Salvar configuração padrão
                return config_padrao
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar configurações: {e}")
            # Retornar configuração padrão em caso de erro
            return UserConfig(user_id=user_id)
    
    def reset_user_config(self, user_id: str = "default") -> bool:
        """Reseta configurações para valores padrão"""
        try:
            config_padrao = UserConfig(user_id=user_id)
            return self.save_user_config(config_padrao)
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar configurações: {e}")
            return False
    
    def export_user_config(self, user_id: str = "default") -> Dict:
        """Exporta configurações de usuário como dicionário"""
        try:
            config = self.get_user_config(user_id)
            return config.to_dict()
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar configurações: {e}")
            return {}
    
    def import_user_config(self, config_dict: Dict, user_id: str = "default") -> bool:
        """Importa configurações de usuário a partir de dicionário"""
        try:
            # Validar e criar configuração
            config_dict['user_id'] = user_id
            config = UserConfig.from_dict(config_dict)
            
            # Validar configuração
            erros = config.validar()
            if erros:
                self.logger.warning(f"Configurações com erros: {erros}")
                return False
            
            return self.save_user_config(config)
            
        except Exception as e:
            self.logger.error(f"Erro ao importar configurações: {e}")
            return False
    
    def get_config_history(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        """Retorna histórico de alterações de configuração"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Criar tabela de histórico se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    campo_alterado TEXT NOT NULL,
                    valor_anterior TEXT,
                    valor_novo TEXT,
                    data_alteracao TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user_configs (user_id)
                )
            """)
            
            cursor.execute("""
                SELECT campo_alterado, valor_anterior, valor_novo, data_alteracao
                FROM config_history 
                WHERE user_id = ?
                ORDER BY data_alteracao DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'campo': row[0],
                'valor_anterior': row[1],
                'valor_novo': row[2],
                'data_alteracao': row[3]
            } for row in rows]
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar histórico: {e}")
            return []
    
    def get_estatisticas(self) -> Dict[str, any]:
        """Retorna estatísticas do banco"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Contar figuras
            cursor.execute("SELECT COUNT(*) FROM figuras_tributarias WHERE ativo = 1")
            total_figuras = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM figuras_tributarias WHERE ativo = 1 AND tipo_tributacao = 'st'")
            figuras_st = cursor.fetchone()[0]
            
            # Contar cálculos
            cursor.execute("SELECT COUNT(*) FROM calculos_icms_st")
            total_calculos = cursor.fetchone()[0]
            
            # Últimos cálculos
            cursor.execute("""
                SELECT data_calculo, total_icms_st_recolher 
                FROM calculos_icms_st 
                ORDER BY data_calculo DESC 
                LIMIT 5
            """)
            ultimos_calculos = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_figuras': total_figuras,
                'figuras_st': figuras_st,
                'total_calculos': total_calculos,
                'ultimos_calculos': ultimos_calculos
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar estatísticas: {e}")
            return {}
        