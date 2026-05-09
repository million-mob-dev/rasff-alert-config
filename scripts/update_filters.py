import json
import sys
import requests

API_BASE = "https://webgate.ec.europa.eu/rasff-window/backend/public"
ENDPOINTS = {
    'notifyingCountries': f"{API_BASE}/organization/list/",
    'countries': f"{API_BASE}/country/list/",
    'productCategories': f"{API_BASE}/productCategory/list/en/",
    'hazardCategories': f"{API_BASE}/hazardCategory/list/en/",
    'riskDecisions': f"{API_BASE}/riskDecision/list/en/",
    'notificationClassifications': f"{API_BASE}/notificationClassification/list/en/",
    'actionTaken': f"{API_BASE}/actionTaken/list/en/",
    'notificationTypes': f"{API_BASE}/productType/list/en/",
    'notificationBasis': f"{API_BASE}/notificationBasis/list/en/",
    'notificationStatus': f"{API_BASE}/notificationStatus/list/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0",
    "Accept": "application/json",
}

def extract_map(data, key_name, value_key='description', id_key='id'):
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        if key_name in data:
            items = data[key_name]
        elif 'content' in data:
            items = data['content']
        else:
            items = list(data.values())[0] if data else []
            
    res = {}
    for item in items:
        name = item.get(value_key, item.get('englishShortName', 'Unknown'))
        res[name] = item[id_key]
    return dict(sorted(res.items()))

def fetch_live_filters():
    print("A descarregar dicionários da API RASFF...")
    live_filters = {}
    for filter_key, url in ENDPOINTS.items():
        print(f"   -> {filter_key}...")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            list_key = filter_key
            if filter_key == 'notifyingCountries': list_key = 'organizations'
            elif filter_key == 'actionTaken': list_key = 'actionTakens'
            elif filter_key == 'notificationStatus': list_key = 'response'
            val_key = 'englishShortName' if filter_key == 'countries' else 'description'
            live_filters[filter_key] = extract_map(resp.json(), list_key, val_key)
        except Exception as e:
            print(f"Erro ao descarregar {filter_key}: {e}")
            sys.exit(1)
    return live_filters

def main():
    live_filters = fetch_live_filters()
    
    with open('rasff_filters_en.json', 'r', encoding='utf-8') as f:
        local_en = json.load(f)
    with open('rasff_filters_pt.json', 'r', encoding='utf-8') as f:
        local_pt = json.load(f)

    changed = False
    
    for category, new_data in live_filters.items():
        if category not in local_en:
            local_en[category] = {}
        if category not in local_pt:
            local_pt[category] = {}
            
        # 1. Adicionar novos ou atualizar EN
        for key, value in new_data.items():
            if key not in local_en[category] or local_en[category][key] != value:
                local_en[category][key] = value
                changed = True
            
            # 2. Injetar no PT apenas se o ID nao existir (preservando as tuas traducoes)
            pt_ids = list(local_pt[category].values())
            if value not in pt_ids:
                local_pt[category][key] = value
                changed = True
                
        # 3. Remover chaves velhas do EN
        for key in list(local_en[category].keys()):
            if key not in new_data:
                del local_en[category][key]
                changed = True
                
        # 4. Remover do PT as chaves cujos IDs já não existem na API oficial
        live_ids = list(new_data.values())
        for pt_key in list(local_pt[category].keys()):
            if local_pt[category][pt_key] not in live_ids:
                del local_pt[category][pt_key]
                changed = True
                
        # Ordenar dicionários no final para ficarem limpos no git
        local_en[category] = dict(sorted(local_en[category].items()))
        local_pt[category] = dict(sorted(local_pt[category].items()))

    if changed:
        print("Alterações detetadas! A atualizar JSONs...")
        with open('rasff_filters_en.json', 'w', encoding='utf-8') as f:
            json.dump(local_en, f, indent=2, ensure_ascii=False)
        with open('rasff_filters_pt.json', 'w', encoding='utf-8') as f:
            json.dump(local_pt, f, indent=2, ensure_ascii=False)
    else:
        print("Tudo atualizado. Nenhuma alteração na API.")

if __name__ == "__main__":
    main()
