import pandas as pd

def processar_e_consolidar(lista_dfs):
    """Une as bases, realiza cálculos e limpa os dados."""
    if not lista_dfs:
        return pd.DataFrame()

    # 1. Consolidação (Exemplo: Empilhar todas as tabelas)
    df_final = pd.concat(lista_dfs, ignore_index=True)
    
    # 2. Limpeza (Remover duplicados baseados no ID do Pedido)
    if 'id_pedido' in df_final.columns:
        df_final = df_final.drop_duplicates(subset=['id_pedido'])

    # 3. Exemplo de Cálculo (Margem ou Status)
    # df_final['data_processamento'] = pd.Timestamp.now()
    
    return df_final
