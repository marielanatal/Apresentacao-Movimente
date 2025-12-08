import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================
st.set_page_config(layout="wide")
st.title("💸 Dashboard Estratégico de Despesas – 2024 x 2025")

FILE = "despesas_2024_2025.xlsx"

# ==============================
# 1. CARREGAR A PLANILHA
# ==============================
try:
    df = pd.read_excel(FILE)
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo `{FILE}`: {e}")
    st.stop()

# Padronizar nomes das colunas
df.columns = [c.strip().upper() for c in df.columns]

# Validar colunas obrigatórias
for col in ["MÊS", "ANO", "VALOR", "RAIZ_PRINCIPAL", "NATUREZA", "EMPRESA/PESSOA"]:
    if col not in df.columns:
        st.error(f"❌ A coluna obrigatória '{col}' não existe na planilha.")
        st.stop()

# Converter tipos
df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype(int)
df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
df["MÊS"] = df["MÊS"].astype(str)

# Criar coluna NUMérica do mês
df["MES_NUM"] = df["MÊS"].str[:2].astype(int)

# ==============================
# 2. KPIs ESTRATÉGICOS
# ==============================
col1, col2, col3, col4 = st.columns(4)

total_2024 = df[df["ANO"] == 2024]["VALOR"].sum()
total_2025 = df[df["ANO"] == 2025]["VALOR"].sum()

var_percentual = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else 0

media_mensal_24 = total_2024 / 12
media_mensal_25 = total_2025 / 12

col1.metric("💰 Total 2024", f"R$ {total_2024:,.0f}".replace(",", "."))
col2.metric("💰 Total 2025", f"R$ {total_2025:,.0f}".replace(",", "."), f"{var_percentual:.1f}%")
col3.metric("📆 Média Mensal 2024", f"R$ {media_mensal_24:,.0f}".replace(",", "."))
col4.metric("📆 Média Mensal 2025", f"R$ {media_mensal_25:,.0f}".replace(",", "."))

st.markdown("---")

# ==============================
# 3. GRÁFICO MENSAL LADO A LADO
# ==============================
st.subheader("📊 Comparativo Mensal – 2024 x 2025")

df_group = df.groupby(["MÊS", "MES_NUM", "ANO"], as_index=False)["VALOR"].sum()
df_group = df_group.sort_values(["MES_NUM", "ANO"])

fig = px.bar(
    df_group,
    x="MÊS",
    y="VALOR",
    color="ANO",
    barmode="group",
    text=df_group["VALOR"].apply(lambda x: f"{x/1000:.1f}K" if x < 1_000_000 else f"{x/1_000_000:.1f}M"),
    color_discrete_map={2024: "#FF8C00", 2025: "#005BBB"}
)

fig.update_traces(
    textposition="outside",
    textfont_size=18,
    cliponaxis=False
)

fig.update_layout(
    yaxis_title="Despesas (R$)",
    height=600,
    bargap=0.25,
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==============================
# 4. ANÁLISE POR RAIZ PRINCIPAL
# ==============================
st.subheader("🏷️ Despesas por Categoria (RAIZ_PRINCIPAL)")

raiz_group = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().sort_values(ascending=False)

fig2 = px.bar(
    raiz_group,
    orientation="h",
    text=raiz_group.apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
    color=raiz_group,
    color_continuous_scale="Blues"
)

fig2.update_traces(textposition="outside", textfont_size=16)
fig2.update_layout(height=550)

st.plotly_chart(fig2, use_container_width=True)

# Insight automático
pct_top1 = raiz_group.iloc[0] / raiz_group.sum() * 100
st.info(f"🔍 Insight: A categoria **{raiz_group.index[0]}** representa **{pct_top1:.1f}%** de todas as despesas.")

st.markdown("---")

# ==============================
# 5. RANKING DE FORNECEDORES
# ==============================
st.subheader("🏆 Top 10 Fornecedores por Gasto")

top_forn = (
    df.groupby("EMPRESA/PESSOA")["VALOR"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(top_forn.reset_index().style.format({"VALOR": "R$ {:,.2f}".replace(",", ".")}))

st.markdown("---")

# ==============================
# 6. TABELA CONSOLIDADA FINAL
# ==============================
st.subheader("📄 Tabela Consolidada – Mês x Ano")

tabela = df.pivot_table(
    index="MÊS",
    columns="ANO",
    values="VALOR",
    aggfunc="sum",
    fill_value=0
).reset_index()

tabela = tabela.sort_values("MÊS")

# Formatando tabela
for col in tabela.columns[1:]:
    tabela[col] = tabela[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

st.dataframe(tabela, use_container_width=True)

