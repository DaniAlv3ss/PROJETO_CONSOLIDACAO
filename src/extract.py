import re
import shutil
import pandas as pd
from io import StringIO
from datetime import datetime
from config import RAW_DIR, HISTORICO_DIR, BACKUP_DIR

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


# ============================================================
# Funções de Carga Incremental
# ============================================================

def _sanitizar_nome(nome_planilha):
    """Remove caracteres especiais e substitui espaços por underscore."""
    nome = re.sub(r"[^\w\s]", "", nome_planilha)
    nome = re.sub(r"\s+", "_", nome.strip())
    return nome


def carregar_base_historica(nome_planilha):
    """
    Carrega o CSV histórico de data/historico/{nome_planilha}.csv.

    Retorna DataFrame vazio se o arquivo não existir.
    """
    nome_arquivo = _sanitizar_nome(nome_planilha) + ".csv"
    caminho = HISTORICO_DIR / nome_arquivo

    if not caminho.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(caminho, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(caminho, encoding="latin-1")


def salvar_base_historica(df, nome_planilha):
    """
    Salva o DataFrame atualizado em data/historico/{nome_planilha}.csv.
    Faz backup da versão anterior em data/backups/ com timestamp.
    """
    nome_arquivo = _sanitizar_nome(nome_planilha) + ".csv"
    caminho = HISTORICO_DIR / nome_arquivo

    # Backup da versão anterior antes de sobrescrever
    if caminho.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"{_sanitizar_nome(nome_planilha)}_{timestamp}.csv"
        shutil.copy2(caminho, BACKUP_DIR / nome_backup)

    df.to_csv(caminho, index=False, encoding="utf-8")


def carga_incremental(df_novo, nome_planilha, colunas_chave):
    """
    Realiza a carga incremental comparando df_novo com a base histórica.

    Parâmetros
    ----------
    df_novo : pd.DataFrame
        Dados novos (vindos do upload ou leitura online).
    nome_planilha : str
        Nome amigável da planilha (usado para nomear o arquivo histórico).
    colunas_chave : list[str]
        Colunas que formam a chave única para identificar registros duplicados.

    Retorna
    -------
    tuple(pd.DataFrame, int)
        DataFrame atualizado (base histórica + novos registros) e
        quantidade de novos registros adicionados.

    Raises
    ------
    ValueError
        Se alguma coluna da chave_unica não existir em df_novo.
    """
    # Validar colunas-chave
    colunas_ausentes = [c for c in colunas_chave if c not in df_novo.columns]
    if colunas_ausentes:
        raise ValueError(
            f"Planilha '{nome_planilha}': as seguintes colunas da chave única "
            f"não foram encontradas no DataFrame: {colunas_ausentes}.\n"
            f"Colunas disponíveis: {list(df_novo.columns)}"
        )

    base_historica = carregar_base_historica(nome_planilha)

    # Primeira execução: salva tudo e retorna
    if base_historica.empty:
        salvar_base_historica(df_novo, nome_planilha)
        return df_novo, len(df_novo)

    # Cria chave composta em ambos os DataFrames.
    # Nota: valores NaN são convertidos para a string 'nan'; se as colunas-chave
    # puderem conter nulos, considere tratar esses valores antes de chamar esta função.
    def _chave(df):
        return df[colunas_chave].astype(str).agg("|".join, axis=1)

    df_novo = df_novo.copy()
    base_historica = base_historica.copy()

    df_novo["_chave_composta"] = _chave(df_novo)

    # Garante que a base histórica também tenha as colunas-chave
    colunas_ausentes_hist = [c for c in colunas_chave if c not in base_historica.columns]
    if colunas_ausentes_hist:
        # Base histórica não tem as colunas-chave: trata como vazia
        salvar_base_historica(df_novo.drop(columns=["_chave_composta"]), nome_planilha)
        return df_novo.drop(columns=["_chave_composta"]), len(df_novo)

    base_historica["_chave_composta"] = _chave(base_historica)

    # Identifica registros novos
    chaves_existentes = set(base_historica["_chave_composta"])
    mascara_novos = ~df_novo["_chave_composta"].isin(chaves_existentes)
    df_novos_registros = df_novo[mascara_novos]
    qtd_novos = len(df_novos_registros)

    # Concatena novos registros com a base histórica
    df_atualizado = pd.concat(
        [base_historica, df_novos_registros], ignore_index=True
    )

    # Remove coluna auxiliar
    df_atualizado = df_atualizado.drop(columns=["_chave_composta"])

    salvar_base_historica(df_atualizado, nome_planilha)

    return df_atualizado, qtd_novos
