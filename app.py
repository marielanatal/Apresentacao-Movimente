import streamlit as st
import resultado
import faturamento
import despesa

st.set_page_config(page_title="Apresentação", layout="wide")

st.title("📌 Visão Geral do Ano")

aba = st.sidebar.radio(
    "Menu",
    ["Resultado", "Faturamento", "Despesas"]
)

if aba == "Resultado":
    resultado.render()

elif aba == "Faturamento":
    faturamento.render()

elif aba == "Despesas":
    despesa.render()
