import streamlit as st
import pandas as pd

def render():

    st.header("💰 Despesas")

    df = pd.read_excel("despesas_2024_2025.xlsx")
    df.columns = df.columns.str.upper().str.replace(" ", "_")

    df["ANO"] = df["ANO"].astype(int)

    total_2024 = df[df["ANO"] == 2024]["VALOR"].sum()
    total_2025 = df[df["ANO"] == 2025]["VALOR"].sum()

    st.metric("Despesas 2024", f"R$ {total_2024:,.2f}".replace(",", "."))
    st.metric("Despesas 2025", f"R$ {total_2025:,.2f}".replace(",", "."))


