import streamlit as st
import time
import pandas as pd
import os
from datetime import datetime
from src import extract, transform, load
from config import PLANILHAS_UPLOAD, PLANILHAS_REDE, HISTORICO_DIR

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

    # Informações das bases históricas
    st.write("---")
    st.subheader("📁 Bases Históricas")
    if HISTORICO_DIR.exists():
        arquivos = list(HISTORICO_DIR.glob("*.csv"))
        if arquivos:
            for arq in sorted(arquivos):
                tamanho_mb = arq.stat().st_size / (1024 * 1024)
                data_mod = datetime.fromtimestamp(arq.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
                st.caption(f"📄 **{arq.name}**")
                st.caption(f"   {tamanho_mb:.2f} MB | Atualizado: {data_mod}")
        else:
            st.caption("Nenhuma base histórica ainda.")
    else:
        st.caption("Pasta de histórico não encontrada.")

# ============================================================
# ÁREA DE UPLOAD DE ARQUIVOS
# ============================================================
st.subheader("📤 Upload de Planilhas (CSV ou XLSX)")
st.caption("Faça o download das planilhas do Google Sheets e arraste aqui.")

uploads = {}
cols = st.columns(len(PLANILHAS_UPLOAD))
for i, planilha in enumerate(PLANILHAS_UPLOAD):
    with cols[i]:
        arquivo = st.file_uploader(
            f"📄 {planilha['nome']}",
            type=["csv", "xlsx", "xls"],
            key=f"upload_{i}",
        )
        uploads[planilha["nome"]] = arquivo

st.markdown("---")

# ============================================================
# ÁREA DE PLANILHAS DA REDE (automáticas)
# ============================================================
st.subheader("📂 Planilhas da Rede Interna (automático)")
for planilha in PLANILHAS_REDE:
    caminho_completo = os.path.join(planilha["caminho"], planilha["arquivo"])
    existe = os.path.exists(caminho_completo)
    icone = "🟢" if existe else "🔴"
    st.caption(f"{icone} **{planilha['nome']}**: `{planilha['arquivo']}`")

st.markdown("---")

# ============================================================
# BOTÃO DE PROCESSAMENTO
# ============================================================
if st.button("🔄 Iniciar Processamento das Bases", type="primary"):

    # Verificar uploads obrigatórios
    uploads_faltando = [p["nome"] for p in PLANILHAS_UPLOAD if uploads.get(p["nome"]) is None]
    if uploads_faltando:
        st.warning(f"⚠️ Faça o upload das planilhas: {', '.join(uploads_faltando)}")
        st.stop()

    progresso = st.progress(0)
    status = st.empty()
    detalhes = st.expander("📋 Logs de Processamento", expanded=True)

    try:
        lista_bases = []
        total_planilhas = len(PLANILHAS_UPLOAD) + len(PLANILHAS_REDE)
        planilhas_processadas = 0

        # ────────────────────────────────────────────
        # ETAPA 1: LEITURA DOS UPLOADS (CSV/XLSX)
        # ────────────────────────────────────────────
        status.info("📥 Passo 1/4: Lendo arquivos de upload...")

        for planilha in PLANILHAS_UPLOAD:
            nome = planilha["nome"]
            detalhes.write(f"📄 Lendo upload: **{nome}**...")

            arquivo = uploads[nome]
            df = extract.ler_arquivo_upload(arquivo)
            detalhes.write(f"   ✔️ Arquivo lido: **{len(df)}** registros")

            # Carga incremental
            chave = planilha["chave_unica"]
            if chave:
                df_atualizado, qtd_novos, qtd_total = extract.carga_incremental(df, nome, chave)
                detalhes.write(f"   📊 **{qtd_novos}** registros novos adicionados (base total: **{qtd_total}**)")
                lista_bases.append(df_atualizado)
            else:
                lista_bases.append(df)

            planilhas_processadas += 1
            progresso.progress(int(planilhas_processadas / total_planilhas * 25))

        # ────────────────────────────────────────────
        # ETAPA 2: LEITURA DA REDE INTERNA
        # ────────────────────────────────────────────
        status.info("📂 Passo 2/4: Lendo planilhas da rede interna...")

        for planilha in PLANILHAS_REDE:
            nome = planilha["nome"]
            somente_historico = planilha.get("somente_historico", False)

            # Se é somente histórico, verifica se já foi carregado antes
            if somente_historico:
                df_hist = extract.carregar_base_historica(nome)
                if not df_hist.empty:
                    detalhes.write(f"📂 **{nome}**: já carregado anteriormente ({len(df_hist)} registros). Pulando.")
                    lista_bases.append(df_hist)
                    planilhas_processadas += 1
                    progresso.progress(int(planilhas_processadas / total_planilhas * 25))
                    continue

            detalhes.write(f"📂 Lendo da rede: **{nome}**...")

            try:
                df = extract.ler_arquivo_rede(planilha)
                filtros_aplicados = planilha.get("filtros", {})
                filtros_str = ", ".join(f"{k}={v}" for k, v in filtros_aplicados.items()) if filtros_aplicados else "nenhum"
                detalhes.write(f"   ✔️ Arquivo lido: **{len(df)}** registros (filtros aplicados: {filtros_str})")

                # Carga incremental
                chave = planilha.get("chave_unica", [])
                if chave:
                    df_atualizado, qtd_novos, qtd_total = extract.carga_incremental(df, nome, chave)
                    detalhes.write(f"   📊 **{qtd_novos}** registros novos (base total: **{qtd_total}**)")
                    lista_bases.append(df_atualizado)
                else:
                    lista_bases.append(df)

            except FileNotFoundError as e:
                detalhes.warning(f"   ⚠️ {nome}: Arquivo não encontrado na rede. {str(e)}")
                # Tenta carregar do histórico
                df_hist = extract.carregar_base_historica(nome)
                if not df_hist.empty:
                    detalhes.write(f"   📂 Usando base histórica: **{len(df_hist)}** registros")
                    lista_bases.append(df_hist)
                else:
                    detalhes.error(f"   ❌ Sem dados para {nome}. Nenhum histórico encontrado.")

            planilhas_processadas += 1
            progresso.progress(int(planilhas_processadas / total_planilhas * 25))

        progresso.progress(33)

        # ────────────────────────────────────────────
        # ETAPA 3: TRANSFORMAÇÃO
        # ────────────────────────────────────────────
        status.info("⚙️ Passo 3/4: Consolidando e processando dados...")
        df_final = transform.processar_e_consolidar(lista_bases)
        detalhes.success(f"✅ Consolidação concluída! **{len(df_final)}** registros totais.")

        st.write("### 📊 Pré-visualização dos Dados Consolidados")
        st.dataframe(df_final.head(15), use_container_width=True)
        progresso.progress(66)

        # ────────────────────────────────────────────
        # ETAPA 4: CARGA (Backup + WebApp)
        # ────────────────────────────────────────────
        status.info("📤 Passo 4/4: Criando backup e enviando para o WebApp...")
        dados_json, nome_arquivo = load.gerar_backup_local(df_final)
        detalhes.write(f"💾 Backup criado: `{nome_arquivo}`")

        codigo_http, resposta_txt = load.enviar_webapp(dados_json)

        if codigo_http == 200:
            progresso.progress(100)
            status.success("✅ Processo finalizado com sucesso!")
            st.balloons()
            st.success(f"O WebApp recebeu os dados. Resposta: {resposta_txt}")
        else:
            progresso.progress(100)
            st.warning(f"⚠️ Backup local salvo com sucesso! Envio para WebApp falhou (HTTP {codigo_http}).")
            st.code(resposta_txt)

    except Exception as e:
        st.error(f"🚨 Erro Crítico: {str(e)}")
        status.error("O processamento foi interrompido.")

else:
    st.info("👆 Faça o upload dos arquivos e clique no botão para iniciar.")

