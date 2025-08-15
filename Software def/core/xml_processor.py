"""
Processador de arquivos XML de NFe
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from decimal import Decimal

from models.nota_fiscal import ItemNFe
from utils.logger import SystemLogger
from utils.exceptions import XMLProcessingError
from utils.validators import Validators

class XMLProcessor:
    """Processador de XML de NFe"""
    
    def __init__(self):
        self.logger = SystemLogger('xml_processor')
        self.validators = Validators()
    
    def processar_xml_nfe(self, xml_content: bytes) -> Dict[str, Any]:
        """Processa XML da NFe e extrai dados dos produtos"""
        try:
            # Parse do XML
            root = ET.fromstring(xml_content)
            
            # Namespace padrão da NFe
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Extrair dados da NFe
            dados_nfe = self._extrair_dados_nfe(root, ns)
            
            # Extrair produtos
            produtos = self._extrair_produtos(root, ns)
            
            # Extrair dados de transporte (frete)
            dados_transporte = self._extrair_dados_transporte(root, ns)
            
            return {
                'dados_nfe': dados_nfe,
                'produtos': produtos,
                'transporte': dados_transporte,
                'total_produtos': len(produtos)
            }
            
        except ET.ParseError as e:
            self.logger.error(f"Erro no parse do XML: {e}")
            raise XMLProcessingError(f"XML inválido: {e}")
        except Exception as e:
            self.logger.error(f"Erro no processamento do XML: {e}")
            raise XMLProcessingError(f"Falha no processamento: {e}")
    
    def _extrair_dados_nfe(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados gerais da NFe"""
        try:
            # Chave da NFe
            inf_nfe = root.find('.//nfe:infNFe', ns)
            chave_nfe = inf_nfe.get('Id')[3:] if inf_nfe is not None else None
            
            # Dados do emitente
            emit = root.find('.//nfe:emit', ns)
            emitente = {
                'cnpj': self._get_text(emit, 'nfe:CNPJ', ns),
                'nome': self._get_text(emit, 'nfe:xNome', ns),
                'fantasia': self._get_text(emit, 'nfe:xFant', ns)
            } if emit is not None else {}
            
            # Dados do destinatário
            dest = root.find('.//nfe:dest', ns)
            destinatario = {
                'cnpj': self._get_text(dest, 'nfe:CNPJ', ns),
                'nome': self._get_text(dest, 'nfe:xNome', ns)
            } if dest is not None else {}
            
            # Totais da NFe
            total = root.find('.//nfe:total/nfe:ICMSTot', ns)
            totais = {
                'valor_produtos': float(self._get_text(total, 'nfe:vProd', ns) or 0),
                'valor_frete': float(self._get_text(total, 'nfe:vFrete', ns) or 0),
                'valor_total_nfe': float(self._get_text(total, 'nfe:vNF', ns) or 0)
            } if total is not None else {}
            
            return {
                'chave_nfe': chave_nfe,
                'emitente': emitente,
                'destinatario': destinatario,
                'totais': totais
            }
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados da NFe: {e}")
            return {}
    
    def _extrair_produtos(self, root: ET.Element, ns: Dict[str, str]) -> List[ItemNFe]:
        """Extrai produtos da NFe"""
        produtos = []
        
        for det in root.findall('.//nfe:det', ns):
            try:
                produto = self._processar_produto(det, ns)
                if produto:
                    produtos.append(produto)
            except Exception as e:
                item_num = det.get('nItem', 'N/A')
                self.logger.warning(f"Erro ao processar item {item_num}: {e}")
                continue
        
        return produtos
    
    def _processar_produto(self, det: ET.Element, ns: Dict[str, str]) -> Optional[ItemNFe]:
        """Processa um produto individual"""
        try:
            prod = det.find('nfe:prod', ns)
            if prod is None:
                return None
            
            # Dados básicos do produto
            codigo = self._get_text(prod, 'nfe:cProd', ns)
            descricao = self._get_text(prod, 'nfe:xProd', ns)
            ncm = self._get_text(prod, 'nfe:NCM', ns)
            quantidade = float(self._get_text(prod, 'nfe:qCom', ns) or 0)
            valor_unitario = float(self._get_text(prod, 'nfe:vUnCom', ns) or 0)
            valor_total = float(self._get_text(prod, 'nfe:vProd', ns) or 0)
            
            # Validações básicas
            if not codigo or not descricao or not ncm:
                self.logger.warning(f"Produto com dados incompletos: {codigo}")
                return None
            
            if quantidade <= 0 or valor_unitario <= 0:
                self.logger.warning(f"Produto com valores inválidos: {codigo}")
                return None
            
            # Normalizar NCM
            ncm_normalizado = self.validators.normalizar_ncm(ncm)
            if not self.validators.validar_ncm(ncm_normalizado):
                self.logger.warning(f"NCM inválido para produto {codigo}: {ncm}")
                return None
            
            # Valores opcionais
            valor_ipi = self._extrair_valor_ipi(det, ns)
            valor_frete = float(self._get_text(prod, 'nfe:vFrete', ns) or 0)
            
            return ItemNFe(
                codigo=codigo,
                descricao=descricao,
                ncm=ncm_normalizado,
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                valor_total=valor_total,
                valor_ipi=valor_ipi,
                valor_frete=valor_frete
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao processar produto: {e}")
            return None
    
    def _extrair_valor_ipi(self, det: ET.Element, ns: Dict[str, str]) -> float:
        """Extrai valor do IPI do produto"""
        try:
            # Tentar diferentes caminhos para o IPI
            caminhos_ipi = [
                './/nfe:IPI/nfe:IPITrib/nfe:vIPI',
                './/nfe:IPI/nfe:IPINT/nfe:vIPI',
                './/nfe:imposto/nfe:IPI/nfe:IPITrib/nfe:vIPI'
            ]
            
            for caminho in caminhos_ipi:
                elemento_ipi = det.find(caminho, ns)
                if elemento_ipi is not None and elemento_ipi.text:
                    return float(elemento_ipi.text)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _extrair_dados_transporte(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados de transporte da NFe"""
        try:
            transp = root.find('.//nfe:transp', ns)
            if transp is None:
                return {}
            
            # Modalidade do frete
            mod_frete = self._get_text(transp, 'nfe:modFrete', ns)
            
            # Valores de frete
            valor_frete = float(self._get_text(transp, 'nfe:vol/nfe:esp', ns) or 0)
            
            # Dados da transportadora
            transporta = transp.find('nfe:transporta', ns)
            dados_transportadora = {}
            if transporta is not None:
                dados_transportadora = {
                    'cnpj': self._get_text(transporta, 'nfe:CNPJ', ns),
                    'nome': self._get_text(transporta, 'nfe:xNome', ns)
                }
            
            return {
                'modalidade_frete': mod_frete,
                'valor_frete': valor_frete,
                'transportadora': dados_transportadora
            }
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados de transporte: {e}")
            return {}
    
    def _get_text(self, parent: Optional[ET.Element], path: str, ns: Dict[str, str]) -> Optional[str]:
        """Extrai texto de um elemento XML"""
        if parent is None:
            return None
        
        element = parent.find(path, ns)
        return element.text if element is not None else None

# Função auxiliar para compatibilidade
def parse_xml_produtos(xml_content: bytes) -> List[Dict[str, Any]]:
    """Função auxiliar para extrair produtos do XML (compatibilidade)"""
    processor = XMLProcessor()
    try:
        dados = processor.processar_xml_nfe(xml_content)
        
        # Converter ItemNFe para dict
        produtos_dict = []
        for item in dados.get('produtos', []):
            produto_dict = {
                'codigo': item.codigo,
                'descricao': item.descricao,
                'ncm': item.ncm,
                'quantidade': item.quantidade,
                'valor_unitario': item.valor_unitario,
                'valor_total': item.valor_total,
                'valor_ipi': item.valor_ipi,
                'valor_frete': item.valor_frete
            }
            
            # Adicionar chave da NFe se disponível
            if 'dados_nfe' in dados and 'chave_nfe' in dados['dados_nfe']:
                produto_dict['chave_nfe'] = dados['dados_nfe']['chave_nfe']
            
            produtos_dict.append(produto_dict)
        
        return produtos_dict
        
    except Exception as e:
        raise XMLProcessingError(f"Erro ao processar XML: {e}")