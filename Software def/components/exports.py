"""
Funções de exportação de dados
"""
import pandas as pd
import io
from models.resultado_calculo import ResultadoCalculoGeral

def export_to_excel(resultado: ResultadoCalculoGeral) -> bytes:
    """Exporta resultado para Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Aba resumo
        resumo_data = {
            'Métrica': ['Total de Itens', 'Valor dos Produtos', 'ICMS ST Total', 'Custo Final Total'],
            'Valor': [resultado.total_itens, resultado.total_valor_produtos, resultado.total_icms_st, resultado.total_custo_final]
        }
        df_resumo = pd.DataFrame(resumo_data)
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Aba detalhes
        detalhes_data = []
        for item in resultado.detalhes_itens:
            detalhes_data.append({
                'Código': item.codigo_item,
                'Descrição': item.descricao,
                'NCM': item.ncm,
                'Quantidade': item.quantidade,
                'Valor Unitário': item.valor_unitario,
                'Valor Total': item.valor_total,
                'Valor IPI': item.valor_ipi,
                'Valor Frete': item.valor_frete,
                'Frete por Fora': item.valor_frete_fora,
                'Tipo Tributação': item.tipo_tributacao,
                'Alíquota ICMS': item.aliquota_icms,
                'MVA Ajustado': item.mva_ajustado,
                'Redução BC ST': item.reducao_bc_st,
                'Redução BC Próprio': item.reducao_bc_proprio,
                'Base Cálculo ST': item.base_calculo_st,
                'ICMS ST Débito': item.valor_icms_st_debito,
                'ICMS Próprio Crédito': item.valor_icms_proprio_credito,
                'ICMS ST a Recolher': item.valor_icms_st_recolher,
                'Custo Final Unitário': item.valor_custo_final,
                'Possui Figura': item.possui_figura,
                'Observações': "; ".join(item.observacoes) if item.observacoes else ""
            })
        
        df_detalhes = pd.DataFrame(detalhes_data)
        df_detalhes.to_excel(writer, sheet_name='Detalhes', index=False)
    
    output.seek(0)
    return output.getvalue()