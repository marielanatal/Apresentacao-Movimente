import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================================================
# 🔹 CARREGAR PLANILHAS AUTOMATICAMENTE
# ============================================================

FILE_FAT = "./Consolidado de Faturamento - 2024 e 2025.xlsx"
FILE_DESP = "./despesas_2024_2025.xlsx"

if not os.path.exists(FILE_FAT):
    st.error(f"❌ Arquivo de faturamento não encontrado: {FILE_FAT}")
    st.stop()

if not os.path.exists(FILE_DESP):
    st.error(f"❌ Arquivo de despesas não encontrado: {FILE_DESP}")
    st.stop()

fat = pd.read_excel(FILE_FAT)
desp = pd.read_excel(FILE_DESP)

# Normalizar nomes de colunas
fat.columns = fat.columns.str.upper().str.replace(" ", "_")
desp.columns = desp.columns.str.upper().str.replace(" ", "_")

# ============================================================
# 🔹 GARANTIR QUE A COLUNA DE MÊS EXISTE E É NUMÉRICA
# ============================================================

possiveis_colunas_mes = ["MÊS", "MES", "MÊS_", "MES_"]
col_mes_fat = None
col_mes_desp = None

for c in possiveis_colunas_mes:
    if c in fat.columns:
        col_mes_fat = c
    if c in desp.columns:
        col_mes_desp = c

if col_mes_fat is None:
    st.error("❌ Planilha de Faturamento não possui coluna de mês válida.")
    st.stop()

if col_mes_desp is None:
    st.error("❌ Planilha de Despesas não possui coluna de mês válida.")
    st.stop()

# Converter "01 - Janeiro" → 1
fat[col_mes_fat] = fat[col_mes_fat].astype(str).str[:2].astype(int)
desp[col_mes_desp] = desp[col_mes_desp].astype(str).str[:2].astype(int)

# ============================================================
# 🔹 TRATAR FATURAMENTO
# ============================================================

fat["FATURAMENTO"] = pd.to_numeric(fat["FATURAMENTO_-_VALOR"], errors="coerce")
fat_resumo = fat.groupby(["ANO", col_mes_fat])["FATURAMENTO"].sum().reset_index()

# ============================================================
# 🔹 TRATAR DESPESAS
# ============================================================

desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")
desp_resumo = desp.groupby(["ANO", col_mes_desp])["VALOR"].sum().reset_index()

# ============================================================
# 🔹 JUNTAR FATURAMENTO + DESPESAS
# ============================================================

tabela = pd.merge(
    fat_resumo,
    desp_resumo,
    left_on=["ANO", col_mes_fat],
    right_on=["ANO", col_mes_desp],
    how="left"
)

tabela.rename(columns={
    "FATURAMENTO": "FAT",
    "VALOR": "DESP"
}, inplace=True)

tabela["DESP"] = tabela["DESP"].fillna(0)

# ============================================================
# 🔹 CALCULAR RESULTADO E MARGEM (%)
# ============================================================

tabela["RESULTADO"] = tabela["FAT"] - tabela["DESP"]
tabela["MARGEM_%"] = (tabela["RESULTADO"] / tabela["FAT"]) * 100

# ============================================================
# 🔹 CRIAR COLUNA DE TRIMESTRE (SEM ERRO)
# ============================================================

tabela["TRIMESTRE"] = ((tabela[col_mes_fat] - 1) // 3) + 1

# ============================================================
# 🔹 INTERFACE VISUAL
# ============================================================

st.title("📊 Resultados Consolidados – Faturamento x Despesas x Margem")

# Mostrar tabela formatada
tabela_show = tabela.copy()
tabela_show["FAT"] = tabela_show["FAT"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tabela_show["DESP"] = tabela_show["DESP"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tabela_show["RESULTADO"] = tabela_show["RESULTADO"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tabela_show["MARGEM_%"] = tabela_show["MARGEM_%"].apply(lambda x: f"{x:.1f}%")

st.dataframe(tabela_show, use_container_width=True)

# ============================================================
# 🔹 GRÁFICO DE MARGEM POR MÊS
# ============================================================

fig_margem = px.line(
    tabela,
    x=col_mes_fat,
    y="MARGEM_%",
    color="ANO",
    markers=True,
    title="📈 Margem Mensal (%) – 2024 x 2025",
    color_discrete_map={2024: "#228B22", 2025: "#006400"}
)

st.plotly_chart(fig_margem, use_container_width=True)

# ============================================================
# 🔹 GRÁFICO DE RESULTADO MENSAL
# ============================================================

fig_res = px.bar(
    tabela,
    x=col_mes_fat,
    y="RESULTADO",
    color="ANO",
    barmode="group",
    title="💰 Resultado (Lucro / Prejuízo) por Mês",
    color_discrete_map={2024: "#FF8C00", 2025: "#1E90FF"}
)

st.plotly_chart(fig_res, use_container_width=True)

# ============================================================
# 🔹 TABELA TRIMESTRAL
# ============================================================

st.subheader("📌 Resultados por Trimestre")

tri = tabela.groupby(["ANO", "TRIMESTRE"]).agg({
    "FAT": "sum",
    "DESP": "sum",
    "RESULTADO": "sum",
    "MARGEM_%": "mean"
}).reset_index()

tri_show = tri.copy()
tri_show["FAT"] = tri_show["FAT"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tri_show["DESP"] = tri_show["DESP"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tri_show["RESULTADO"] = tri_show["RESULTADO"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
tri_show["MARGEM_%"] = tri_show["MARGEM_%"].apply(lambda x: f"{x:.1f}%")

st.dataframe(tri_show, use_container_width=True)
