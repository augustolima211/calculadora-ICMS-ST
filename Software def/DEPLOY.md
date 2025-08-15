# 🚀 Guia de Deploy - Streamlit Cloud

## ✅ Checklist Pré-Deploy

### Arquivos Essenciais
- [x] `app.py` - Aplicação principal
- [x] `requirements.txt` - Dependências atualizadas
- [x] `.streamlit/config.toml` - Configurações de produção
- [x] `.streamlit/secrets.toml.example` - Template de secrets
- [x] `.gitignore` - Arquivos a ignorar
- [x] `README.md` - Documentação
- [x] Arquivos `__init__.py` em todas as pastas

### Estrutura Verificada
```
✅ app.py
✅ requirements.txt
✅ .streamlit/
   ✅ config.toml
   ✅ secrets.toml.example
✅ core/ (com __init__.py)
✅ pages/ (com __init__.py)
✅ components/ (com __init__.py)
✅ models/ (com __init__.py)
✅ utils/ (com __init__.py)
✅ config/ (com __init__.py)
```

## 🔧 Passos para Deploy

### 1. Preparar Repositório Git
```bash
# Adicionar todos os arquivos
git add .

# Commit das mudanças
git commit -m "Preparar aplicação para deploy no Streamlit Cloud"

# Push para o repositório
git push origin main
```

### 2. Configurar no Streamlit Cloud

1. **Acesse**: https://share.streamlit.io
2. **Login** com sua conta GitHub
3. **Clique em "New app"**
4. **Configure**:
   - Repository: `seu-usuario/calculadora-icms-st`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: `calculadora-icms-st` (ou nome desejado)

### 3. Configurar Secrets (Opcional)

Se precisar de configurações específicas:

1. **No painel do app**, clique em "Settings"
2. **Vá para "Secrets"**
3. **Adicione** (baseado no `.streamlit/secrets.toml.example`):

```toml
[database]
db_path = "data/calculadora.db"

[app]
debug_mode = false
log_level = "INFO"
```

### 4. Deploy Automático

- O Streamlit Cloud detectará automaticamente o `requirements.txt`
- Instalará as dependências
- Executará `streamlit run app.py`
- Sua app estará disponível em: `https://seu-app.streamlit.app`

## 🔍 Verificações Pós-Deploy

### ✅ Funcionalidades a Testar
- [ ] Dashboard carrega corretamente
- [ ] Cálculo ICMS ST funciona
- [ ] Figuras Tributárias são exibidas
- [ ] Relatórios são gerados
- [ ] Configurações são salvas
- [ ] Banco de dados funciona
- [ ] Imports estão corretos

### 🐛 Troubleshooting Comum

#### Erro de Import
```
ModuleNotFoundError: No module named 'core'
```
**Solução**: Verificar se todos os `__init__.py` estão presentes

#### Erro de Dependência
```
ERROR: Could not find a version that satisfies the requirement
```
**Solução**: Verificar versões no `requirements.txt`

#### Erro de Banco de Dados
```
no such table: figuras_tributarias
```
**Solução**: Verificar se `init_database()` está sendo chamado

## 📊 Monitoramento

### Logs do Streamlit Cloud
- Acesse o painel do app
- Clique em "Manage app"
- Veja os logs em tempo real

### Performance
- Monitor de recursos no painel
- Tempo de resposta da aplicação
- Uso de memória

## 🔄 Atualizações

Para atualizar a aplicação:

1. **Faça as mudanças** no código local
2. **Commit e push** para o repositório
3. **Deploy automático** será acionado
4. **Aguarde** a atualização (1-2 minutos)

## 📞 Suporte

- **Documentação**: https://docs.streamlit.io/streamlit-cloud
- **Community**: https://discuss.streamlit.io
- **Status**: https://status.streamlit.io

---

**🎉 Sua aplicação está pronta para o Streamlit Cloud!**