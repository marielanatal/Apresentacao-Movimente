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

    # Padronizar colunas
    df_fat["Ano"] = pd.to_numeric(df_fat["Ano"], errors="coerce")
    df_fat["Faturamento"] = pd.to_numeric(df_fat["Faturamento - Valor"], errors="coerce")
    df_fat["MES"] = df_fat["Mês"]                     # padroniza nome da coluna
    df_fat["MES_NUM"] = df_fat["MES"].str[:2].astype(int)

    # Faturamento mensal por ano
    fat_mensal = df_fat.groupby(["Ano", "MES", "MES_NUM"])["Faturamento"].sum().reset_index()

    # ------------------------------
    # 2. Carregar DESPESAS
    # ------------------------------
    desp_path = "despesas_2024_2025.xlsx"

    if not os.path.exists(desp_path):
        st.error(f"Arquivo de despesas não encontrado: {desp_path}")
        return

    df_desp = pd.read_excel(desp_path)

    # Padronizar nomes
    df_desp.columns = df_desp.columns.str.upper().str.replace(" ", "_")

    df_desp["ANO"] = pd.to_numeric(df_desp["ANO"], errors="coerce")
    df_desp["VALOR"] = pd.to_numeric(df_desp["VALOR"], errors="coerce")

    df_desp["MES"] = df_desp["MÊS"]                   # deixa igual ao faturamento
    df_desp["MES_NUM"] = df_desp["MES"].str[:2].astype(int)

    # Despesas mensais
    desp_mensal = df_desp.groupby(["ANO", "MES", "MES_NUM"])["VALOR"].sum().reset_index()

    # ------------------------------
    # 3. MERGE — juntar faturamento + despesas
    # ------------------------------
    base = fat_mensal.merge(
        desp_mensal,
        left_on=["Ano", "MES", "MES_NUM"],
        right_on=["ANO", "MES", "MES_NUM"],
        how="left"
    ).fillna(0)

    # ------------------------------
    # 4. CÁLCULOS
    # ------------------------------
    base["Resultado"] = base["Faturamento"] - base["VALOR"]

    base["Margem (%)"] = base.apply(
        lambda row: (row["Resultado"] / row["Faturamento"] * 100) if row["Faturamento"] > 0 else 0,
        axis=1
    )

    # ------------------------------
    # 5. GRÁFICO DE RESULTADO MENSAL
    # ------------------------------
    st.subheader("📉 Resultado Mensal (Lucro ou Prejuízo)")

    fig = px.bar(
        base,
        x="MES",
        y="Resultado",
        color="Ano",
        barmode="group",
        text=base["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
        color_discrete_map={
            2024: "#FF8C00",
            2025: "#005BBB"
        }
    )

    fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=18)
    fig.update_layout(height=600, plot_bgcolor="white")

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 6. TABELA RESUMO
    # ------------------------------
    st.subheader("📄 Tabela Consolidada: Faturamento x Despesas x Margem")

    tabela = base[["Ano", "MES", "Faturamento", "VALOR", "Resultado", "Margem (%)"]].copy()

    tabela["Faturamento"] = tabela["Faturamento"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["VALOR"] = tabela["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Resultado"] = tabela["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Margem (%)"] = tabela["Margem (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(tabela, use_container_width=True)
