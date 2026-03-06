from pathlib import Path

# Localização base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Definição das pastas de dados
RAW_DIR = BASE_DIR / "data" / "raw"
BACKUP_DIR = BASE_DIR / "data" / "backups"
HISTORICO_DIR = BASE_DIR / "data" / "historico"

# Garante que as pastas existem
RAW_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
HISTORICO_DIR.mkdir(parents=True, exist_ok=True)

# URL do WebApp (Google Apps Script)
WEBAPP_URL = "https://script.google.com/macros/s/SEU_ID_DO_APPS_SCRIPT/exec"

# ============================================================
# PLANILHAS QUE PRECISAM DE UPLOAD MANUAL (CSV ou XLSX)
# (Google Sheets restritos à organização KaBuM)
# ============================================================
PLANILHAS_UPLOAD = [
    {
        "nome": "RMA | Garantia e Arrependimento",
        "chave_unica": ["REGISTRO", "PEDIDO", "OS"],
        "filtros": {},
    },
    {
        "nome": "Cadastro Computadores (respostas)",
        "chave_unica": ["Carimbo de data/hora", "OS", "Pedido"],
        "filtros": {},
    },
]

# ============================================================
# PLANILHAS DA REDE INTERNA (leitura automática)
# ============================================================
CAMINHO_REDE_DEVOLUCAO = r"\\10.200.1.7\grupokabum\Departamentos\RMA\Stephani"

PLANILHAS_REDE = [
    {
        "nome": "Devoluções 2026",
        "caminho": CAMINHO_REDE_DEVOLUCAO,
        "arquivo": "26_Devoluções_Base analítica_Consolidado (2026).xlsx",
        "aba": "Planilha1",
        "filtros": {"Monte_o_seu": True},
        "chave_unica": ["NFe_Numero_Pedido", "NFe_Numero"],
    },
    {
        "nome": "Devoluções 2025 (histórico)",
        "caminho": CAMINHO_REDE_DEVOLUCAO,
        "arquivo": "25_Devoluções_Base analítica_Consolidado (2025).xlsx",
        "aba": "Planilha1",
        "filtros": {"Monte_o_seu": True},
        "chave_unica": ["NFe_Numero_Pedido", "NFe_Numero"],
        "somente_historico": True,  # carrega apenas 1 vez, não reprocessa
    },
]