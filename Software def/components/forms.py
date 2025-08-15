"""
Formulários reutilizáveis
"""
import streamlit as st
from typing import Dict, Any

def form_produto_manual() -> Dict[str, Any]:
    """Formulário para entrada manual de produto"""
    with st.form("produto_manual"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código do Produto*")
            descricao = st.text_input("Descrição*")
            ncm = st.text_input("NCM*", help="8 dígitos")
            quantidade = st.number_input("Quantidade*", min_value=0.01, value=1.0, step=0.01)
        
        with col2:
            valor_unitario = st.number_input("Valor Unitário (R$)*", min_value=0.01, value=1.0, step=0.01)
            valor_ipi = st.number_input("Valor IPI (R$)", min_value=0.0, value=0.0, step=0.01)
            valor_frete = st.number_input("Valor Frete (R$)", min_value=0.0, value=0.0, step=0.01)
            frete_por_fora = st.number_input("Frete por Fora (R$)", min_value=0.0, value=0.0, step=0.01)
        
        submitted = st.form_submit_button("🧮 Calcular", type="primary")
        
        if submitted:
            return {
                'codigo': codigo,
                'descricao': descricao,
                'ncm': ncm,
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'valor_ipi': valor_ipi,
                'valor_frete': valor_frete,
                'frete_por_fora': frete_por_fora
            }
    
    return None