import streamlit as st
import pandas as pd
import plotly.express as px
import os

def render():
    st.title("💰 Dashboard de Despesas – 2024 x 2025")

    FILE_PATH = "despesas_2024_2025.xlsx"

    if not os.path.exists(FILE_PATH):
        st.error(f"Arquivo não encontrado: {FILE_PATH}")
        return

    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.upper().str.replace(" ", "_")
    df["ANO"] = df["ANO"].astype(int)
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

    total24 = df[df["ANO"]==2024]["VALOR"].sum()
    total25 = df[df["ANO"]==2025]["VALOR"].sum()
    dif = ((total25-total24)/total24*100) if total24>0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total 2024", f"R$ {total24:,.0f}".replace(",","."))
    col2.metric("Total 2025", f"R$ {total25:,.0f}".replace(",","."))
    col3.metric("Diferença %", f"{dif:.1f}%")

    st.subheader("📌 Despesas por Categoria (Raiz Principal)")
    g1 = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().reset_index()
    fig1 = px.bar(g1, x="VALOR", y="RAIZ_PRINCIPAL", orientation="h", text="VALOR")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🏆 Top 10 Fornecedores")
    top = df.groupby("EMPRESA/PESSOA")["VALOR"].sum().reset_index().nlargest(10,"VALOR")
    st.dataframe(top, use_container_width=True)

    st.subheader("📊 Resumo Mensal")
    resumo = df.pivot_table(values="VALOR", index="MÊS", columns="ANO", aggfunc="sum").fillna(0)
    st.dataframe(resumo, use_container_width=True)
