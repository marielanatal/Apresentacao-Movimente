import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

# ============================================================
# 1) UPLOAD MANUAL OU LEITURA AUTOMÁTICA
# ============================================================

ARQUIVO_PADRAO = "Consolidado de Faturamento - 2024 e 2025.xlsx"

uploaded_file = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])

def carregar_planilha():
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)

    if os.path.exists(ARQUIVO_PADRAO):
        st.success(f"📁 Carregando arquivo padrão: {ARQUIVO_PADRAO}")
        return pd.read_excel(ARQUIVO_PADRAO)

    st.warning("Envie uma planilha Excel para visualizar o dashboard.")
    return None


df = carregar_planilha()

if df is not None:

    # ============================================================
    # 2) TRATAMENTOS
    # ============================================================

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype(int)
    df["Faturamento - Valor"] = pd.to_numeric(df["Faturamento - Valor"], errors="coerce")
    df["Meta"] = pd.to_numeric(df["Meta"], errors="coerce")
    df["Mes_Num"] = df["Mês"].str[:2].astype(int)

    # 🔥 AQUI A MÁGICA: faturamento único por mês
    df_fat_unico = df.sort_values("Mes_Num").drop_duplicates(
        subset=["Mes_Num", "Ano"],
        keep="first"
    )

    # Função para encurtar número
    def format_short(num):
        if pd.isna(num):
            return "-"
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"


    # ============================================================
    # 3) CARDS POR ANO
    # ============================================================

    st.subheader("📌 Resumo por Ano")
    col1, col2 = st.columns(2)

    for ano, col in zip([2024, 2025], [col1, col2]):
        dados_ano = df_fat_unico[df_fat_unico["Ano"] == ano]

        fat_total = dados_ano["Faturamento - Valor"].sum()
        meta_total = dados_ano["Meta"].sum()
        ating = (fat_total / meta_total * 100) if meta_total > 0 else 0

        col.metric(
            label=f"Ano {ano}",
            value=f"Faturamento: R$ {fat_total:,.0f}".replace(",", "."),
            delta=f"{ating:.1f}% da Meta (Meta: R$ {meta_total:,.0f})".replace(",", ".")
        )


    # ============================================================
    # 4) GRÁFICO DE COLUNAS COMPAR
