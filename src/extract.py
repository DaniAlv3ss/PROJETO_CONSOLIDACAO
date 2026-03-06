import pandas as pd
import gspread
from config import GOOGLE_JSON_KEY

def extrair_google_sheets(nome_planilha):
    """Lê dados do Google Sheets usando uma Service Account."""
    try:
        gc = gspread.service_account(filename=str(GOOGLE_JSON_KEY))
        sh = gc.open(nome_planilha)
        worksheet = sh.get_worksheet(0)  # Pega a primeira aba
        df = pd.DataFrame(worksheet.get_all_records())
        return df
    except Exception as e:
        raise Exception(f"Erro ao acessar a planilha '{nome_planilha}': {str(e)}")

def extrair_sistema_externo(nome_arquivo):
    """Simula a leitura de um arquivo exportado por outro sistema."""
    # Exemplo: Lendo um CSV que o outro sistema deixou na pasta raw
    # df = pd.read_csv(RAW_DIR / nome_arquivo)
    return pd.DataFrame()  # Placeholder
