from pathlib import Path

# Localização base do projeto (Torna o projeto portátil)
BASE_DIR = Path(__file__).resolve().parent

# Definição das pastas de dados
RAW_DIR = BASE_DIR / "data" / "raw"
BACKUP_DIR = BASE_DIR / "data" / "backups"

# Garante que as pastas existem no PC de qualquer pessoa
RAW_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# URL do WebApp (Google Apps Script) - Substitua pelo ID real
WEBAPP_URL = "https://script.google.com/macros/s/SEU_ID_DO_APPS_SCRIPT/exec"

# ============================================================
# PLANILHAS DO GOOGLE SHEETS (Via Export CSV - Sem Google Cloud)
# ============================================================
# Cada planilha é um dicionário com:
#   - "nome": Nome amigável (aparece no log do Streamlit)
#   - "spreadsheet_id": O ID da planilha (extraído da URL)
#   - "gid": O ID da aba específica (extraído da URL após #gid=)
#
# Como encontrar:
#   URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=GID
# ============================================================

PLANILHAS_GOOGLE = [
    {
        "nome": "RMA | Garantia e Arrependimento",
        "spreadsheet_id": "1KTZTyHf_Lj3Sl6mA9trq38k5WgQJxBCRsoL7aP_itXI",
        "gid": "2112567324",
    },
    {
        "nome": "Cadastro Computadores (respostas)",
        "spreadsheet_id": "10l1w3d3HYSKFgSsnjOZ545efR-bdIECEkOR82IjV3TE",
        "gid": "150735617",
    },
    {
        "nome": "Dash de Devolução - MOSPC",
        "spreadsheet_id": "1m3tOvmSOJIvRZY9uZNf1idSTEnUFbHIWPNh5tiHkKe0",
        "gid": "588129608",
    },
]