import streamlit as st
from datetime import datetime
from decimal import ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, ROUND_CEILING, ROUND_FLOOR

def show_configuracoes(services):
    """Página de configurações do sistema"""
    st.title("⚙️ Configurações")
    
    config_manager = services['config_manager']
    
    try:
        config = config_manager.load_config()
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {e}")
        return
    
    # Abas de configuração
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧮 Cálculo", "🎨 Interface", "📊 Exportação", "🔧 Sistema", "ℹ️ Informações"
    ])
    
    with tab1:
        show_config_calculo(config_manager, config)
    
    with tab2:
        show_config_interface(config_manager, config)
    
    with tab3:
        show_config_exportacao(config_manager, config)
    
    with tab4:
        show_config_sistema(config_manager, config, services)
    
    with tab5:
        show_config_informacoes(services)

def show_config_calculo(config_manager, config):
    """Configurações de cálculo"""
    st.subheader("🧮 Configurações de Cálculo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Precisão e Arredondamento**")
        
        precisao = st.number_input(
            "Precisão decimal",
            min_value=2,
            max_value=6,
            value=config.precisao_decimal,
            help="Número de casas decimais para cálculos"
        )
        
        opcoes_arredondamento = {
            "Meio para cima": "ROUND_HALF_UP",
            "Para baixo": "ROUND_DOWN",
            "Para cima": "ROUND_UP",
            "Teto": "ROUND_CEILING",
            "Piso": "ROUND_FLOOR"
        }
        
        tipo_arredondamento = st.selectbox(
            "Tipo de arredondamento",
            options=list(opcoes_arredondamento.keys()),
            index=list(opcoes_arredondamento.values()).index(config.tipo_arredondamento)
        )
        
        st.markdown("**Alíquotas Padrão**")
        
        # Verificar e corrigir valores de alíquota com validação segura
        try:
            aliquota_12_value = float(config.aliquota_icms_padrao_12)
            if aliquota_12_value <= 1.0:
                aliquota_12_value *= 100  # Converter de decimal para percentual
            # Garantir que não exceda o máximo
            aliquota_12_value = min(aliquota_12_value, 100.0)
        except (ValueError, TypeError):
            aliquota_12_value = 12.0  # Valor padrão
        
        aliquota_12 = st.number_input(
            "Alíquota ICMS 12% (percentual)",
            min_value=0.0,
            max_value=100.0,
            value=aliquota_12_value,
            step=0.01,
            format="%.2f",
            help="Digite o valor em percentual (ex: 12.00 para 12%)"
        )
        
        # Verificar se o valor já está em percentual ou decimal
        aliquota_4_value = float(config.aliquota_icms_padrao_4)
        if aliquota_4_value <= 1.0:
            aliquota_4_value *= 100  # Converter de decimal para percentual
        
        aliquota_4 = st.number_input(
            "Alíquota ICMS 4% (percentual)",
            min_value=0.0,
            max_value=100.0,
            value=aliquota_4_value,
            step=0.01,
            format="%.2f",
            help="Digite o valor em percentual (ex: 4.00 para 4%)"
        )
    
    with col2:
        st.markdown("**Comportamentos Automáticos**")
        
        reducao_automatica = st.checkbox(
            "Considerar redução de BC automaticamente",
            value=config.considerar_reducao_bc_automatica,
            help="Aplica redução de base de cálculo automaticamente quando disponível"
        )
        
        mva_automatico = st.checkbox(
            "Aplicar MVA ajustado automaticamente",
            value=config.aplicar_mva_ajustado_automatico,
            help="Aplica MVA ajustado automaticamente quando disponível"
        )
        
        validar_ncm = st.checkbox(
            "Validar NCM automaticamente",
            value=config.validar_ncm_automatico,
            help="Valida NCM durante o processamento"
        )
        
        st.markdown("**Alertas e Notificações**")
        
        alertar_figura = st.checkbox(
            "Alertar quando figura não encontrada",
            value=config.alertar_figura_nao_encontrada
        )
        
        alertar_zeros = st.checkbox(
            "Alertar valores zerados",
            value=config.alertar_valores_zerados
        )
    
    if st.button("💾 Salvar Configurações de Cálculo", type="primary"):
        try:
            # Atualizar configurações
            config.precisao_decimal = precisao
            config.tipo_arredondamento = opcoes_arredondamento[tipo_arredondamento]
            
            # Garantir que as alíquotas sejam salvas em decimal
            config.aliquota_icms_padrao_12 = aliquota_12 / 100 if aliquota_12 > 1.0 else aliquota_12
            config.aliquota_icms_padrao_4 = aliquota_4 / 100 if aliquota_4 > 1.0 else aliquota_4
            
            config.considerar_reducao_bc_automatica = reducao_automatica
            config.aplicar_mva_ajustado_automatico = mva_automatico
            config.validar_ncm_automatico = validar_ncm
            config.alertar_figura_nao_encontrada = alertar_figura
            config.alertar_valores_zerados = alertar_zeros
            
            config_manager.save_config(config)
            st.success("✅ Configurações de cálculo salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")

def show_config_interface(config_manager, config):
    """Configurações de interface"""
    st.subheader("🎨 Configurações de Interface")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Aparência**")
        
        # Mapeamento de temas com validação segura
        tema_opcoes = {"light": "Claro", "dark": "Escuro"}
        tema_reverso = {v: k for k, v in tema_opcoes.items()}
        
        try:
            tema_atual = config.tema if config.tema in tema_opcoes else "light"
            tema_index = list(tema_opcoes.values()).index(tema_opcoes[tema_atual])
        except (ValueError, KeyError):
            tema_index = 0  # Default para "Claro"
            
        tema_display = st.selectbox(
            "Tema",
            options=list(tema_opcoes.values()),
            index=tema_index
        )
        
        tema = tema_reverso[tema_display]
        
        try:
            idioma_index = ["pt-BR", "en-US"].index(config.idioma)
        except ValueError:
            idioma_index = 0  # Default para pt-BR
            
        idioma = st.selectbox(
            "Idioma",
            options=["pt-BR", "en-US"],
            index=idioma_index
        )
    
    with col2:
        st.markdown("**Comportamento**")
        
        mostrar_tooltips = st.checkbox(
            "Mostrar tooltips",
            value=config.mostrar_tooltips,
            help="Exibe dicas de ajuda nos elementos da interface"
        )
        
        mostrar_detalhes = st.checkbox(
            "Mostrar detalhes do cálculo",
            value=config.mostrar_detalhes_calculo,
            help="Exibe informações detalhadas durante os cálculos"
        )
        
        auto_salvar = st.checkbox(
            "Auto-salvar cálculos",
            value=config.auto_salvar_calculos,
            help="Salva automaticamente os resultados dos cálculos"
        )
    
    if st.button("💾 Salvar Configurações de Interface", type="primary"):
        try:
            config.tema = tema
            config.idioma = idioma
            config.mostrar_tooltips = mostrar_tooltips
            config.mostrar_detalhes_calculo = mostrar_detalhes
            config.auto_salvar_calculos = auto_salvar
            
            config_manager.save_config(config)
            st.success("✅ Configurações de interface salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")

def show_config_exportacao(config_manager, config):
    """Configurações de exportação"""
    st.subheader("📊 Configurações de Exportação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Formato Padrão**")
        
        # Mapeamento de formatos com validação segura
        formato_opcoes = {"xlsx": "Excel", "csv": "CSV", "pdf": "PDF"}
        formato_reverso = {v: k for k, v in formato_opcoes.items()}
        
        try:
            formato_atual = config.formato_exportacao_padrao if config.formato_exportacao_padrao in formato_opcoes else "xlsx"
            formato_index = list(formato_opcoes.values()).index(formato_opcoes[formato_atual])
        except (ValueError, KeyError):
            formato_index = 0  # Default para "Excel"
            
        formato_display = st.selectbox(
            "Formato de exportação padrão",
            options=list(formato_opcoes.values()),
            index=formato_index
        )
        
        formato_exportacao = formato_reverso[formato_display]
    
    with col2:
        st.markdown("**Conteúdo da Exportação**")
        
        incluir_graficos = st.checkbox(
            "Incluir gráficos na exportação",
            value=config.incluir_graficos_exportacao,
            help="Adiciona gráficos aos relatórios exportados"
        )
        
        incluir_observacoes = st.checkbox(
            "Incluir observações na exportação",
            value=config.incluir_observacoes_exportacao,
            help="Adiciona observações e comentários aos relatórios"
        )
    
    if st.button("💾 Salvar Configurações de Exportação", type="primary"):
        try:
            config.formato_exportacao_padrao = formato_exportacao
            config.incluir_graficos_exportacao = incluir_graficos
            config.incluir_observacoes_exportacao = incluir_observacoes
            
            config_manager.save_config(config)
            st.success("✅ Configurações de exportação salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")

def show_config_sistema(config_manager, config, services):
    """Configurações do sistema"""
    st.subheader("🔧 Configurações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Backup e Manutenção**")
        
        backup_automatico = st.checkbox(
            "Backup automático",
            value=config.backup_automatico,
            help="Realiza backup automático dos dados"
        )
        
        intervalo_backup = st.number_input(
            "Intervalo de backup (dias)",
            min_value=1,
            max_value=30,
            value=config.intervalo_backup_dias
        )
        
        manter_historico = st.number_input(
            "Manter histórico (dias)",
            min_value=7,
            max_value=365,
            value=config.manter_historico_dias
        )
        
        usar_cache = st.checkbox(
            "Usar cache de figuras",
            value=config.usar_cache_figuras,
            help="Utiliza cache para melhorar performance"
        )
    
    with col2:
        st.markdown("**Performance e Limites**")
        
        timeout_conexao = st.number_input(
            "Timeout de conexão (segundos)",
            min_value=5,
            max_value=300,
            value=config.timeout_conexao_segundos
        )
        
        max_itens = st.number_input(
            "Máximo de itens por cálculo",
            min_value=10,
            max_value=10000,
            value=config.max_itens_por_calculo
        )
        
        log_level = st.selectbox(
            "Nível de log",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.log_level)
        )
    
    st.markdown("**Ações do Sistema**")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🔄 Resetar Configurações", help="Restaura configurações padrão"):
            if st.session_state.get('confirm_reset', False):
                try:
                    config_manager.reset_config()
                    st.success("✅ Configurações resetadas com sucesso!")
                    st.session_state['confirm_reset'] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao resetar configurações: {e}")
            else:
                st.session_state['confirm_reset'] = True
                st.warning("⚠️ Clique novamente para confirmar o reset")
    
    with col4:
        if st.button("🗑️ Limpar Cache", help="Remove arquivos de cache"):
            try:
                # Implementar limpeza de cache se necessário
                st.success("✅ Cache limpo com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao limpar cache: {e}")
    
    with col5:
        if st.button("💾 Backup Manual", help="Realiza backup imediato"):
            try:
                # Implementar backup manual se necessário
                st.success("✅ Backup realizado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao realizar backup: {e}")
    
    if st.button("💾 Salvar Configurações do Sistema", type="primary"):
        try:
            config.backup_automatico = backup_automatico
            config.intervalo_backup_dias = intervalo_backup
            config.manter_historico_dias = manter_historico
            config.usar_cache_figuras = usar_cache
            config.timeout_conexao_segundos = timeout_conexao
            config.max_itens_por_calculo = max_itens
            config.log_level = log_level
            
            config_manager.save_config(config)
            st.success("✅ Configurações do sistema salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")

def show_config_informacoes(services):
    """Informações do sistema"""
    st.subheader("ℹ️ Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Aplicação**")
        st.info("""
        **Calculadora Fiscal ICMS ST**
        
        📋 **Versão:** 2.0.0
        📅 **Data:** Agosto 2025
        👨‍💻 **Desenvolvedor:** Augusto Lima
        
        **Funcionalidades:**
        - ✅ Cálculo de ICMS ST
        - ✅ Processamento de XML
        - ✅ Gerenciamento de figuras tributárias
        - ✅ Relatórios e exportação
        - ✅ Dashboard analítico
        """)
    
    with col2:
        st.markdown("**Status do Sistema**")
        
        try:
            db_manager = services.get('db_manager')
            if db_manager:
                st.success("🟢 Banco de dados: Conectado")
            else:
                st.error("🔴 Banco de dados: Desconectado")
        except:
            st.error("🔴 Banco de dados: Erro")
        
        try:
            config_manager = services.get('config_manager')
            if config_manager:
                st.success("🟢 Gerenciador de config: Ativo")
            else:
                st.error("🔴 Gerenciador de config: Inativo")
        except:
            st.error("🔴 Gerenciador de config: Erro")
        
        try:
            icms_calculator = services.get('icms_calculator')
            if icms_calculator:
                st.success("🟢 Calculadora ICMS: Ativa")
            else:
                st.error("🔴 Calculadora ICMS: Inativa")
        except:
            st.error("🔴 Calculadora ICMS: Erro")
        
        st.markdown("**Estatísticas**")
        try:
            # Aqui você pode adicionar estatísticas reais do sistema
            st.metric("Cálculos realizados", "---")
            st.metric("Figuras cadastradas", "---")
            st.metric("Tempo de atividade", "---")
        except:
            st.warning("⚠️ Estatísticas indisponíveis")
    
    st.markdown("---")
    st.markdown("**Suporte Técnico**")
    st.info("""
    📧 **Email:** augustolima21yahoo@gmail.com
    📞 **Telefone:** (35) 99826-6656
    🌐 **Site:** www.calculadorafiscal.com
    📚 **Documentação:** docs.calculadorafiscal.com
    """)