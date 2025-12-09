import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    # =============================
    # 1) CARREGAR PLANILHA AUTOMATICAMENTE DO REPOSITÓRIO
    # =============================
    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")

    # Padronizar colunas
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(int)

    # =============================
    # 2) RESUMO POR ANO
    # =============================
    resumo = df.groupby("Ano")["Faturamento - Valor"].sum().reset_index()

    fat_2024 = resumo.loc[resumo["Ano"] == 2024, "Faturamento - Valor"].values[0]
    fat_2025 = resumo.loc[resumo["Ano"] == 2025, "Faturamento - Valor"].values[0]

    col1, col2 = st.columns(2)

    col1.metric("Ano 2024", f"R$ {fat_2024:,.0f}".replace(",", "."))
    col2.metric("Ano 2025", f"R$ {fat_2025:,.0f}".replace(",", "."))

    # =============================
    # 3) COMPARATIVO MENSAL
    # =============================
    df["Mês_num"] = df["Mês"].str[:2].astype(int)

    tabela_mensal = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()

    fig = px.bar(
        tabela_mensal,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",
        text_auto=".1s",
        title="Comparativo Mensal"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # 4) TABELA COMPARATIVA FINAL
    # =============================

    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    # Ordenar meses
    tabela = tabela.sort_values("Mês")

    # Criar diferenças
    tabela["Diferença (R$)"] = tabela[2025] - tabela[2024]
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela[2024]) * 100

    # Formatação
    tabela_fmt = tabela.copy()
    tabela_fmt[2024] = tabela_fmt[2024].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt[2025] = tabela_fmt[2025].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (R$)"] = tabela_fmt["Diferença (R$)"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (%)"] = tabela_fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela_fmt, use_container_width=True)
