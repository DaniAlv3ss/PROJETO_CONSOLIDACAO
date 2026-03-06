import json
import requests
import pandas as pd
from datetime import datetime
from config import BACKUP_DIR, WEBAPP_URL

def gerar_backup_local(df):
    """Salva o DataFrame consolidado como um arquivo JSON local."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_nome = f"consolidado_{timestamp}.json"
    caminho_completo = BACKUP_DIR / arquivo_nome
    
    # Converte para lista de dicionários (formato JSON)
    dados = df.to_dict(orient='records')
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    return dados, arquivo_nome

def enviar_webapp(dados_json):
    """Envia o JSON via POST para o Google Apps Script."""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBAPP_URL, json=dados_json, headers=headers, timeout=30)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)
