import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard de Despesas", layout="wide")

st.title("💰 Dashboard de Despesas – 2024 x 2025")
st.markdown("---")

# ---------------------------------------------------------
# 🔹 1. Carregar planilha automaticamente do diretório /pages
# ---------------------------------------------------------

FILE_PATH = "./despesas_2024_2025.xlsx"

if not os.path.exists(FILE_PATH):
    st.error(f"❌ Arquivo não encontrado: {FILE_PATH}")
    st.stop()

df = pd.read_excel(FILE_PATH)

# ---------------------------------------------------------
# 🔹 2. Padronização das colunas
# ---------------------------------------------------------

df.columns = df.columns.str.upper().str.replace(" ", "_")

df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype(int)
df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

# ---------------------------------------------------------
# 🔹 3. Cálculos principais para os cards
# ---------------------------------------------------------

total_2024 = df[df["ANO"] == 2024]["VALOR"].sum()
total_2025 = df[df["ANO"] == 2025]["VALOR"].sum()

media_2024 = df[df["ANO"] == 2024]["VALOR"].mean()
media_2025 = df[df["ANO"] == 2025]["VALOR"].mean()

# Diferença percentual entre anos
if total_2024 > 0:
    dif_percentual = ((total_2025 - total_2024) / total_2024) * 100
else:
    dif_percentual = 0

# ---------------------------------------------------------
# 🔹 4. Exibir cards (MODELO A)
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("💸 Total 2024", f"R$ {total_2024:,.0f}".replace(",", "."))
col2.metric("💸 Total 2025", f"R$ {total_2025:,.0f}".replace(",", "."))
col3.metric("📉 Diferença % (25 vs 24)", f"{dif_percentual:.1f}%")
col4.metric("📊 Média Mensal", f"R$ {(df['VALOR'].mean()):,.0f}".replace(",", "."))

st.markdown("---")

# ---------------------------------------------------------
# 🔹 5. Gráfico de barras por categoria (RAIZ PRINCIPAL)
# ---------------------------------------------------------

st.subheader("🏷️ Despesas por Categoria (RAIZ PRINCIPAL)")

g1 = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().reset_index()

fig1 = px.bar(
    g1,
    x="VALOR",
    y="RAIZ_PRINCIPAL",
    orientation="h",
    text=g1["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
    color="VALOR",
    color_continuous_scale="Blues",
)

fig1.update_traces(textposition="outside", textfont_size=14)
fig1.update_layout(height=500, xaxis_title="Valor (R$)", yaxis_title="Categoria")

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 🔹 6. Top 10 Fornecedores por Gastos
# ---------------------------------------------------------

st.subheader("🏆 Top 10 Fornecedores por Gasto")

top_forn = (
    df.groupby("EMPRESA/PESSOA")["VALOR"]
    .sum()
    .reset_index()
    .sort_values(by="VALOR", ascending=False)
    .head(10)
)

top_forn["VALOR_FORMATADO"] = top_forn["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

st.dataframe(
    top_forn[["EMPRESA/PESSOA", "VALOR_FORMATADO"]],
    hide_index=True
)

st.markdown("---")

# ---------------------------------------------------------
# --- RESUMO MENSAL POR ANO ---

resumo = df.pivot_table(
    index="MES",
    columns="ANO",
    values="VALOR",
    aggfunc="sum"
).reset_index()

# Ordenar meses corretamente
ordem_meses = [
    "01 - JANEIRO", "02 - FEVEREIRO", "03 - MARÇO", "04 - ABRIL",
    "05 - MAIO", "06 - JUNHO", "07 - JULHO", "08 - AGOSTO",
    "09 - SETEMBRO", "10 - OUTUBRO", "11 - NOVEMBRO", "12 - DEZEMBRO"
]
resumo["MES"] = pd.Categorical(resumo["MES"], categories=ordem_meses, ordered=True)
resumo = resumo.sort_values("MES")

# Criar novas colunas
resumo["DIFERENÇA (R$)"] = resumo[2025] - resumo[2024]
resumo["VARIAÇÃO (%)"] = (resumo["DIFERENÇA (R$)"] / resumo[2024]) * 100

# Formatação para exibição
resumo_formatado = resumo.copy()
for col in [2024, 2025, "DIFERENÇA (R$)"]:
    resumo_formatado[col] = resumo_formatado[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

resumo_formatado["VARIAÇÃO (%)"] = resumo["VARIAÇÃO (%)"].apply(lambda x: f"{x:.1f}%")

st.markdown("### 📊 Resumo Mensal por Ano")
st.dataframe(resumo_formatado, use_container_width=True)
