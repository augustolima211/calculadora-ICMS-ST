"""
Dashboard principal da aplicação
"""
import streamlit as st
from datetime import datetime

def show_dashboard(services):
    """Exibe o dashboard principal"""
    st.header("📊 Dashboard")
    
    try:
        db_manager = services['db_manager']
        
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_figuras = len(db_manager.get_all_figuras_tributarias())
            st.metric("Figuras Tributárias", total_figuras)
        
        with col2:
            # Placeholder para estatísticas de cálculos
            st.metric("Cálculos Realizados", "0")
        
        with col3:
            # Placeholder para total ICMS ST
            st.metric("Total ICMS ST", "R$ 0,00")
        
        with col4:
            # Placeholder para economia
            st.metric("Economia Gerada", "R$ 0,00")
        
        st.divider()
        
        # Informações do sistema
        st.subheader("ℹ️ Informações do Sistema")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.info("""
            **Funcionalidades Disponíveis:**
            - ✅ Cadastro de Figuras Tributárias
            - ✅ Cálculo ICMS ST Manual
            - ✅ Importação de XML NFe
            - ✅ Rateio de Frete por Fora
            - ✅ Exportação para Excel
            """)
        
        with info_col2:
            st.success("""
            **Fórmulas Implementadas:**
            - 🧮 Débito ST: (Valor + IPI + Frete) × (1 + MVA) × (1 - Red.) × 18%
            - 💰 Crédito ICMS: Valor × (1 - Red.) × Alíquota
            - 📈 ICMS ST a Recolher: Débito - Crédito
            - 💵 Custo Final: (Valor + ICMS ST + IPI + Frete) ÷ Qtd
            """)
        
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")