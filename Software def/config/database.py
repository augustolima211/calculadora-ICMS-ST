"""
Configuração do banco de dados SQLite
"""
import sqlite3
from pathlib import Path
import os

# Configuração do banco de dados
def get_db_path():
    """Retorna o caminho do banco de dados baseado no ambiente"""
    try:
        import streamlit as st
        # Tenta usar configuração do Streamlit secrets
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            return st.secrets['database']['db_path']
    except (ImportError, KeyError):
        pass
    
    # Fallback para desenvolvimento local
    return Path(__file__).parent.parent / "data" / "calculadora.db"

# Caminho do banco de dados
DB_PATH = get_db_path()

# Criar diretório data se não existir (apenas para SQLite local)
if isinstance(DB_PATH, Path):
    DB_PATH.parent.mkdir(exist_ok=True)

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de figuras tributárias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS figuras_tributarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ncm TEXT UNIQUE NOT NULL,
            descricao TEXT NOT NULL,
            tipo_tributacao TEXT NOT NULL CHECK (tipo_tributacao IN ('st', 'tributado')),
            aliquota_icms_12 REAL DEFAULT 12.0,
            aliquota_icms_4 REAL DEFAULT 4.0,
            mva_ajustado_12 REAL DEFAULT 0.0,
            mva_ajustado_4 REAL DEFAULT 0.0,
            reducao_bc_icms_st REAL DEFAULT 0.0,
            reducao_bc_icms_proprio REAL DEFAULT 0.0,
            observacoes TEXT,
            origem_dados TEXT DEFAULT 'manual',
            ativo BOOLEAN DEFAULT TRUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de cálculos salvos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculos_icms_st (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem TEXT NOT NULL,
            chave_nfe TEXT,
            total_itens INTEGER NOT NULL,
            total_valor_produtos REAL NOT NULL,
            total_icms_st_debito REAL DEFAULT 0.0,
            total_icms_proprio_credito REAL DEFAULT 0.0,
            total_icms_st_recolher REAL NOT NULL,
            total_custo_final REAL NOT NULL,
            total_frete_por_fora REAL DEFAULT 0.0,
            itens_com_st INTEGER DEFAULT 0,
            itens_sem_figura INTEGER DEFAULT 0,
            observacoes_gerais TEXT,
            data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de itens dos cálculos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_calculo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calculo_id INTEGER NOT NULL,
            codigo_item TEXT NOT NULL,
            descricao TEXT NOT NULL,
            ncm TEXT NOT NULL,
            quantidade REAL NOT NULL,
            valor_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            valor_ipi REAL DEFAULT 0.0,
            valor_frete REAL DEFAULT 0.0,
            valor_frete_fora REAL DEFAULT 0.0,
            tipo_tributacao TEXT,
            aliquota_icms REAL DEFAULT 0.0,
            mva_ajustado REAL DEFAULT 0.0,
            reducao_bc_st REAL DEFAULT 0.0,
            reducao_bc_proprio REAL DEFAULT 0.0,
            base_calculo_st REAL DEFAULT 0.0,
            valor_icms_st_debito REAL DEFAULT 0.0,
            valor_icms_proprio_credito REAL DEFAULT 0.0,
            valor_icms_st_recolher REAL DEFAULT 0.0,
            valor_custo_final REAL DEFAULT 0.0,
            possui_figura BOOLEAN DEFAULT FALSE,
            observacoes TEXT,
            FOREIGN KEY (calculo_id) REFERENCES calculos_icms_st (id)
        )
    """)
    
    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_figuras_ncm ON figuras_tributarias(ncm)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_figuras_ativo ON figuras_tributarias(ativo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_calculos_data ON calculos_icms_st(data_calculo)")
    
    conn.commit()
    conn.close()

def get_connection():
    """Retorna conexão com o banco de dados"""
    return sqlite3.connect(DB_PATH)