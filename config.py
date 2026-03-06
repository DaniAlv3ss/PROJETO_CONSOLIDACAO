from pathlib import Path

# Localização base do projeto (Torna o projeto portátil)
BASE_DIR = Path(__file__).resolve().parent

# Definição das pastas de dados
RAW_DIR = BASE_DIR / "data" / "raw"
BACKUP_DIR = BASE_DIR / "data" / "backups"
HISTORICO_DIR = BASE_DIR / "data" / "historico"

# Garante que as pastas existem no PC de qualquer pessoa
RAW_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
HISTORICO_DIR.mkdir(parents=True, exist_ok=True)

# URL do WebApp (Google Apps Script) - Substitua pelo ID real
WEBAPP_URL = "https://script.google.com/macros/s/SEU_ID_DO_APPS_SCRIPT/exec"

# ============================================================
# PLANILHAS DO GOOGLE SHEETS (Via Export CSV - Sem Google Cloud)
# ============================================================
# Planilhas que podem ser lidas online (são do usuário, abertas)
# ============================================================

PLANILHAS_ONLINE = [
    {
        "nome": "Cadastro Computadores (respostas)",
        "spreadsheet_id": "10l1w3d3HYSKFgSsnjOZ545efR-bdIECEkOR82IjV3TE",
        "gid": "150735617",
        "chave_unica": ["Carimbo de data/hora", "OS", "Pedido"],
    },
    {
        "nome": "Dash de Devolução - MOSPC",
        "spreadsheet_id": "1m3tOvmSOJIvRZY9uZNf1idSTEnUFbHIWPNh5tiHkKe0",
        "gid": "588129608",
        "chave_unica": [],  # sem carga incremental, lê tudo online
    },
]

# ============================================================
# Planilhas que precisam de upload manual (sem permissão online)
# ============================================================

PLANILHAS_UPLOAD = [
    {
        "nome": "RMA | Garantia e Arrependimento",
        "chave_unica": ["REGISTRO", "PEDIDO", "OS"],
    },
]