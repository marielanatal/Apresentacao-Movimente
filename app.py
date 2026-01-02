raise Exception("ESTE É O APP CORRETO")
import streamlit as st
import faturamento
import despesas
import resultado

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Selecione a página:",
    ["Faturamento", "Despesas", "Resultado"]
)

if pagina == "Faturamento":
    faturamento.render()

elif pagina == "Despesas":
    Despesas.render()

elif pagina == "Resultado":
    resultado.render()




elif pagina == "🧾 Resultado e Margens":
    resultado.render()
