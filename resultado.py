import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📈 Resultado Geral – Faturamento x Despesas")

    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_fat["MES"] = df_fat["Mês"].str[:2].astype(int)

    df_desp["ANO"] = df_desp["ANO"].astype(int)
    df_desp["MES"] = df_desp["MÊS"].str[:2].astype(int)

    fat = (
        df_fat.groupby(["Ano", "MES"])["Faturamento - Valor"]
        .sum()
        .reset_index()
        .rename(columns={"Ano": "ANO", "Faturamento - Valor": "FAT"})
    )

    desp = (
        df_desp.groupby(["ANO", "MES"])["VALOR"]
        .sum()
        .reset_index()
        .rename(columns={"VALOR": "DESP"})
    )

    base = fat.merge(desp, on=["ANO", "MES"], how="outer").fillna(0)
    base["RESULTADO"] = base["FAT"] - base["DESP"]

    df24 = base[base["ANO"] == 2024]
    df25 = base[base["ANO"] == 2025]

    def fmt(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    col1, col2 = st.columns(2)

    col1.metric("Resultado 2024", fmt(df24["RESULTADO"].sum()))
    col2.metric("Resultado 2025", fmt(df25["RESULTADO"].sum()))

    fig = px.line(
        base,
        x="MES",
        y="RESULTADO",
        color="ANO",
        markers=True,
        title="Resultado Mensal"
    )

    st.plotly_chart(fig, use_container_width=True)
