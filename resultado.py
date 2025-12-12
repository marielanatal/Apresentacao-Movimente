import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # ================================
    # 1) CARREGAR PLANILHAS OFICIAIS
    # ================================
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # Padronizar colunas
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["ANO"] = df_fat["ANO"].astype(int)
    df_desp["ANO"] = df_desp["ANO"].astype(int)

    # Converter valores
    df_fat["FATURAMENTO - VALOR"] = df_fat["FATURAMENTO - VALOR"].astype(float)
    df_desp["VALOR"] = df_desp["VALOR"].astype(float)

    # Criar número do mês
    df_fat["MES_NUM"] = df_fat["MÊS"].str[:2].astype(int)
    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # ================================
    # 2) AGRUPAR POR ANO + MÊS
    # ================================
    fat_group = df_fat.groupby(["ANO", "MES_NUM", "MÊS"])["FATURAMENTO - VALOR"].sum().reset_index()
    desp_group = df_desp.groupby(["ANO", "MES_NUM", "MÊS"])["VALOR"].sum().reset_index()

    # ================================
    # 3) JUNTAR FATURAMENTO E DESPESAS
    # ================================
    base = pd.merge(
        fat_group,
        desp_group,
        on=["ANO", "MES_NUM", "MÊS"],
        how="left"
    )

    base["DESPESAS"] = base["VALOR"].fillna(0)
    base["RESULTADO"] = base["FATURAMENTO - VALOR"] - base["DESPESAS"]

    base = base.sort_values(["ANO", "MES_NUM"])

    # ================================
    # 4) SEPARAR TABELAS POR ANO
    # ================================
    tabela_2024 = base[base["ANO"] == 2024].copy()
    tabela_2025 = base[base["ANO"] == 2025].copy()

    # Criar variação (%)
    tabela_2024["VAR %"] = (tabela_2024["RESULTADO"] / tabela_2024["FATURAMENTO - VALOR"]) * 100
    tabela_2025["VAR %"] = (tabela_2025["RESULTADO"] / tabela_2025["FATURAMENTO - VALOR"]) * 100

    # ================================
    # 5) FORMATAÇÃO
    # ================================
    def format_table(df):
        df_fmt = df.copy()
        df_fmt["FATURAMENTO - VALOR"] = df_fmt["FATURAMENTO - VALOR"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
        df_fmt["DESPESAS"] = df_fmt["DESPESAS"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
        df_fmt["RESULTADO"] = df_fmt["RESULTADO"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
        df_fmt["VAR %"] = df_fmt["VAR %"].apply(lambda v: f"{v:.1f}%")
        return df_fmt

    # ================================
    # 6) EXIBIR TABELA 2024
    # ================================
    st.subheader("📘 Resultado 2024")

    tabela_2024_fmt = format_table(tabela_2024)
    st.dataframe(tabela_2024_fmt, use_container_width=True)

    # Totais 2024
    total_fat24 = tabela_2024["FATURAMENTO - VALOR"].sum()
    total_desp24 = tabela_2024["DESPESAS"].sum()
    total_res24 = total_fat24 - total_desp24
    total_var24 = (total_res24 / total_fat24) * 100

    st.metric("Total Faturamento 2024", f"R$ {total_fat24:,.2f}".replace(",", "."))
    st.metric("Total Despesas 2024", f"R$ {total_desp24:,.2f}".replace(",", "."))
    st.metric("Resultado Total 2024", f"R$ {total_res24:,.2f}".replace(",", "."))
    st.metric("Variação Total 2024", f"{total_var24:.1f}%")

    # ================================
    # 7) EXIBIR TABELA 2025
    # ================================
    st.subheader("📙 Resultado 2025")

    tabela_2025_fmt = format_table(tabela_2025)
    st.dataframe(tabela_2025_fmt, use_container_width=True)

    # Totais 2025
    total_fat25 = tabela_2025["FATURAMENTO - VALOR"].sum()
    total_desp25 = tabela_2025["DESPESAS"].sum()
    total_res25 = total_fat25 - total_desp25
    total_var25 = (total_res25 / total_fat25) * 100

    st.metric("Total Faturamento 2025", f"R$ {total_fat25:,.2f}".replace(",", "."))
    st.metric("Total Despesas 2025", f"R$ {total_desp25:,.2f}".replace(",", "."))
    st.metric("Resultado Total 2025", f"R$ {total_res25:,.2f}".replace(",", "."))
    st.metric("Variação Total 2025", f"{total_var25:.1f}%")



