# 🧮 Calculadora Fiscal ICMS ST

Aplicação web para cálculo de ICMS Substituição Tributária desenvolvida com Streamlit.

## 📋 Funcionalidades

- **Dashboard**: Visão geral dos cálculos e estatísticas
- **Cálculo ICMS ST**: Interface para cálculos manuais e importação de XML
- **Figuras Tributárias**: Gerenciamento de NCMs e configurações tributárias
- **Relatórios**: Exportação de dados e análises
- **Configurações**: Personalização do sistema

## 🚀 Deploy no Streamlit Cloud

### Pré-requisitos

1. Conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Repositório no GitHub com o código da aplicação
3. Arquivo `requirements.txt` atualizado

### Passos para Deploy

1. **Preparar o repositório**:
   ```bash
   git add .
   git commit -m "Preparar para deploy no Streamlit Cloud"
   git push origin main
   ```

2. **Configurar no Streamlit Cloud**:
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Clique em "New app"
   - Conecte seu repositório GitHub
   - Configure:
     - **Repository**: `seu-usuario/seu-repositorio`
     - **Branch**: `main`
     - **Main file path**: `app.py`

3. **Configurar Secrets** (se necessário):
   - No painel do Streamlit Cloud, vá em "Settings" > "Secrets"
   - Adicione as configurações baseadas no arquivo `.streamlit/secrets.toml.example`:
   ```toml
   [database]
   db_path = "data/calculadora.db"
   
   [app]
   debug_mode = false
   log_level = "INFO"
   ```

4. **Deploy automático**:
   - O Streamlit Cloud fará o deploy automaticamente
   - Aguarde a instalação das dependências
   - Sua aplicação estará disponível em uma URL única

### 🔧 Configurações Importantes

#### Banco de Dados
- A aplicação usa SQLite por padrão
- Para produção, considere usar PostgreSQL ou MySQL
- Configure a conexão em `secrets.toml`

#### Arquivos de Configuração
- `.streamlit/config.toml`: Configurações de produção
- `.streamlit/secrets.toml`: Variáveis sensíveis (não commitado)
- `requirements.txt`: Dependências Python

### 📁 Estrutura do Projeto

```
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── .streamlit/
│   ├── config.toml       # Configurações do Streamlit
│   └── secrets.toml.example  # Exemplo de secrets
├── core/                 # Módulos principais
│   ├── database_manager.py
│   ├── icms_calculator.py
│   ├── xml_processor.py
│   └── config_manager.py
├── pages/                # Páginas da aplicação
│   ├── dashboard.py
│   ├── calculo_icms.py
│   ├── figuras_tributarias.py
│   ├── relatorios.py
│   └── configuracoes.py
├── components/           # Componentes reutilizáveis
├── models/              # Modelos de dados
├── utils/               # Utilitários
└── config/              # Configurações
```

### 🛠️ Desenvolvimento Local

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar aplicação**:
   ```bash
   streamlit run app.py
   ```

3. **Acessar**: http://localhost:8501

### 📝 Notas Importantes

- **Performance**: O SQLite funciona bem para aplicações pequenas/médias
- **Escalabilidade**: Para muitos usuários, considere PostgreSQL
- **Backup**: Configure backup automático dos dados
- **Monitoramento**: Use os logs do Streamlit Cloud para debugging

### 🔍 Troubleshooting

#### Erro de Dependências
- Verifique se todas as dependências estão no `requirements.txt`
- Use versões específicas para evitar conflitos

#### Erro de Banco de Dados
- Verifique as configurações em `secrets.toml`
- Confirme se o banco está acessível

#### Erro de Importação
- Verifique a estrutura de pastas
- Confirme se todos os `__init__.py` estão presentes

### 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no Streamlit Cloud
2. Consulte a [documentação oficial](https://docs.streamlit.io)
3. Verifique as configurações de secrets e config

---

**Desenvolvido com ❤️ usando Streamlit**