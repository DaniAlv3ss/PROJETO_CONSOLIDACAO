import streamlit as st
import time
import pandas as pd
from src import extract, transform, load
from config import PLANILHAS_ONLINE, PLANILHAS_UPLOAD, HISTORICO_DIR

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
    st.write("---")

    # Informações sobre bases históricas
    st.write("📁 **Bases Históricas**")
    arquivos_historico = sorted(HISTORICO_DIR.glob("*.csv"))
    if arquivos_historico:
        for arq in arquivos_historico:
            tamanho_kb = arq.stat().st_size / 1024
            data_mod = pd.Timestamp(arq.stat().st_mtime, unit="s").strftime("%d/%m/%Y %H:%M")
            st.caption(f"📄 `{arq.name}`\n{tamanho_kb:.1f} KB · {data_mod}")
    else:
        st.caption("Nenhuma base histórica encontrada.")

# ─── ETAPA 1: Uploads obrigatórios ───────────────────────────────────────────
st.subheader("📤 ETAPA 1: Upload das planilhas")

uploads = {}
for planilha in PLANILHAS_UPLOAD:
    arquivo = st.file_uploader(
        f"📤 Upload CSV: {planilha['nome']}",
        type=["csv"],
        key=f"upload_{planilha['nome']}",
    )
    uploads[planilha["nome"]] = arquivo

st.markdown("---")

# ─── Botão de Execução ────────────────────────────────────────────────────────
if st.button("🔄 Iniciar Processamento"):

    # Verifica se todos os uploads obrigatórios foram feitos
    uploads_faltando = [p["nome"] for p in PLANILHAS_UPLOAD if uploads.get(p["nome"]) is None]
    if uploads_faltando:
        for nome_faltando in uploads_faltando:
            st.warning(f"⚠️ Por favor, faça o upload do CSV: **{nome_faltando}**")
        st.stop()

    progresso = st.progress(0)
    status = st.empty()
    detalhes = st.expander("Logs de Processamento", expanded=True)

    try:
        lista_bases = []

        # ── ETAPA 1 – EXTRAÇÃO ────────────────────────────────────────────────
        status.info("📥 Passo 1/3: Extraindo dados...")

        # 1a. Planilhas de upload manual
        for planilha in PLANILHAS_UPLOAD:
            nome = planilha["nome"]
            arquivo = uploads[nome]
            detalhes.write(f"Lendo CSV enviado: **{nome}**...")
            try:
                df = pd.read_csv(arquivo, encoding="utf-8")
            except UnicodeDecodeError:
                arquivo.seek(0)
                df = pd.read_csv(arquivo, encoding="latin-1")
            detalhes.write(f"✔️ {nome}: **{len(df)}** registros lidos do upload.")
            lista_bases.append((planilha, df))

        # 1b. Planilhas online
        for planilha in PLANILHAS_ONLINE:
            nome = planilha["nome"]
            detalhes.write(f"Lendo planilha online: **{nome}**...")
            df = extract.extrair_google_sheets(planilha)
            detalhes.write(f"✔️ {nome}: **{len(df)}** registros lidos.")
            lista_bases.append((planilha, df))
            time.sleep(0.3)

        progresso.progress(33)

        # ── ETAPA 1.5 – CARGA INCREMENTAL ────────────────────────────────────
        status.info("🔄 Passo 1.5/3: Aplicando carga incremental...")
        dfs_para_consolidar = []

        for planilha, df in lista_bases:
            nome = planilha["nome"]
            chave_unica = planilha.get("chave_unica", [])

            if chave_unica:
                df_atualizado, qtd_novos = extract.carga_incremental(
                    df, nome, chave_unica
                )
                detalhes.write(
                    f"📊 {nome}: **{qtd_novos}** registros novos adicionados "
                    f"(base total: **{len(df_atualizado)}** registros)"
                )
                dfs_para_consolidar.append(df_atualizado)
            else:
                detalhes.write(f"📋 {nome}: usando dados como vieram ({len(df)} registros).")
                dfs_para_consolidar.append(df)

        progresso.progress(50)

        # ── ETAPA 2 – TRANSFORMAÇÃO ───────────────────────────────────────────
        status.info("⚙️ Passo 2/3: Consolidando e processando cálculos...")
        df_final = transform.processar_e_consolidar(dfs_para_consolidar)
        detalhes.success(f"Consolidação concluída! {len(df_final)} registros encontrados.")
        st.write("### Pré-visualização dos Dados Consolidados")
        st.dataframe(df_final.head(10), use_container_width=True)
        progresso.progress(66)

        # ── ETAPA 3 – CARGA ───────────────────────────────────────────────────
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
    st.write("Faça o upload dos arquivos necessários e clique no botão acima para iniciar a rotina de dados.")

