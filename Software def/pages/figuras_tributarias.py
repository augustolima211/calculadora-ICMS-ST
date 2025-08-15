"""
Interface de gerenciamento de figuras tributárias
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from models.figura_tributaria import FiguraTributaria

def show_figuras_tributarias(services):
    """Exibe a interface de figuras tributárias"""
    st.header("📋 Figuras Tributárias")
    
    # Abas para cadastro e listagem
    tab1, tab2 = st.tabs(["➕ Cadastrar", "📋 Listar"])
    
    with tab1:
        show_cadastro_figura(services)
    
    with tab2:
        show_lista_figuras(services)

def show_cadastro_figura(services):
    """Interface para cadastro de figura tributária"""
    st.subheader("➕ Cadastrar Figura Tributária")
    
    with st.form("cadastro_figura"):
        col1, col2 = st.columns(2)
        
        with col1:
            ncm = st.text_input("NCM*", help="8 dígitos")
            descricao = st.text_input("Descrição*")
            tipo_tributacao = st.selectbox(
                "Tipo de Tributação*",
                ["st", "tributado"],
                format_func=lambda x: "Substituição Tributária" if x == "st" else "Tributado"
            )
            
            mva_ajustado_12 = st.number_input(
                "MVA Ajustado 12% (%)",
                min_value=0.0,
                value=0.0,
                step=0.01
            )
            
            mva_ajustado_4 = st.number_input(
                "MVA Ajustado 4% (%)",
                min_value=0.0,
                value=0.0,
                step=0.01
            )
        
        with col2:
            aliquota_icms_12 = st.number_input(
                "Alíquota ICMS 12% (%)",
                min_value=0.0,
                max_value=100.0,
                value=12.0,
                step=0.01
            )
            
            aliquota_icms_4 = st.number_input(
                "Alíquota ICMS 4% (%)",
                min_value=0.0,
                max_value=100.0,
                value=4.0,
                step=0.01
            )
            
            reducao_bc_st = st.number_input(
                "Redução BC ICMS ST (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.01
            )
            
            reducao_bc_proprio = st.number_input(
                "Redução BC ICMS Próprio (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.01
            )
        
        observacoes = st.text_area("Observações")
        
        if st.form_submit_button("💾 Cadastrar Figura", type="primary"):
            try:
                # Validar dados
                if not all([ncm, descricao]):
                    st.error("Preencha todos os campos obrigatórios (*)")
                    return
                
                # Criar figura
                figura = FiguraTributaria(
                    ncm=ncm,
                    descricao=descricao,
                    tipo_tributacao=tipo_tributacao,
                    aliquota_icms_12=aliquota_icms_12,
                    aliquota_icms_4=aliquota_icms_4,
                    mva_ajustado_12=mva_ajustado_12,
                    mva_ajustado_4=mva_ajustado_4,
                    reducao_bc_icms_st=reducao_bc_st,
                    reducao_bc_icms_proprio=reducao_bc_proprio,
                    observacoes=observacoes
                )
                
                # Validar figura
                erros = figura.validar()
                if erros:
                    st.error("Erros de validação:\n" + "\n".join(f"- {erro}" for erro in erros))
                    return
                
                # Salvar no banco
                db_manager = services['db_manager']
                db_manager.save_figura_tributaria(figura)
                
                st.success("✅ Figura tributária cadastrada com sucesso!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao cadastrar figura: {e}")

def show_lista_figuras(services):
    """Lista figuras tributárias cadastradas"""
    st.subheader("📋 Figuras Cadastradas")
    
    try:
        db_manager = services['db_manager']
        figuras_dict = db_manager.get_all_figuras_tributarias()
        
        if not figuras_dict:
            st.info("Nenhuma figura tributária cadastrada")
            return
        
        # Converter para DataFrame
        df_data = []
        for ncm, figura in figuras_dict.items():
            df_data.append({
                'NCM': figura.ncm,
                'Descrição': figura.descricao,
                'Tipo': 'ST' if figura.tipo_tributacao == 'st' else 'Tributado',
                'MVA 12%': f"{figura.mva_ajustado_12:.2f}%",
                'MVA 4%': f"{figura.mva_ajustado_4:.2f}%",
                'Red. ST': f"{figura.reducao_bc_icms_st:.2f}%",
                'Red. Próprio': f"{figura.reducao_bc_icms_proprio:.2f}%",
                'Ativo': "✅" if figura.ativo else "❌"
            })
        
        df = pd.DataFrame(df_data)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_ncm = st.text_input("Filtrar por NCM")
        
        with col2:
            filtro_tipo = st.selectbox(
                "Filtrar por Tipo",
                ["Todos", "ST", "Tributado"]
            )
        
        with col3:
            filtro_ativo = st.selectbox(
                "Filtrar por Status",
                ["Todos", "Ativo", "Inativo"]
            )
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if filtro_ncm:
            df_filtrado = df_filtrado[df_filtrado['NCM'].str.contains(filtro_ncm, case=False)]
        
        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == filtro_tipo]
        
        if filtro_ativo == "Ativo":
            df_filtrado = df_filtrado[df_filtrado['Ativo'] == "✅"]
        elif filtro_ativo == "Inativo":
            df_filtrado = df_filtrado[df_filtrado['Ativo'] == "❌"]
        
        # Exibir tabela
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Figuras", len(df))
        
        with col2:
            figuras_st = len(df[df['Tipo'] == 'ST'])
            st.metric("Figuras ST", figuras_st)
        
        with col3:
            figuras_ativas = len(df[df['Ativo'] == "✅"])
            st.metric("Figuras Ativas", figuras_ativas)
        
    except Exception as e:
        st.error(f"Erro ao carregar figuras: {e}")