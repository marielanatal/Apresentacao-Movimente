import streamlit as st
import resultado

st.set_page_config(page_title="Apresentação", layout="wide")

st.title("📌 Visão Geral do Ano")

resultado.render()

