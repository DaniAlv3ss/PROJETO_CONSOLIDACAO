from pathlib import Path

# Localização base do projeto (Torna o projeto portátil)
BASE_DIR = Path(__file__).resolve().parent

# Definição das pastas de dados
RAW_DIR = BASE_DIR / "data" / "raw"
BACKUP_DIR = BASE_DIR / "data" / "backups"

# Garante que as pastas existem no PC de qualquer pessoa
RAW_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Credenciais e URLs (Substitua pelo ID real do Apps Script)
WEBAPP_URL = "https://script.google.com/macros/s/SEU_ID_DO_APPS_SCRIPT/exec"
GOOGLE_JSON_KEY = BASE_DIR / "credenciais.json"

# Nomes das planilhas que o script deve procurar no Google Drive
PLANILHAS_PARA_CONSOLIDAR = ["Base_Vendas", "Base_Estoque", "Base_Sistemas"]