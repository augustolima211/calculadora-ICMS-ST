"""
Componentes de gráficos e visualizações
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from models.resultado_calculo import ResultadoCalculoGeral

def show_estatisticas_calculo(resultado: ResultadoCalculoGeral):
    """Exibe estatísticas do cálculo"""
    st.subheader("📈 Estatísticas do Cálculo")
    
    # Estatísticas por tipo
    itens_com_st = sum(1 for item in resultado.detalhes_itens if item.valor_icms_st_recolher > 0)
    itens_sem_figura = sum(1 for item in resultado.detalhes_itens if not item.possui_figura)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Itens com ST", itens_com_st)
    
    with col2:
        st.metric("Itens sem Figura", itens_sem_figura)
    
    with col3:
        percentual_st = (itens_com_st / resultado.total_itens * 100) if resultado.total_itens > 0 else 0
        st.metric("% com ST", f"{percentual_st:.1f}%")
    
    # Gráfico de distribuição
    if len(resultado.detalhes_itens) > 1:
        df_chart = pd.DataFrame([
            {'Categoria': 'Com ST', 'Quantidade': itens_com_st},
            {'Categoria': 'Sem ST', 'Quantidade': resultado.total_itens - itens_com_st}
        ])
        
        fig = px.pie(df_chart, values='Quantidade', names='Categoria', 
                    title='Distribuição de Itens por ST')
        st.plotly_chart(fig, use_container_width=True)