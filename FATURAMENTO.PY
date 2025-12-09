import streamlit as st
import pandas as pd
import plotly.express as px
import os

def render():
    st.title("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    uploaded_file = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])
    ARQUIVO_PADRAO = "Consolidado de Faturamento - 2024 e 2025.xlsx"

    def carregar():
        if uploaded_file:
            return pd.read_excel(uploaded_file)
        if os.path.exists(ARQUIVO_PADRAO):
            return pd.read_excel(ARQUIVO_PADRAO)
        return None

    df = carregar()

    if df is None:
        st.warning("Envie ou carregue o arquivo padrão.")
        return

    df["Ano"] = df["Ano"].astype(int)
    df["Mes_Num"] = df["Mês"].str[:2].astype(int)
    df["Faturamento - Valor"] = pd.to_numeric(df["Faturamento - Valor"], errors="coerce")
    df["Meta"] = pd.to_numeric(df["Meta"], errors="coerce")

    def fmt(v):
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000: return f"{v/1_000:.1f}K"
        return str(v)

    st.subheader("Resumo por Ano")
    col1, col2 = st.columns(2)

    for ano, coluna in zip([2024, 2025], [col1, col2]):
        dados = df[df["Ano"] == ano]
        fat = dados["Faturamento - Valor"].sum()
        meta = dados["Meta"].sum()
        perc = (fat/meta*100) if meta>0 else 0

        coluna.metric(
            f"Ano {ano}",
            f"R$ {fat:,.0f}".replace(",", "."),
            f"{perc:.1f}% da Meta"
        )

    df_plot = df.groupby(["Mês","Mes_Num","Ano"])["Faturamento - Valor"].sum().reset_index()
    df_plot["Valor_fmt"] = df_plot["Faturamento - Valor"].apply(fmt)
    df_plot["Ano"] = df_plot["Ano"].astype(str)

    st.subheader("📊 Comparativo Mensal")
    fig = px.bar(
        df_plot,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",
        text="Valor_fmt"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Tabela Comparativa")
    tabela = df.pivot_table(index="Mês", columns="Ano",
                            values="Faturamento - Valor", aggfunc="sum").reset_index()
    st.dataframe(tabela, use_container_width=True)
