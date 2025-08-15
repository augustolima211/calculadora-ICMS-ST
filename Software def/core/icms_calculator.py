"""
Calculadora de ICMS ST com fórmulas específicas
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from models.nota_fiscal import ItemNFe
from models.figura_tributaria import FiguraTributaria
from models.resultado_calculo import ResultadoCalculoItem, ResultadoCalculoGeral
from core.database_manager import DatabaseManager
from core.xml_processor import XMLProcessor
from utils.logger import SystemLogger
from utils.exceptions import CalculationError, ValidationError
from utils.validators import Validators

class ICMSCalculator:
    """Calculadora de ICMS ST com fórmulas específicas"""
    
    def __init__(self):
        self.logger = SystemLogger('icms_calculator')
        self.db_manager = DatabaseManager()
        self.xml_processor = XMLProcessor()
        self.validators = Validators()
        
        # Configurações de precisão decimal
        self.decimal_places = 2
        self.rounding = ROUND_HALF_UP
    
    def calcular_icms_st_xml(self, xml_content: bytes, frete_por_fora: float = 0.0) -> ResultadoCalculoGeral:
        """Calcula ICMS ST a partir de arquivo XML da NFe"""
        try:
            # Processar XML
            dados_xml = self.xml_processor.processar_xml_nfe(xml_content)
            
            if not dados_xml.get('produtos'):
                raise ValidationError("Nenhum produto encontrado na NFe")
            
            itens_nfe = dados_xml['produtos']
            chave_nfe = dados_xml.get('dados_nfe', {}).get('chave_nfe')
            
            # Aplicar rateio de frete por fora se necessário
            if frete_por_fora > 0:
                itens_nfe = self._ratear_frete_por_fora(itens_nfe, frete_por_fora)
            
            # Calcular ICMS ST
            return self.calcular_icms_st_itens(itens_nfe, chave_nfe, 'XML')
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo ICMS ST XML: {e}")
            raise CalculationError(f"Falha no cálculo: {e}")
    
    def calcular_icms_st_manual(self, dados_itens: List[Dict[str, Any]], frete_por_fora: float = 0.0) -> ResultadoCalculoGeral:
        """Calcula ICMS ST para dados inseridos manualmente"""
        try:
            # Converter dados manuais para ItemNFe
            itens_nfe = []
            for i, dados in enumerate(dados_itens):
                try:
                    item = self._converter_dados_manuais(dados, i + 1)
                    itens_nfe.append(item)
                except ValidationError as e:
                    self.logger.warning(f"Item {i + 1} inválido: {e}")
                    continue
            
            if not itens_nfe:
                raise ValidationError("Nenhum item válido fornecido")
            
            # Aplicar rateio de frete por fora se necessário
            if frete_por_fora > 0:
                itens_nfe = self._ratear_frete_por_fora(itens_nfe, frete_por_fora)
            
            # Calcular ICMS ST
            return self.calcular_icms_st_itens(itens_nfe, None, 'MANUAL')
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo ICMS ST manual: {e}")
            raise CalculationError(f"Falha no cálculo: {e}")
    
    def calcular_icms_st_itens(self, itens: List[ItemNFe], chave_nfe: Optional[str], origem: str) -> ResultadoCalculoGeral:
        """Calcula ICMS ST para lista de itens"""
        try:
            resultados_itens = []
            observacoes_gerais = []
            
            for item in itens:
                try:
                    resultado_item = self._calcular_item_icms_st(item)
                    resultados_itens.append(resultado_item)
                except Exception as e:
                    self.logger.error(f"Erro no cálculo do item {item.codigo}: {e}")
                    resultado_erro = self._criar_resultado_erro(item, str(e))
                    resultados_itens.append(resultado_erro)
            
            # Calcular totais
            resultado_geral = self._calcular_totais(
                resultados_itens, 
                origem, 
                chave_nfe, 
                observacoes_gerais
            )
            
            self.logger.info(f"Cálculo ICMS ST concluído: {len(resultados_itens)} itens processados")
            return resultado_geral
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo ICMS ST: {e}")
            raise CalculationError(f"Falha no cálculo: {e}")
    
    def _calcular_item_icms_st(self, item: ItemNFe) -> ResultadoCalculoItem:
        """Calcula ICMS ST para um item usando as fórmulas corretas"""
        observacoes = []
        
        # Normalizar NCM
        ncm_normalizado = self.validators.normalizar_ncm(item.ncm)
        
        # Buscar figura tributária
        figura = self.db_manager.get_figura_tributaria(ncm_normalizado)
        
        if not figura:
            observacoes.append(f"Figura tributária não encontrada para NCM {ncm_normalizado}")
            return self._criar_resultado_sem_figura(item, observacoes)
        
        # Validar se é ST
        if figura.tipo_tributacao != 'st':
            observacoes.append("Item não sujeito à substituição tributária")
            return self._criar_resultado_sem_st(item, figura, observacoes)
        
        # Determinar alíquota ICMS (12% ou 4%)
        aliquota_icms = self._determinar_aliquota_icms(figura, item)
        mva_ajustado = figura.mva_ajustado_12 if aliquota_icms == 12.0 else figura.mva_ajustado_4
        
        # Calcular frete por fora rateado
        frete_fora_rateado = getattr(item, 'valor_frete_fora', 0.0)
        
        # FÓRMULA DÉBITO ST: (Valor produto + IPI + Frete + Frete fora) * (1 + MVA ajustado) * (1 - redução base ST) * 18%
        base_calculo_bruta = item.valor_total + item.valor_ipi + item.valor_frete + frete_fora_rateado
        
        # Aplicar MVA ajustado
        mva_decimal = mva_ajustado / 100
        base_com_mva = base_calculo_bruta * (1 + mva_decimal)
        
        # Aplicar redução da base de cálculo ST
        fator_reducao_st = (100 - figura.reducao_bc_icms_st) / 100
        base_calculo_st = base_com_mva * fator_reducao_st
        
        # Calcular débito ST (sempre 18%)
        valor_icms_st_debito = base_calculo_st * 0.18
        
        # FÓRMULA CRÉDITO ICMS PRÓPRIO: Valor produto * (1 - redução base próprio) * alíquota ICMS
        base_icms_proprio = item.valor_total
        
        # Aplicar redução da base de cálculo próprio
        fator_reducao_proprio = (100 - figura.reducao_bc_icms_proprio) / 100
        base_icms_proprio_final = base_icms_proprio * fator_reducao_proprio
        
        # Calcular crédito ICMS próprio
        aliquota_decimal = aliquota_icms / 100
        valor_icms_proprio_credito = base_icms_proprio_final * aliquota_decimal
        
        # ICMS ST A RECOLHER = DÉBITO - CRÉDITO
        valor_icms_st_recolher = valor_icms_st_debito - valor_icms_proprio_credito
        
        # Garantir que não seja negativo
        if valor_icms_st_recolher < 0:
            valor_icms_st_recolher = 0.0
            observacoes.append("ICMS ST a recolher zerado (crédito maior que débito)")
        
        # CUSTO FINAL UNITÁRIO: (Valor produto + ICMS ST a recolher + IPI + Frete + Frete fora) / quantidade
        valor_custo_total = item.valor_total + valor_icms_st_recolher + item.valor_ipi + item.valor_frete + frete_fora_rateado
        valor_custo_final = valor_custo_total / item.quantidade if item.quantidade > 0 else 0
        
        return ResultadoCalculoItem(
            codigo_item=item.codigo,
            descricao=item.descricao,
            ncm=item.ncm,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor_total=item.valor_total,
            valor_ipi=item.valor_ipi,
            valor_frete=item.valor_frete,
            valor_frete_fora=frete_fora_rateado,
            tipo_tributacao=figura.tipo_tributacao,
            aliquota_icms=aliquota_icms,
            mva_ajustado=mva_ajustado,
            reducao_bc_st=figura.reducao_bc_icms_st,
            reducao_bc_proprio=figura.reducao_bc_icms_proprio,
            base_calculo_st=self._round_decimal(base_calculo_st),
            valor_icms_st_debito=self._round_decimal(valor_icms_st_debito),
            valor_icms_proprio_credito=self._round_decimal(valor_icms_proprio_credito),
            valor_icms_st_recolher=self._round_decimal(valor_icms_st_recolher),
            valor_icms_st=self._round_decimal(valor_icms_st_recolher),
            valor_custo_final=self._round_decimal(valor_custo_final),
            possui_figura=True,
            observacoes=observacoes
        )
    
    def _ratear_frete_por_fora(self, itens: List[ItemNFe], total_frete: float) -> List[ItemNFe]:
        """Rateia o frete por fora proporcionalmente ao valor dos itens"""
        try:
            total_valor_itens = sum(item.valor_total for item in itens)
            
            if total_valor_itens == 0:
                return itens
            
            itens_com_frete = []
            frete_rateado_acumulado = 0.0
            
            for i, item in enumerate(itens):
                # Calcular proporção do item
                proporcao = item.valor_total / total_valor_itens
                
                # Calcular frete rateado (último item recebe o ajuste)
                if i == len(itens) - 1:
                    frete_rateado = total_frete - frete_rateado_acumulado
                else:
                    frete_rateado = self._round_decimal(total_frete * proporcao)
                    frete_rateado_acumulado += frete_rateado
                
                # Adicionar frete por fora como atributo
                setattr(item, 'valor_frete_fora', frete_rateado)
                itens_com_frete.append(item)
            
            return itens_com_frete
            
        except Exception as e:
            self.logger.error(f"Erro no rateio de frete: {e}")
            return itens
    
    def _determinar_aliquota_icms(self, figura: FiguraTributaria, item: ItemNFe) -> float:
        """Determina qual alíquota ICMS usar (12% ou 4%)"""
        # Por padrão, usar 12% (pode ser customizada conforme regras específicas)
        return 12.0
    
    def _criar_resultado_sem_figura(self, item: ItemNFe, observacoes: List[str]) -> ResultadoCalculoItem:
        """Cria resultado para item sem figura tributária"""
        frete_fora = getattr(item, 'valor_frete_fora', 0.0)
        
        return ResultadoCalculoItem(
            codigo_item=item.codigo,
            descricao=item.descricao,
            ncm=item.ncm,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor_total=item.valor_total,
            valor_ipi=item.valor_ipi,
            valor_frete=item.valor_frete,
            valor_frete_fora=frete_fora,
            valor_custo_final=item.valor_total + item.valor_ipi + item.valor_frete + frete_fora,
            possui_figura=False,
            observacoes=observacoes
        )
    
    def _criar_resultado_sem_st(self, item: ItemNFe, figura: FiguraTributaria, observacoes: List[str]) -> ResultadoCalculoItem:
        """Cria resultado para item que não tem ST"""
        frete_fora = getattr(item, 'valor_frete_fora', 0.0)
        
        return ResultadoCalculoItem(
            codigo_item=item.codigo,
            descricao=item.descricao,
            ncm=item.ncm,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor_total=item.valor_total,
            valor_ipi=item.valor_ipi,
            valor_frete=item.valor_frete,
            valor_frete_fora=frete_fora,
            tipo_tributacao=figura.tipo_tributacao,
            reducao_bc_st=figura.reducao_bc_icms_st,
            reducao_bc_proprio=figura.reducao_bc_icms_proprio,
            valor_custo_final=item.valor_total + item.valor_ipi + item.valor_frete + frete_fora,
            possui_figura=True,
            observacoes=observacoes
        )
    
    def _criar_resultado_erro(self, item: ItemNFe, erro: str) -> ResultadoCalculoItem:
        """Cria resultado para item com erro"""
        frete_fora = getattr(item, 'valor_frete_fora', 0.0)
        
        return ResultadoCalculoItem(
            codigo_item=item.codigo,
            descricao=item.descricao,
            ncm=item.ncm,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor_total=item.valor_total,
            valor_ipi=item.valor_ipi,
            valor_frete=item.valor_frete,
            valor_frete_fora=frete_fora,
            tipo_tributacao='ERRO',
            observacoes=[f"Erro no cálculo: {erro}"]
        )
    
    def _calcular_totais(self, resultados_itens: List[ResultadoCalculoItem], origem: str, chave_nfe: Optional[str], observacoes_gerais: List[str]) -> ResultadoCalculoGeral:
        """Calcula totais gerais do cálculo"""
        total_itens = len(resultados_itens)
        total_valor_produtos = sum(item.valor_total for item in resultados_itens)
        total_icms_st = sum(item.valor_icms_st_recolher for item in resultados_itens)
        total_custo_final = sum(item.valor_custo_final * item.quantidade for item in resultados_itens)
        
        itens_com_st = sum(1 for item in resultados_itens if item.valor_icms_st_recolher > 0)
        itens_sem_figura = sum(1 for item in resultados_itens if not item.possui_figura)
        
        # Adicionar observações gerais
        if itens_sem_figura > 0:
            observacoes_gerais.append(f"{itens_sem_figura} itens sem figura tributária")
        
        if itens_com_st == 0:
            observacoes_gerais.append("Nenhum item com ICMS ST calculado")
        
        return ResultadoCalculoGeral(
            origem=origem,
            chave_nfe=chave_nfe,
            total_itens=total_itens,
            total_valor_produtos=self._round_decimal(total_valor_produtos),
            total_icms_st=self._round_decimal(total_icms_st),
            total_custo_final=self._round_decimal(total_custo_final),
            itens_com_st=itens_com_st,
            itens_sem_figura=itens_sem_figura,
            data_calculo=datetime.now(),
            detalhes_itens=resultados_itens,
            observacoes_gerais=observacoes_gerais
        )
    
    def _converter_dados_manuais(self, dados: Dict[str, Any], index: int) -> ItemNFe:
        """Converte dados manuais para ItemNFe"""
        try:
            # Validar campos obrigatórios
            campos_obrigatorios = ['codigo', 'descricao', 'ncm', 'quantidade', 'valor_unitario']
            for campo in campos_obrigatorios:
                if campo not in dados or dados[campo] is None:
                    raise ValidationError(f"Campo obrigatório ausente: {campo}")
            
            # Validar tipos e valores
            quantidade = float(dados['quantidade'])
            valor_unitario = float(dados['valor_unitario'])
            
            if quantidade <= 0:
                raise ValidationError("Quantidade deve ser maior que zero")
            
            if valor_unitario <= 0:
                raise ValidationError("Valor unitário deve ser maior que zero")
            
            # Validar NCM
            ncm = str(dados['ncm']).strip()
            if not self.validators.validar_ncm(ncm):
                raise ValidationError(f"NCM inválido: {ncm}")
            
            # Calcular valor total
            valor_total = quantidade * valor_unitario
            
            # Valores opcionais
            valor_ipi = float(dados.get('valor_ipi', 0.0))
            valor_frete = float(dados.get('valor_frete', 0.0))
            
            return ItemNFe(
                codigo=str(dados['codigo']),
                descricao=str(dados['descricao']),
                ncm=self.validators.normalizar_ncm(ncm),
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                valor_total=valor_total,
                valor_ipi=valor_ipi,
                valor_frete=valor_frete
            )
            
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Erro na conversão de dados do item {index}: {e}")
    
    def _round_decimal(self, value: float) -> float:
        """Arredonda valor para o número de casas decimais configurado"""
        decimal_value = Decimal(str(value))
        rounded = decimal_value.quantize(
            Decimal('0.01'), 
            rounding=self.rounding
        )
        return float(rounded)