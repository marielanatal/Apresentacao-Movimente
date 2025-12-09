# =============================
# 8) KPI – INDICADORES GERAIS
# =============================

fat_total_2024 = tabela["Fat 2024"].sum()
fat_total_2025 = tabela["Fat 2025"].sum()
fat_yoy = fat_total_2025 - fat_total_2024
fat_yoy_pct = (fat_yoy / fat_total_2024) * 100

desp_total_2024 = tabela["Desp 2024"].sum()
desp_total_2025 = tabela["Desp 2025"].sum()
desp_yoy = desp_total_2025 - desp_total_2024
desp_yoy_pct = (desp_yoy / desp_total_2024) * 100

lucro_2024 = fat_total_2024 - desp_total_2024
lucro_2025 = fat_total_2025 - desp_total_2025
lucro_yoy = lucro_2025 - lucro_2024

margem_2024 = (lucro_2024 / fat_total_2024) * 100 if fat_total_2024 else 0
margem_2025 = (lucro_2025 / fat_total_2025) * 100 if fat_total_2025 else 0
margem_yoy = margem_2025 - margem_2024

# KPIs no layout de 4 colunas
st.markdown("## 📌 Indicadores Gerais")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Faturamento Total 2025",
    f"R$ {fat_total_2025:,.0f}".replace(",", "."),
    f"{fat_yoy_pct:.1f}%",
)

k2.metric(
    "Despesas Totais 2025",
    f"R$ {desp_total_2025:,.0f}".replace(",", "."),
    f"{desp_yoy_pct:.1f}%",
)

k3.metric(
    "Lucro Total 2025",
    f"R$ {lucro_2025:,.0f}".replace(",", "."),
    f"R$ {lucro_yoy:,.0f}".replace(",", "."),
)

k4.metric(
    "Margem Total 2025",
    f"{margem_2025:.1f}%",
    f"{margem_yoy:.1f}%",
)

st.markdown("---")

