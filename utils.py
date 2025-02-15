from flask import Response
import requests

def export_csv(data, field_names):
    """Exporta os dados para um arquivo CSV e retorna o arquivo"""
    csv = 'Platform,Account Id,Account Name,' + ','.join(field_names) + '\n'

    for row in data:
        csv += ','.join(map(str,row)) + '\n'
    
    return Response(csv, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=insights.csv'})


def get_index(fields): #necessário para fazer o calculo CORRETAMENTE do CPC no endpoint "/{{plataforma}}/resumo"
    """Obtém os índices dos campos cpc, spend, clicks, impressions e ctr""" # A formula matemática para calcular a SOMA de CPC's é: ∑(CPC) = ∑(Spend) / ∑(Clicks)
    for f in fields:
        if f == 'cpc' or f == 'cost_per_click':
            indexCpc = fields.index(f) + 3
        elif f == 'spend' or f == 'cost':
            indexSpend = fields.index(f) + 3
        elif f == 'clicks':
            indexClicks = fields.index(f) + 3
        elif f == 'impressions' or f == 'views':
            indexImpressions = fields.index(f) + 3

    indexCtr = fields.index('ctr') + 3 if 'ctr' in fields else None

    if 'cost_per_click' not in fields and 'cpc' not in fields: # Se não houver cpc no cabeçalho, adiciona-o
        indexCpc = len(fields) + 3
        fields.append('cpc')
    
    return indexCpc, indexSpend, indexClicks, indexImpressions, indexCtr