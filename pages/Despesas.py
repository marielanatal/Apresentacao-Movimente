import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("💸 Dashboard de Despesas – 2024 x 2025")

# Nome do arquivo no GitHub
FILE_NAME = "despesas_2024_2025.xlsx"

# ===============================
# CARREGAR A PLANILHA
# ===============================
try:
    df = pd.read_excel(FILE_NAME)
except:
    st.error(f"❌ Não foi possível carregar o arquivo **{FILE_NAME}**.")
    st.stop()

# ===============================
# AJUSTES DE DADOS
# ===============================
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype(int)
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
df["Mes_Num"] = df["Mês"].str[:2].astype(int)

# ordenar meses
df = df.sort_values(["Mes_Num", "Ano"])

# ===============================
# FILTROS
# ===============================
st.sidebar.header("Filtros")

anos = st.sidebar.multiselect(
    "Selecione os anos:",
    sorted(df["Ano"].unique()),
    default=sorted(df["Ano"].unique())
)

categorias = st.sidebar.multiselect(
    "Categoria:",
    sorted(df["Categoria"].dropna().unique()),
    default=sorted(df["Categoria"].dropna().unique())
)

df_filt = df[df["Ano"].isin(anos) & df["Categoria"].isin(categorias)]

# ===============================
# CARDS DE RESUMO
# ===============================
st.subheader("📌 Resumo por Ano")

col1, col2 = st.columns(2)

for ano, col in zip(sorted(df["Ano"].unique()), [col1, col2]):
    total = df[df["Ano"] == ano]["Valor"].sum()
    col.metric(
        label=f"Total {ano}",
        value=f"R$ {total:,.0f}".replace(",", ".")
    )

st.markdown("---")

# ===============================
# GRÁFICO LADO A LADO
# ===============================
st.subheader("📊 Comparativo Mensal – 2024 x 2025")

df_plot = df.groupby(["Mês", "Mes_Num", "Ano"], as_index=False)["Valor"].sum()

fig = px.bar(
    df_plot,
    x="Mês",
    y="Valor",
    color="Ano",
    barmode="group",
    text=df_plot["Valor"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
    color_discrete_map={
        2024: "#FF8C00",   # Laranja
        2025: "#005BBB",   # Azul
    }
)

fig.update_traces(
    textposition="outside",
    textfont=dict(size=18, color="black"),
    cliponaxis=False
)

fig.update_layout(
    yaxis_title="Despesas (R$)",
    xaxis_title="Mês",
    height=650,
    plot_bgcolor="white",
    bargap=0.25
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===============================
# TABELA FINAL
# ===============================
st.subheader("📄 Tabela Consolidada por Ano")

tabela = df.pivot_table(
    index="Mês",
    columns="Ano",
    values="Valor",
    aggfunc="sum",
    fill_value=0
)

tabela = tabela.applymap(lambda x: f"R$ {x:,.0f}".replace(",", "."))

st.dataframe(tabela, use_container_width=True)
