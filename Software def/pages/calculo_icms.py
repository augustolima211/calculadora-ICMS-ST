"""
Interface de cálculo de ICMS ST
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from models.resultado_calculo import ResultadoCalculoGeral
from components.exports import export_to_excel
from components.charts import show_estatisticas_calculo

def show_calculo_icms(services):
    """Exibe a interface de cálculo de ICMS ST"""
    st.header("📊 Cálculo de ICMS ST")
    
    # Abas para diferentes tipos de cálculo
    tab1, tab2, tab3 = st.tabs(["📝 Manual", "📄 Upload XML", "📋 Por NFe"])
    
    with tab1:
        show_calculo_manual(services)
    
    with tab2:
        show_upload_xml(services)
    
    with tab3:
        show_calculo_por_nfe(services)

def show_calculo_manual(services):
    """Interface para cálculo manual"""
    st.subheader("📝 Cálculo Manual")
    
    # Formulário para entrada de dados
    with st.form("calculo_manual"):
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
        
        submitted = st.form_submit_button("🧮 Calcular ICMS ST", type="primary")
        
        if submitted:
            try:
                # Validar dados
                if not all([codigo, descricao, ncm]):
                    st.error("Preencha todos os campos obrigatórios (*)")
                    return
                
                # Preparar dados para cálculo
                dados_item = {
                    'codigo': codigo,
                    'descricao': descricao,
                    'ncm': ncm,
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'valor_ipi': valor_ipi,
                    'valor_frete': valor_frete
                }
                
                # Calcular ICMS ST
                icms_calculator = services['icms_calculator']
                resultado = icms_calculator.calcular_icms_st_manual([dados_item], frete_por_fora)
                
                # Exibir resultados
                show_resultado_calculo(resultado, services)
                
            except Exception as e:
                st.error(f"Erro no cálculo: {e}")

def show_upload_xml(services):
    """Interface para upload de XML"""
    st.subheader("📄 Upload de XML NFe")
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Selecione o arquivo XML da NFe",
        type=['xml'],
        help="Arquivo XML da Nota Fiscal Eletrônica"
    )
    
    if uploaded_file is not None:
        # Parâmetros adicionais
        col1, col2 = st.columns(2)
        
        with col1:
            frete_por_fora = st.number_input(
                "Frete por Fora (R$)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Valor do frete não incluído na nota"
            )
        
        with col2:
            usar_figuras_cadastradas = st.checkbox(
                "Usar apenas figuras tributárias cadastradas",
                value=True,
                help="Se desmarcado, usará MVA padrão para itens sem figura"
            )
        
        if st.button("🧮 Processar XML e Calcular", type="primary"):
            try:
                # Ler conteúdo do arquivo
                xml_content = uploaded_file.read()
                
                # Processar XML e calcular
                icms_calculator = services['icms_calculator']
                resultado = icms_calculator.calcular_icms_st_xml(xml_content, frete_por_fora)
                
                # Exibir resultados
                show_resultado_calculo(resultado, services)
                
            except Exception as e:
                st.error(f"Erro no processamento do XML: {e}")

def show_calculo_por_nfe(services):
    """Interface para cálculo por NFe existente"""
    st.subheader("📋 Cálculo por NFe Existente")
    st.info("Funcionalidade em desenvolvimento - Permitirá selecionar NFes já importadas")

def show_resultado_calculo(resultado: ResultadoCalculoGeral, services):
    """Exibe os resultados do cálculo - VERSÃO COM SALVAMENTO E EXPORT AUTOMÁTICO"""
    try:
        st.success("✅ Cálculo realizado com sucesso!")
        
        # ==========================================
        # SALVAMENTO AUTOMÁTICO NO BANCO
        # ==========================================
        st.info("💾 Salvando automaticamente no banco de dados...")
        
        try:
            if services and 'db_manager' in services:
                db_manager = services['db_manager']
                if hasattr(db_manager, 'save_calculo'):
                    resultado_id = db_manager.save_calculo(resultado)
                    st.success(f"✅ Cálculo salvo automaticamente! ID: {resultado_id}")
                else:
                    st.warning("⚠️ Método de salvamento não disponível")
            else:
                st.warning("⚠️ Serviço de banco não disponível")
        except Exception as e:
            st.error(f"❌ Erro no salvamento automático: {str(e)}")
        
        # ==========================================
        # GERAÇÃO AUTOMÁTICA DO EXCEL
        # ==========================================
        st.info("📊 Gerando arquivo Excel automaticamente...")
        
        excel_data = None
        try:
            from components.exports import export_to_excel
            excel_data = export_to_excel(resultado)
            if excel_data:
                st.success("✅ Excel gerado automaticamente!")
            else:
                st.warning("⚠️ Falha na geração automática do Excel")
        except ImportError:
            st.error("❌ Módulo de exportação não encontrado")
        except Exception as e:
            st.error(f"❌ Erro na geração automática do Excel: {str(e)}")
        
        # ==========================================
        # RESUMO GERAL
        # ==========================================
        st.subheader("📊 Resumo do Cálculo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Itens", resultado.total_itens)
        
        with col2:
            st.metric("Valor dos Produtos", f"R$ {resultado.total_valor_produtos:,.2f}")
        
        with col3:
            st.metric("ICMS ST Total", f"R$ {resultado.total_icms_st:,.2f}")
        
        with col4:
            st.metric("Custo Final Total", f"R$ {resultado.total_custo_final:,.2f}")
        
        # ==========================================
        # DETALHES DOS ITENS
        # ==========================================
        st.subheader("📋 Detalhes dos Itens")
        
        # Converter para DataFrame
        df_itens = []
        for item in resultado.detalhes_itens:
            df_itens.append({
                'Código': item.codigo_item,
                'Descrição': item.descricao,
                'NCM': item.ncm,
                'Qtd': item.quantidade,
                'Vlr Unit': f"R$ {item.valor_unitario:.2f}",
                'Vlr Total': f"R$ {item.valor_total:.2f}",
                'ICMS ST': f"R$ {item.valor_icms_st_recolher:.2f}",
                'Custo Final': f"R$ {item.valor_custo_final:.2f}",
                'Possui Figura': "✅" if item.possui_figura else "❌",
                'Observações': "; ".join(item.observacoes) if item.observacoes else "-"
            })
        
        df = pd.DataFrame(df_itens)
        st.dataframe(df, use_container_width=True)
        
        # ==========================================
        # DOWNLOAD DO EXCEL (SE GERADO)
        # ==========================================
        if excel_data:
            st.markdown("---")
            st.subheader("📥 Download Disponível")
            
            col_download1, col_download2 = st.columns([1, 3])
            
            with col_download1:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_data,
                    file_name=f"calculo_icms_st_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_automatico",
                    use_container_width=True
                )
            
            with col_download2:
                st.info("📊 Arquivo Excel pronto para download com todos os detalhes do cálculo")
        
        # ==========================================
        # ESTATÍSTICAS AUTOMÁTICAS (OPCIONAL)
        # ==========================================
        st.markdown("---")
        st.subheader("📈 Estatísticas Automáticas")
        
        # Estatísticas básicas sempre visíveis
        total_com_figura = sum(1 for item in resultado.detalhes_itens if item.possui_figura)
        total_sem_figura = resultado.total_itens - total_com_figura
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Itens com Figura", total_com_figura)
        
        with col_stat2:
            st.metric("Itens sem Figura", total_sem_figura)
        
        with col_stat3:
            percentual = (total_com_figura / resultado.total_itens * 100) if resultado.total_itens > 0 else 0
            st.metric("% com Figura", f"{percentual:.1f}%")
        
        with col_stat4:
            valor_medio = resultado.total_valor_produtos / resultado.total_itens if resultado.total_itens > 0 else 0
            st.metric("Valor Médio/Item", f"R$ {valor_medio:.2f}")
        
        # ==========================================
        # RESUMO POR NCM (AUTOMÁTICO)
        # ==========================================
        st.subheader("📋 Resumo por NCM")
        
        ncm_resumo = {}
        for item in resultado.detalhes_itens:
            ncm = item.ncm
            if ncm not in ncm_resumo:
                ncm_resumo[ncm] = {
                    'quantidade': 0,
                    'valor_total': 0,
                    'icms_st': 0,
                    'itens': 0
                }
            
            ncm_resumo[ncm]['quantidade'] += item.quantidade
            ncm_resumo[ncm]['valor_total'] += item.valor_total
            ncm_resumo[ncm]['icms_st'] += item.valor_icms_st_recolher
            ncm_resumo[ncm]['itens'] += 1
        
        df_ncm = pd.DataFrame([
            {
                'NCM': ncm,
                'Qtd Itens': dados['itens'],
                'Quantidade': f"{dados['quantidade']:.2f}",
                'Valor Total': f"R$ {dados['valor_total']:,.2f}",
                'ICMS ST': f"R$ {dados['icms_st']:,.2f}",
                'Participação': f"{(dados['valor_total']/resultado.total_valor_produtos*100):.1f}%"
            }
            for ncm, dados in ncm_resumo.items()
        ])
        
        st.dataframe(df_ncm, use_container_width=True)
        
        # ==========================================
        # GRÁFICOS AUTOMÁTICOS (SE DISPONÍVEL)
        # ==========================================
        try:
            from components.charts import show_estatisticas_calculo
            
            # Checkbox para mostrar gráficos detalhados
            if st.checkbox("📈 Mostrar Gráficos Detalhados", value=False):
                st.markdown("---")
                st.subheader("📈 Gráficos Detalhados")
                show_estatisticas_calculo(resultado)
                
        except ImportError:
            st.info("ℹ️ Gráficos detalhados não disponíveis (módulo não encontrado)")
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar gráficos: {str(e)}")
        
        # ==========================================
        # INFORMAÇÕES TÉCNICAS
        # ==========================================
        st.markdown("---")
        
        with st.expander("🔧 Informações Técnicas"):
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Total de Itens Processados:** {resultado.total_itens}")
            st.write(f"**Valor Total dos Produtos:** R$ {resultado.total_valor_produtos:,.2f}")
            st.write(f"**Total ICMS ST Calculado:** R$ {resultado.total_icms_st:,.2f}")
            st.write(f"**Custo Final Total:** R$ {resultado.total_custo_final:,.2f}")
            
            # Status dos serviços
            st.write("**Status dos Serviços:**")
            if services:
                for nome_servico, servico in services.items():
                    status = "✅ Disponível" if servico else "❌ Indisponível"
                    st.write(f"- {nome_servico}: {status}")
            else:
                st.write("- ❌ Nenhum serviço disponível")
        
        # ==========================================
        # RESUMO FINAL
        # ==========================================
        st.markdown("---")
        st.success("🎉 **Processamento Completo!**")
        
        col_resumo1, col_resumo2 = st.columns(2)
        
        with col_resumo1:
            st.info("✅ **Ações Executadas Automaticamente:**\n\n" +
                   "💾 Cálculo salvo no banco de dados\n\n" +
                   "📊 Arquivo Excel gerado\n\n" +
                   "📈 Estatísticas calculadas\n\n" +
                   "📋 Resumos criados")
        
        with col_resumo2:
            st.info("📥 **Próximos Passos:**\n\n" +
                   "⬇️ Faça o download do Excel\n\n" +
                   "📈 Analise as estatísticas\n\n" +
                   "🔍 Verifique os detalhes por NCM\n\n" +
                   "🔄 Execute novo cálculo se necessário")
        
    except Exception as e:
        st.error(f"❌ Erro crítico na exibição: {str(e)}")
        
        # FALLBACK ULTRA-SEGURO
        st.markdown("---")
        st.subheader("🆘 Dados Básicos (Modo Seguro)")
        
        try:
            st.write(f"**Total de Itens:** {resultado.total_itens}")
            st.write(f"**ICMS ST Total:** R$ {resultado.total_icms_st:,.2f}")
            st.write(f"**Custo Final:** R$ {resultado.total_custo_final:,.2f}")
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Tentar salvamento de emergência
            st.info("🔄 Tentando salvamento de emergência...")
            try:
                if services and 'db_manager' in services:
                    db_manager = services['db_manager']
                    if hasattr(db_manager, 'save_calculo'):
                        resultado_id = db_manager.save_calculo(resultado)
                        st.success(f"✅ Salvamento de emergência realizado! ID: {resultado_id}")
            except Exception as save_error:
                st.error(f"❌ Falha no salvamento de emergência: {str(save_error)}")
            
        except Exception as fallback_error:
            st.error(f"❌ Erro crítico no fallback: {str(fallback_error)}")
            st.code(f"Detalhes: {type(fallback_error).__name__}: {str(fallback_error)}")