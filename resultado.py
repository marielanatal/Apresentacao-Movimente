import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📈 Comparativo Faturamento, Despesas e Resultado")

    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_fat["MÊS_NUM"] = df_fat["Mês"].str[:2].astype(int)

    df_desp["ANO"] = df_desp["ANO"].astype(int)
    df_desp["MÊS_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    fat = (
        df_fat.groupby(["Ano", "MÊS_NUM"])["Faturamento - Valor"]
        .sum()
        .reset_index()
        .rename(columns={"Ano": "ANO", "Faturamento - Valor": "FAT"})
    )

    desp = (
        df_desp.groupby(["ANO", "MÊS_NUM"])["VALOR"]
        .sum()
        .reset_index()
        .rename(columns={"VALOR": "DESP"})
    )

    base = fat.merge(desp, on=["ANO", "MÊS_NUM"], how="outer").fillna(0)
    base["RESULT"] = base["FAT"] - base["DESP"]

    df24 = base[base["ANO"] == 2024]
    df25 = base[base["ANO"] == 2025]

    def fmt(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    soma_24 = {
        "FAT": df24["FAT"].sum(),
        "DESP": df24["DESP"].sum(),
        "RES": df24["RESULT"].sum()
    }

    soma_25 = {
        "FAT": df25["FAT"].sum(),
        "DESP": df25["DESP"].sum(),
        "RES": df25["RESULT"].sum()
    }

    st.markdown("## 📌 Visão Geral do Ano")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("2024 - Resultado", fmt(soma_24["RES"]))

    with c2:
        st.metric("2025 - Resultado", fmt(soma_25["RES"]))

    fig = px.line(
        base,
        x="MÊS_NUM",
        y="RESULT",
        color="ANO",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)


