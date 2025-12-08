import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(page_title="Despesas 2024–2025", layout="wide")

st.title("💰 Dashboard de Despesas – 2024 x 2025")
st.markdown("---")

# ===============================
# UPLOAD DO ARQUIVO
# ===============================
uploaded_file = st.file_uploader("Envie o arquivo de despesas (Excel)", type=["xlsx"])

if uploaded_file is None:
    st.info("📂 Envie o arquivo despesas_2024_2025.xlsx para visualizar o dashboard.")
    st.stop()

# ===============================
# LEITURA DA PLANILHA
# ===============================
df = pd.read_excel(uploaded_file)

# ===============================
# TRATAMENTO DO DATAFRAME
# ===============================

# Ajuste robusto do ano (aceita '2024', '2024 ', 'ANO:2024', etc.)
df["ANO"] = (
    df["ANO"]
    .astype(str)
    .str.extract(r"(\d{4})")  # pega apenas anos com 4 dígitos
    .astype(float)
    .astype("Int64")
)

# Mês como categoria ordenada
ordem_meses = [
    "01 - Janeiro","02 - Fevereiro","03 - Março","04 - Abril","05 - Maio","06 - Junho",
    "07 - Julho","08 - Agosto","09 - Setembro","10 - Outubro","11 - Novembro","12 - Dezembro"
]

df["MÊS"] = pd.Categorical(df["MÊS"], categories=ordem_meses, ordered=True)

# Garantindo que VALOR é numérico
df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

# ===============================
# VISÃO 1 – DESPESAS POR RAIZ PRINCIPAL
# ===============================

st.subheader("📌 Despesas por Categoria (RAIZ_PRINCIPAL)")

df_raiz = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().reset_index()

if df_raiz.empty:
    st.warning("⚠️ Nenhum dado encontrado para RAIZ_PRINCIPAL.")
else:
    fig1 = px.bar(
        df_raiz,
        x="RAIZ_PRINCIPAL",
        y="VALOR",
        title="Gasto Total por Categoria",
        text_auto=".2s",
        color="RAIZ_PRINCIPAL",
    )

    fig1.update_layout(showlegend=False, height=450)
    st.plotly_chart(fig1, use_container_width=True)


# ===============================
# VISÃO 2 – DESPESAS POR MÊS E ANO
# ===============================

st.subheader("📅 Despesas Mensais – Comparativo 2024 x 2025")

df_mes = df.groupby(["ANO", "MÊS"])["VALOR"].sum().reset_index()

fig2 = px.bar(
    df_mes,
    x="MÊS",
    y="VALOR",
    color="ANO",
    barmode="group",
    text_auto=".2s",
    title="Comparativo Mensal",
)

fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)


# ===============================
# VISÃO 3 – TOP 10 FORNECEDORES POR GASTO
# ===============================

st.subheader("🏆 Top 10 Fornecedores por Gasto")

top_forn = (
    df.groupby("EMPRESA/PESSOA")["VALOR"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# Formatação segura para Streamlit
top_forn["VALOR"] = top_forn["VALOR"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", ".")
)

st.dataframe(top_forn, use_container_width=True)


# ===============================
# VISÃO 4 – TABELA COMPLETA FORMATADA
# ===============================

st.subheader("📄 Base Completa")

df_show = df.copy()
df_show["VALOR"] = df_show["VALOR"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))

st.dataframe(df_show, use_container_width=True)

