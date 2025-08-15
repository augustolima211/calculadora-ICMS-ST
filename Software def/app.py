"""
Calculadora Fiscal de ICMS ST - Aplicação Principal Refatorada
Interface principal usando Streamlit
"""
import streamlit as st
from datetime import datetime

# Imports dos módulos internos
from core.database_manager import DatabaseManager
from core.icms_calculator import ICMSCalculator
from core.xml_processor import XMLProcessor
from core.config_manager import ConfigManager
from utils.logger import SystemLogger
from utils.exceptions import ValidationError, CalculationError, DatabaseError
from utils.validators import Validators

# Imports das páginas
from pages.dashboard import show_dashboard
from pages.calculo_icms import show_calculo_icms
from pages.figuras_tributarias import show_figuras_tributarias
from pages.relatorios import show_relatorios
from pages.configuracoes import show_configuracoes

# Configuração da página
st.set_page_config(
    page_title="Calculadora Fiscal ICMS ST",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização dos serviços
@st.cache_resource
def init_services():
    """Inicializa os serviços do sistema"""
    try:
        db_manager = DatabaseManager()
        icms_calculator = ICMSCalculator()
        xml_processor = XMLProcessor()
        validators = Validators()
        logger = SystemLogger('app')
        config_manager = ConfigManager()
        
        return {
            'db_manager': db_manager,
            'icms_calculator': icms_calculator,
            'xml_processor': xml_processor,
            'validators': validators,
            'logger': logger,
            'config_manager': config_manager
        }
    except Exception as e:
        st.error(f"Erro na inicialização dos serviços: {e}")
        return None

def main():
    """Função principal da aplicação"""
    # Inicializar serviços
    services = init_services()
    if not services:
        st.stop()
    
    # Header principal
    st.markdown('<h1 class="main-header">🧮 Calculadora Fiscal ICMS ST</h1>', unsafe_allow_html=True)
    
    # Sidebar para navegação
    st.sidebar.title("📋 Menu Principal")
    
    opcoes_menu = {
        "🏠 Dashboard": "dashboard",
        "📊 Cálculo ICMS ST": "calculo",
        "📋 Figuras Tributárias": "figuras",
        "📄 Relatórios": "relatorios",
        "⚙️ Configurações": "configuracoes"
    }
    
    opcao_selecionada = st.sidebar.selectbox(
        "Selecione uma opção:",
        list(opcoes_menu.keys())
    )
    
    pagina = opcoes_menu[opcao_selecionada]
    
    # Roteamento das páginas
    try:
        if pagina == "dashboard":
            show_dashboard(services)
        elif pagina == "calculo":
            show_calculo_icms(services)
        elif pagina == "figuras":
            show_figuras_tributarias(services)
        elif pagina == "relatorios":
            show_relatorios(services)
        elif pagina == "configuracoes":
            show_configuracoes(services)
    except Exception as e:
        st.error(f"Erro ao carregar página {pagina}: {e}")
        services['logger'].error(f"Erro na página {pagina}: {e}")

if __name__ == "__main__":
    main()