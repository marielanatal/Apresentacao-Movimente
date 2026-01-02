import streamlit as st
import pandas as pd

def render():

    st.header("📊 Faturamento")

    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df.columns = df.columns.str.strip()

    df["Ano"] = df["Ano"].astype(int)

    resumo = df.groupby("Ano")["Faturamento - Valor"].sum()

    st.metric("Faturamento 2024", f"R$ {resumo[2024]:,.0f}".replace(",", "."))
    st.metric("Faturamento 2025", f"R$ {resumo[2025]:,.0f}".replace(",", "."))
