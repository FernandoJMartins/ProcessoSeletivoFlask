
import requests
from config import api_url, headers, PLATFORM_NAMES
from utils import export_csv, get_index

def get_all_plataforms_data():
    """ Obtém os dados de todas as plataformas. """
    all_fields = set () # Cria um conjunto vazio para armazenar os campos
    p_data = {} # Dicionário para armazenar os dados de cada plataforma


    for p in PLATFORM_NAMES:
        
        data, field_names = get_data(p)
        p_name = PLATFORM_NAMES.get(p, p)
        p_data[p] = (data, field_names)
        all_fields.update(field_names) # Adiciona os campos ao conjunto

    # Normalizar os dados, garantindo que todas as linhas tenham os mesmos campos
    normalized_data = []
    all_fields = list (all_fields) # Converte o conjunto para lista

    
    for platform, (data, field_names) in p_data.items():
        for row in data:

            row_dict = dict(zip(["Platform", "Account Id", "Account Name"] + field_names, row))

            spend = float(row_dict.get("spend", row_dict.get("cost", 0)))  # Pode ser "spend" ou "cost"
            clicks = int(row_dict.get("clicks", 0))  # Pode não existir

            if clicks > 0:
                row_dict["cpc"] = spend / clicks
            
            cpc = round(spend / clicks, 2) if clicks > 0 else 0

            row_dict["cpc"] = cpc

            normalized_row = [row_dict.get(field, '') for field in ["Platform", "Account Id", "Account Name"] + all_fields]
            normalized_data.append(normalized_row)

    return normalized_data, all_fields

    

def get_data(platform):
    """ Obtém dados de uma única plataforma. """
    data = []
    accounts = get_accounts(platform)
    p_name = PLATFORM_NAMES.get(platform, platform)

    for acc in accounts:
        acc_id = acc.get('id')
        acc_name = acc.get('name')
        acc_token = acc.get('token')

        url = f'{api_url}fields?platform={platform}'
        request = requests.get(url, headers = headers)

        if request.status_code != 200:
            return request.text

        fields = request.json().get('fields', [])
        field_names = [f['value'] for f in fields]

        url = f'{api_url}insights?platform={platform}&account={acc_id}&token={acc_token}&fields={",".join(field_names)}'
        response = requests.get(url, headers=headers)

        insights = response.json().get('insights', [])

        for i in insights:
            row = [p_name, acc_id, acc_name] + [i.get(field, '') for field in field_names]
            data.append(row)
    return data, field_names



def get_accounts(platform):
    """ Obtém as contas de uma única plataforma. """
    url = f'{api_url}/accounts?platform={platform}'
    
    api_response = requests.get(url, headers=headers)

    if api_response.status_code != 200:
        return api_response.text

    data = api_response.json()

    # Obtém a lista de contas (se houver)
    accounts = data.get('accounts', [])
    if not accounts:
        return f'Nenhuma conta encontrada para a platform'

    return accounts



def service_get_platform(platform):
    """ endpoint /{{platform}} """
    data, field_names = get_data(platform)
    return export_csv(data, field_names)


def service_get_platform_resumo(platform):
    """ endpoint /{{platform}}/resumo """
    data, field_names = get_data(platform)
    p_name = PLATFORM_NAMES.get(platform, platform)
    new_data = {}
    sumSpend, sumClicks, sumImpressions = {}, {}, {} # Armazena a soma dos gastos e clicks de cada conta

    indexCpc, indexSpend, indexClicks, indexImpressions, indexCtr = get_index(field_names)

    for row in data: 
        
        acc_id = row[1]
        acc_name = row[2]

        if acc_id not in new_data:
            sumSpend[acc_id], sumClicks[acc_id], sumImpressions[acc_id] = 0, 0, 0 # Inicializa as variáveis de soma
            new_data[acc_id] = [p_name, acc_id, acc_name] + [0] *(len(field_names)) # Inicializa a lista com zeros
            
 
        for i in range(3, len(row)):
            
            if i == indexImpressions:
                sumImpressions[acc_id] += int(row[i]) # Soma as impressões da conta
            if i == indexSpend:
                sumSpend[acc_id] += float(row[i]) # Soma os gastos da conta
            if i == indexClicks:
                sumClicks[acc_id] += int(row[i]) # Soma os clicks da conta

            if isinstance(row[i], (int, float) or isinstance(row[i], str) and row[i].isdigit()):    
                new_data[acc_id][i] += row[i]
            else:
                new_data[acc_id][i] = '' # Se não for numérico, deixa vazio
                    
    for acc_id in new_data:   # CALCULA O CPC DA FORMA MATEMATICAMENTE CORRETA!!!!
        if sumClicks[acc_id] > 0:
            new_data[acc_id][indexCpc] = round(sumSpend[acc_id] / sumClicks[acc_id], 2) #Calcula o CPC
        else: # Se não houver clicks, cpc = 0
            new_data[acc_id][indexCpc] = 0 

        if sumImpressions[acc_id] > 0 and indexCtr: # Se houver impressões e ctr no cabeçalho
            new_data[acc_id][indexCtr] = round(sumClicks[acc_id] / sumImpressions[acc_id], 2)


    return export_csv(new_data.values(), field_names)


def service_get_geral():
    """ endpoint /geral """
    normalized_data, all_fields = get_all_plataforms_data()
    return export_csv(normalized_data, all_fields)

def service_get_geral_resumo():
    """ endpoint /geral/resumo """
    new_data = {}

    data, field_names = get_all_plataforms_data()

    for row in data:
        p_name = row[0]

        if p_name not in new_data:
            new_data[p_name] = [p_name] + [''] * (len(field_names) - 1) 

        for i in range(3, len(row)):  
            if i < len(new_data[p_name]):  # Verifica se o índice está dentro do intervalo
                if isinstance(row[i], (int, float)):  # garante q o valor é numérico
                    if isinstance(new_data[p_name][i], (int, float)):  # garante que ja foi inicializado como numérico
                        new_data[p_name][i] += row[i]
                    else:
                        new_data[p_name][i] = row[i]  # Inicializa a coluna com o valor
                else:
                    new_data[p_name][i] = row[i]  # Se não for numérico, deixa vazio
            else:
                new_data[p_name].append('')  
                

    return export_csv(new_data.values(), field_names)    