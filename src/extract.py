import pandas as pd
from io import StringIO
from config import RAW_DIR

# URL base para exportar uma aba do Google Sheets como CSV
_EXPORT_URL = (
    "https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    "/export?format=csv&gid={gid}"
)

def extrair_google_sheets(planilha_info):
    """
    Lê uma aba do Google Sheets via export CSV público.

    Parâmetros
    ----------
    planilha_info : dict
        Dicionário com as chaves:
        - "nome"            : str  → Nome amigável (para logs)
        - "spreadsheet_id"  : str  → ID da planilha
        - "gid"             : str  → ID da aba

    Retorna
    -------
    pd.DataFrame com os dados da aba.

    Requisitos
    ----------
    A planilha precisa estar compartilhada como:
    - "Qualquer pessoa com o link pode ver"  (ou)
    - "Qualquer pessoa na organização com o link"
    """
    nome = planilha_info["nome"]
    url = _EXPORT_URL.format(
        spreadsheet_id=planilha_info["spreadsheet_id"],
        gid=planilha_info["gid"],
    )

    try:
        df = pd.read_csv(url)

        if df.empty:
            raise ValueError(f"A planilha '{nome}' retornou vazia.")

        return df

    except Exception as e:
        raise Exception(
            f"Erro ao acessar a planilha '{nome}': {str(e)}\n"
            f"Verifique se a planilha está compartilhada com 'Qualquer pessoa com o link'."
        )

def extrair_csv_local(nome_arquivo):
    """
    Lê um arquivo CSV exportado de um sistema interno.

    O arquivo deve estar na pasta data/raw/.

    Parâmetros
    ----------
    nome_arquivo : str
        Nome do arquivo CSV (ex: "relatorio_sistema.csv")

    Retorna
    -------
    pd.DataFrame com os dados do CSV.
    """
    caminho = RAW_DIR / nome_arquivo

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo '{nome_arquivo}' não encontrado em data/raw/.\n"
            f"Caminho esperado: {caminho}"
        )

    try:
        df = pd.read_csv(caminho, encoding="utf-8")
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding="latin-1")
        return df
