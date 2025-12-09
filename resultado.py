import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ======================================
# FUNÇÃO DE FORMATAÇÃO
# ======================================

def format_currency(valor):
    return f"R$ {valor:,.0f}".replace(",", ".") if pd.notnull(valor) else "R$ 0"

def format_percent(valor):
    return f"{valor:.1f}%" if pd.notnull(valor) else "0%"

def format_metric(value):
    """Cor verde quando positivo, vermelho quando negativo."""
    if pd.isna(value):
        return "-"
    color = "green" if value >= 0 else "red"
    prefix = "+" if value >= 0 else ""
    return f"<span style='color:{color}; font-weight:bold;'>{prefix}{value:.1f}%</span>"

# ======================================
# CARREGAR PLANILHAS
# ======================================

fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
desp = pd.read_excel("despesas_2024_2025.xlsx")

# Normalizar nomes
fat.columns = fat.columns.str.upper()
desp.columns = desp.columns.str.upper()

# ======================================
# AJUSTE DO FATURAMENTO
# ======================================

fat["MÊS"] = fat["MÊS"].astype(str).str.zfill(2)
fat["MES_ANO"] = fat["MÊS"] + "-" + fat["ANO"].astype(str)

fat_group = fat.groupby(["MÊS", "ANO"]).agg({
    "FATURAMENTO - VALOR": "sum"
}).reset_index()

fat_pivot = fat_group.pivot(index="MÊS", columns="ANO", values="FATURAMENTO - VALOR").fillna(0)
fat_pivot.columns = [f"Fat {col}" for col in fat_pivot.columns]

# ======================================
# AJUSTE DAS DESPESAS
# ======================================

desp["MÊS"] = desp["MÊS"].astype(str).str[:2]  # pegar "01", "02", etc.
desp_group = desp.groupby(["MÊS", "ANO"])["VALOR"].sum().reset_index()

desp_pivot = desp_group.pivot(index="MÊS", columns="ANO", values="VALOR").fillna(0)
desp_pivot.columns = [f"Desp {col}" for col in desp_pivot.columns]

# ======================================
# JUNÇÃO FAT + DESP
# ======================================

tabela = fat_pivot.join(desp_pivot, how="outer").fillna(0)

# Ordenar meses corretamente
tabela = tabela.sort_index()

# Adicionar nomes dos meses
map_meses = {
    "01": "01 - Janeiro", "02": "02 - Fevereiro", "03": "03 - Março",
    "04": "04 - Abril", "05": "05 - Maio", "06": "06 - Junho",
    "07": "07 - Julho", "08": "08 - Agosto", "09": "09 - Setembro",
    "10": "10 - Outubro", "11": "11 - Novembro", "12": "12 - Dezembro"
}
tabela["Mês"] = tabela.index.map(map_meses)

# ======================================
# CÁLCULOS DE RESULTADO E MARGEM
# ======================================

tabela["Resultado 2024"] = tabela["Fat 2024"] - tabela["Desp 2024"]
tabela["Resultado 2025"] = tabela["Fat 2025"] - tabela["Desp 2025"]

tabela["Margem 2024"] = (tabela["Resultado 2024"] / tabela["Fat 2024"].replace(0, pd.NA)) * 100
tabela["Margem 2025"] = (tabela["Resultado 2025"] / tabela["Fat 2025"].replace(0, pd.NA)) * 100

# ======================================
# EXIBIÇÃO PRINCIPAL
# ======================================

st.title("📊 Resultado Mensal – Receita, Despesa, Margem e Lucro")

st.write("Comparação direta mês a mês entre 2024 e 2025.")

# Organizar visualmente
tabela_out = tabela.copy()
tabela_out = tabela_out[[
    "Mês",
    "Fat 2024", "Fat 2025",
    "Desp 2024", "Desp 2025",
    "Resultado 2024", "Resultado 2025",
    "Margem 2024", "Margem 2025",
]]

# Formatando
tabela_out["Fat 2024"] = tabela_out["Fat 2024"].apply(format_currency)
tabela_out["Fat 2025"] = tabela_out["Fat 2025"].apply(format_currency)
tabela_out["Desp 2024"] = tabela_out["Desp 2024"].apply(format_currency)
tabela_out["Desp 2025"] = tabela_out["Desp 2025"].apply(format_currency)
tabela_out["Resultado 2024"] = tabela_out["Resultado 2024"].apply(format_currency)
tabela_out["Resultado 2025"] = tabela_out["Resultado 2025"].apply(format_currency)
tabela_out["Margem 2024"] = tabela_out["Margem 2024"].apply(format_percent)
tabela_out["Margem 2025"] = tabela_out["Margem 2025"].apply(format_percent)

st.dataframe(tabela_out, hide_index=True, use_container_width=True)

# ======================================
# KPIs ANUAIS
# ======================================

fat_total_2024 = tabela["Fat 2024"].sum()
fat_total_2025 = tabela["Fat 2025"].sum()
desp_total_2024 = tabela["Desp 2024"].sum()
desp_total_2025 = tabela["Desp 2025"].sum()

lucro_2024 = fat_total_2024 - desp_total_2024
lucro_2025 = fat_total_2025 - desp_total_2025

margem_2024 = (lucro_2024 / fat_total_2024) * 100
margem_2025 = (lucro_2025 / fat_total_2025) * 100

fat_yoy_pct = ((fat_total_2025 - fat_total_2024) / fat_total_2024) * 100
desp_yoy_pct = ((desp_total_2025 - desp_total_2024) / desp_total_2024) * 100
margem_yoy = margem_2025 - margem_2024

st.markdown("## 📌 Indicadores Gerais (Ano)")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Faturamento Total 2024", format_currency(fat_total_2024))
c1.metric("Faturamento Total 2025", format_currency(fat_total_2025), f"{fat_yoy_pct:.1f}%")

c2.metric("Despesas 2024", format_currency(desp_total_2024))
c2.metric("Despesas 2025", format_currency(desp_total_2025), f"{desp_yoy_pct:.1f}%")

c3.metric("Lucro 2024", format_currency(lucro_2024))
c3.metric("Lucro 2025", format_currency(lucro_2025), format_currency(lucro_2025 - lucro_2024))

c4.markdown(
    f"""
    <div style="font-size:18px; font-weight:600;">Margem Total 2025</div>
    <div style="font-size:26px; font-weight:700;">{margem_2025:.1f}%</div>
    <div>{format_metric(margem_yoy)}</div>
    """,
    unsafe_allow_html=True
)

# ======================================
# KPIs POR TRIMESTRE
# ======================================

st.markdown("## 📌 Indicadores por Trimestre")

tabela["Trimestre"] = ((tabela.index.to_series().astype(int) - 1) // 3) + 1

resumo_trim = tabela.groupby("Trimestre").agg({
    "Fat 2024": "sum",
    "Fat 2025": "sum",
    "Desp 2024": "sum",
    "Desp 2025": "sum"
}).reset_index()

resumo_trim["Lucro 2024"] = resumo_trim["Fat 2024"] - resumo_trim["Desp 2024"]
resumo_trim["Lucro 2025"] = resumo_trim["Fat 2025"] - resumo_trim["Desp 2025"]
resumo_trim["Margem 2024"] = (resumo_trim["Lucro 2024"] / resumo_trim["Fat 2024"]) * 100
resumo_trim["Margem 2025"] = (resumo_trim["Lucro 2025"] / resumo_trim["Fat 2025"]) * 100

resumo_trim["Var Fat %"] = ((resumo_trim["Fat 2025"] - resumo_trim["Fat 2024"]) / resumo_trim["Fat 2024"]) * 100
resumo_trim["Var Desp %"] = ((resumo_trim["Desp 2025"] - resumo_trim["Desp 2024"]) / resumo_trim["Desp 2024"]) * 100
resumo_trim["Var Margem %"] = resumo_trim["Margem 2025"] - resumo_trim["Margem 2024"]

for _, row in resumo_trim.iterrows():
    tri = int(row["Trimestre"])
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(f"Faturamento T{tri} 2025", format_currency(row["Fat 2025"]), f"{row['Var Fat %']:.1f}%")
    c2.metric(f"Despesas T{tri} 2025", format_currency(row["Desp 2025"]), f"{row['Var Desp %']:.1f}%")
    c3.metric(f"Lucro T{tri} 2025", format_currency(row["Lucro 2025"]))
    c4.markdown(
        f"""
        <div style='font-size:16px; font-weight:600;'>Margem T{tri} 2025</div>
        <div style='font-size:22px; font-weight:700;'>{row['Margem 2025']:.1f}%</div>
        <div>{format_metric(row['Var Margem %'])}</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")




