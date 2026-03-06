import pandas as pd
import shutil
import re
from pathlib import Path
from datetime import datetime
from config import RAW_DIR, HISTORICO_DIR, BACKUP_DIR


def _sanitizar_nome(nome):
    """Remove caracteres especiais e substitui espaços por underscore."""
    nome = re.sub(r'[^\w\s-]', '', nome)
    nome = re.sub(r'\s+', '_', nome)
    return nome.strip('_')


def _caminho_historico(nome_planilha):
    """Retorna o caminho do arquivo histórico para uma planilha."""
    nome_arquivo = _sanitizar_nome(nome_planilha) + ".csv"
    return HISTORICO_DIR / nome_arquivo


def carregar_base_historica(nome_planilha):
    """
    Carrega a base histórica de uma planilha.
    Retorna DataFrame vazio se não existir.
    """
    caminho = _caminho_historico(nome_planilha)
    if not caminho.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(caminho, encoding="utf-8", dtype=str)
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding="latin-1", dtype=str)
        return df


def salvar_base_historica(df, nome_planilha):
    """
    Salva a base histórica atualizada.
    Faz backup do arquivo anterior antes de sobrescrever.
    """
    caminho = _caminho_historico(nome_planilha)

    # Backup do arquivo anterior (se existir)
    if caminho.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"{_sanitizar_nome(nome_planilha)}_backup_{timestamp}.csv"
        caminho_backup = BACKUP_DIR / nome_backup
        shutil.copy2(caminho, caminho_backup)

    df.to_csv(caminho, index=False, encoding="utf-8")


def carga_incremental(df_novo, nome_planilha, colunas_chave):
    """
    Compara dados novos com a base histórica e adiciona apenas registros novos.

    Retorna: (df_atualizado, qtd_novos, qtd_total)
    """
    # Validar se as colunas chave existem no DataFrame
    colunas_faltando = [col for col in colunas_chave if col not in df_novo.columns]
    if colunas_faltando:
        raise ValueError(
            f"Colunas chave não encontradas no arquivo: {colunas_faltando}\n"
            f"Colunas disponíveis: {list(df_novo.columns)}"
        )

    # Converter tudo para string para comparação
    df_novo_str = df_novo.copy()
    for col in colunas_chave:
        df_novo_str[col] = df_novo_str[col].astype(str).str.strip()

    # Carregar base histórica
    df_historico = carregar_base_historica(nome_planilha)

    if df_historico.empty:
        # Primeira execução - salva tudo
        salvar_base_historica(df_novo, nome_planilha)
        return df_novo, len(df_novo), len(df_novo)

    # Converter colunas chave do histórico para string
    for col in colunas_chave:
        if col in df_historico.columns:
            df_historico[col] = df_historico[col].astype(str).str.strip()

    # Criar chave composta para comparação
    df_novo_str["_chave_composta"] = df_novo_str[colunas_chave].apply(
        lambda row: "||".join(row.values), axis=1
    )
    df_historico["_chave_composta"] = df_historico[colunas_chave].apply(
        lambda row: "||".join(row.values), axis=1
    )

    # Identificar registros novos
    chaves_existentes = set(df_historico["_chave_composta"])
    mascara_novos = ~df_novo_str["_chave_composta"].isin(chaves_existentes)
    df_novos_registros = df_novo[mascara_novos].copy()

    qtd_novos = len(df_novos_registros)

    if qtd_novos > 0:
        # Remover coluna auxiliar do histórico
        df_historico = df_historico.drop(columns=["_chave_composta"])
        # Concatenar novos registros
        df_atualizado = pd.concat([df_historico, df_novos_registros], ignore_index=True)
        salvar_base_historica(df_atualizado, nome_planilha)
    else:
        df_atualizado = df_historico.drop(columns=["_chave_composta"])

    return df_atualizado, qtd_novos, len(df_atualizado)


def ler_arquivo_upload(arquivo_upload):
    """
    Lê um arquivo CSV ou XLSX do st.file_uploader.
    Aceita ambos os formatos.
    """
    nome = arquivo_upload.name.lower()

    try:
        if nome.endswith(".csv"):
            try:
                df = pd.read_csv(arquivo_upload, encoding="utf-8")
            except UnicodeDecodeError:
                arquivo_upload.seek(0)
                df = pd.read_csv(arquivo_upload, encoding="latin-1")
        elif nome.endswith((".xlsx", ".xls")):
            df = pd.read_excel(arquivo_upload, engine="openpyxl")
        else:
            raise ValueError(f"Formato não suportado: {nome}. Use CSV ou XLSX.")

        if df.empty:
            raise ValueError("O arquivo está vazio.")

        return df
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo '{arquivo_upload.name}': {str(e)}")


def ler_arquivo_rede(planilha_info):
    """
    Lê um arquivo Excel da rede interna.
    Aplica filtros se definidos.
    """
    caminho = Path(planilha_info["caminho"]) / planilha_info["arquivo"]
    aba = planilha_info.get("aba", 0)  # default: primeira aba
    filtros = planilha_info.get("filtros", {})

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado na rede: {caminho}\n"
            f"Verifique se você tem acesso ao caminho de rede."
        )

    try:
        df = pd.read_excel(caminho, sheet_name=aba, engine="openpyxl")
    except Exception as e:
        raise Exception(f"Erro ao ler '{planilha_info['arquivo']}': {str(e)}")

    if df.empty:
        raise ValueError(f"O arquivo '{planilha_info['arquivo']}' está vazio.")

    # Aplicar filtros
    for coluna, valor in filtros.items():
        if coluna in df.columns:
            df = df[df[coluna] == valor].copy()
        else:
            raise ValueError(
                f"Coluna de filtro '{coluna}' não encontrada em '{planilha_info['arquivo']}'.\n"
                f"Colunas disponíveis: {list(df.columns)}"
            )

    if df.empty:
        raise ValueError(
            f"Após aplicar filtros, o arquivo '{planilha_info['arquivo']}' ficou vazio.\n"
            f"Filtros aplicados: {filtros}"
        )

    return df
