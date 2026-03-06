import streamlit as st
import time
import pandas as pd
from src import extract, transform, load
from config import PLANILHAS_GOOGLE

# Configuração da Página
st.set_page_config(page_title="Data Sync | KaBuM!", page_icon="🧡", layout="wide")

# Interface Principal
st.title("🚀 Consolidador Automático de Pedidos")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://logodownload.org/wp-content/uploads/2017/11/kabum-logo.png", width=150)
    st.title("Painel de Controle")
    st.info("Utilize esta interface para processar as bases e enviar os dados para o WebApp.")
    st.write("---")
    st.write("👤 **Autor:** Daniel Alves")
    st.write("⛱️ **Status:** Modo Férias Ativo")

# Botão de Execução
if st.button("🔄 Iniciar Processamento das Bases"):

    progresso = st.progress(0)
    status = st.empty()
    detalhes = st.expander("Logs de Processamento", expanded=True)

    try:
        # ETAPA 1: EXTRAÇÃO (Google Sheets via Export CSV)
        status.info("📥 Passo 1/3: Extraindo dados do Google Sheets...")
        lista_bases = []
        total = len(PLANILHAS_GOOGLE)

        for i, planilha in enumerate(PLANILHAS_GOOGLE):
            detalhes.write(f"Lendo planilha: **{planilha['nome']}**...")
            df = extract.extrair_google_sheets(planilha)
            lista_bases.append(df)
            detalhes.write(f"✔️ {planilha['nome']}: **{len(df)}** registros lidos.")
            time.sleep(0.3)
        progresso.progress(33)

        # ETAPA 2: TRANSFORMAÇÃO
        status.info("⚙️ Passo 2/3: Consolidando e processando cálculos...")
        df_final = transform.processar_e_consolidar(lista_bases)
        detalhes.success(f"Consolidação concluída! {len(df_final)} registros encontrados.")
        st.write("### Pré-visualização dos Dados Consolidados")
        st.dataframe(df_final.head(10), use_container_width=True)
        progresso.progress(66)

        # ETAPA 3: CARGA
        status.info("📤 Passo 3/3: Criando backup e enviando para o WebApp...")
        dados_json, nome_arquivo = load.gerar_backup_local(df_final)
        detalhes.write(f"Arquivo de backup criado: `{nome_arquivo}`")

        codigo_http, resposta_txt = load.enviar_webapp(dados_json)

        if codigo_http == 200:
            progresso.progress(100)
            status.success("✅ Processo finalizado com sucesso!")
            st.balloons()
            st.success(f"O WebApp recebeu os dados. Resposta: {resposta_txt}")
        else:
            st.error(f"❌ Falha no envio para o WebApp. Erro HTTP: {codigo_http}")
            st.code(resposta_txt)

    except Exception as e:
        st.error(f"🚨 Erro Crítico: {str(e)}")
        status.error("O processamento foi interrompido.")

else:
    st.write("Clique no botão acima para iniciar a rotina de dados.")
