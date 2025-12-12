import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # =============================
    # 2) PADRONIZAR COLUNAS
    # =============================
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_desp["ANO"] = df_desp["ANO"].astype(int)

    # Converter valores que vêm como texto
    df_fat["Faturamento - Valor"] = (
        df_fat["Faturamento - Valor"]
        .astype(str)
        .str.replace(".", "")
        .str.replace(",", ".")
        .astype(float)
    )

    df_desp["VALOR"] = (
        df_desp["VALOR"]
        .astype(str)
        .str.replace(".", "")
        .str.replace(",", ".")
        .astype(float)
    )

    # =============================
    # 3) EXTRAIR Nº DO MÊS
    # =============================
    df_fat["MES_NUM"] = df_fat["Mês"].str[:2].astype(int)
    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # =============================
    # 4) AGRUPAR FATURAMENTO E DESPESAS
    # =============================
    fat_mensal = df_fat.groupby(["Ano", "MES_NUM"])["Faturamento - Valor"].sum()
    desp_mensal = df_desp.groupby(["ANO", "MES_NUM"])["VALOR"].sum()

    # =============================
    # 5) CRIAR TABELA RESULTADO
    # =============================
    resultado = pd.DataFrame({
        "FAT_2024": fat_mensal.loc[2024],
        "DESP_2024": desp_mensal.loc[2024],
        "RES_2024": fat_mensal.loc[2024] - desp_mensal.loc[2024],

        "FAT_2025": fat_mensal.loc[2025],
        "DESP_2025": desp_mensal.loc[2025],
        "RES_2025": fat_mensal.loc[2025] - desp_mensal.loc[2025],
    })

    # =============================
    # 6) FORMATAR TABELA PARA EXIBIÇÃO
    # =============================
    def fmt(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    tabela_fmt = resultado.copy()
    for col in tabela_fmt.columns:
        tabela_fmt[col] = tabela_fmt[col].apply(fmt)

    st.subheader("📄 Resultado Financeiro por Mês")
    st.dataframe(tabela_fmt, use_container_width=True)

    # =============================
    # 7) GRÁFICO MELHORADO (RESULTADO)
    # =============================
    resultado_plot = resultado.reset_index().rename(columns={"index": "Mês"})

    fig = px.line(
        resultado_plot,
        x="Mês",
        y=["RES_2024", "RES_2025"],
        markers=True,
        title="📈 Evolução do Resultado (Lucro Líquido)"
    )

    fig.update_layout(
        yaxis_tickformat="R$,.0f",
        legend_title_text="Ano",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
