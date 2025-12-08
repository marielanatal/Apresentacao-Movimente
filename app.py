import streamlit as st
import faturamento
import Despesas
import resultado

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# ---------------------------
# MENU LATERAL
# ---------------------------
st.sidebar.title("📌 Navegação")

pagina = st.sidebar.radio(
    "Selecione a página:",
    [
        "📊 Visão de Faturamento",
        "💰 Visão de Despesas",
        "🧾 Resultado e Margens"
    ]
)

# ---------------------------
# CARREGAR A PÁGINA
# ---------------------------
if pagina == "📊 Visão de Faturamento":
    faturamento.render()

elif pagina == "💰 Visão de Despesas":
    Despesas.render()

elif pagina == "🧾 Resultado e Margens":
    resultado.render()

