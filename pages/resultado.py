import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render():

    st.title("🧾 Resultado e Margens – Receita x Despesas")
    st.markdown("---")

    # ------------------------------
    # 1. Carregar FATURAMENTO
    # ------------------------------
    fat_path = "Consolidado de Faturamento - 2024 e 2025.xlsx"
    if not os.path.exists(fat_path):
        st.error(f"Arquivo de faturamento não encontrado: {fat_path}")
        return

    df_fat = pd.read_excel(fat_path)
    df_fat["Ano"] = pd.to_numeric(df_fat["Ano"], errors="coerce").astype(int)
    df_fat["Mes_Num"] = df_fat["Mês"].str[:2].astype(int)
    df_fat["Faturamento"] = pd.to_numeric(df_fat["Faturamento - Valor"], errors="coerce")

    fat_mensal = df_fat.groupby(["Ano", "Mês", "Mes_Num"])["Faturamento"].sum().reset_index()

    # ------------------------------
    # 2. Carregar DESPESAS
    # ------------------------------
    desp_path = "despesas_2024_2025.xlsx"
    if not os.path.exists(desp_path):
        st.error(f"Arquivo de despesas não encontrado: {desp_path}")
        return

    df_desp = pd.read_excel(desp_path)
    df_desp.columns = df_desp.columns.str.upper().str.replace(" ", "_")
    df_desp["ANO"] = df_desp["ANO"].astype(int)
    df_desp["VALOR"] = pd.to_numeric(df_desp["VALOR"], errors="coerce")

    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    desp_mensal = df_desp.groupby(["ANO", "MÊS", "MES_NUM"])["VALOR"].sum().reset_index()

    # ------------------------------
    # 3. MERGE – juntar FATURAMENTO + DESPESAS
    # ------------------------------
    base = fat_mensal.merge(
        desp_mensal,
        left_on=["Ano", "Mês", "Mes_Num"],
        right_on=["ANO", "MÊS", "MES_NUM"],
        how="left"
    ).fillna(0)

    # ------------------------------
    # 4. CÁLCULOS
    # ------------------------------
    base["Resultado"] = base["Faturamento"] - base["VALOR"]
    base["Margem (%)"] = (base["Resultado"] / base["Faturamento"]) * 100

    # ------------------------------
    # 5. GRÁFICO – Resultado Mensal
    # ------------------------------
    st.subheader("📉 Resultado Mensal (Lucro ou Prejuízo)")

    fig = px.bar(
        base,
        x="Mês",
        y="Resultado",
        color="Ano",
        barmode="group",
        text=base["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
        color_discrete_map={2024: "#FF8C00", 2025: "#005BBB"}
    )

    fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=18)
    fig.update_layout(height=600, plot_bgcolor="white")

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 6. TABELA COMPLETA
    # ------------------------------
    st.subheader("📄 Tabela Consolidada: Faturamento x Despesas x Margem")

    tabela = base[["Ano", "Mês", "Faturamento", "VALOR", "Resultado", "Margem (%)"]].copy()

    tabela["Faturamento"] = tabela["Faturamento"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["VALOR"] = tabela["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Resultado"] = tabela["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Margem (%)"] = tabela["Margem (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(tabela, use_container_width=True)
