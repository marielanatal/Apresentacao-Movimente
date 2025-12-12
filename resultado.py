import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # ============================================================
    # 1) CARREGAR PLANILHAS (já estão no repositório)
    # ============================================================

    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # ------------------------------------------------------------
    # PADRONIZAR COLUNAS
    # ------------------------------------------------------------
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_desp["ANO"] = df_desp["ANO"].astype(int)

    # ============================================================
    # 2) PREPARAR FATURAMENTO
    # ============================================================

    df_fat["MÊS_NUM"] = df_fat["MÊS"].str[:2].astype(int)

    fat_mensal = df_fat.groupby(["Ano", "MÊS_NUM", "MÊS"])["Faturamento - Valor"].sum().reset_index()
    fat_mensal = fat_mensal.rename(columns={"Faturamento - Valor": "FATURAMENTO"})

    # ============================================================
    # 3) PREPARAR DESPESAS
    # ============================================================

    df_desp["MÊS_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    desp_mensal = df_desp.groupby(["ANO", "MÊS_NUM", "MÊS"])["VALOR"].sum().reset_index()
    desp_mensal = desp_mensal.rename(columns={"ANO": "Ano", "VALOR": "DESPESA"})

    # ============================================================
    # 4) JUNTAR FATURAMENTO + DESPESAS
    # ============================================================

    base = pd.merge(
        fat_mensal,
        desp_mensal,
        how="outer",
        on=["Ano", "MÊS_NUM", "MÊS"]
    ).fillna(0)

    base["RESULTADO"] = base["FATURAMENTO"] - base["DESPESA"]

    # ============================================================
    # 5) CRIAR TABELAS PARA 2024 E 2025
    # ============================================================

    tabela_2024 = base[base["Ano"] == 2024].copy()
    tabela_2025 = base[base["Ano"] == 2025].copy()

    # ------ Variação mês a mês ------
    tabela_2024["VARIAÇÃO"] = tabela_2024["RESULTADO"].diff()
    tabela_2025["VARIAÇÃO"] = tabela_2025["RESULTADO"].diff()

    # ------ Totais ------
    total_2024 = pd.DataFrame({
        "MÊS": ["TOTAL"],
        "FATURAMENTO": [tabela_2024["FATURAMENTO"].sum()],
        "DESPESA": [tabela_2024["DESPESA"].sum()],
        "RESULTADO": [tabela_2024["RESULTADO"].sum()],
        "VARIAÇÃO": [None]
    })

    total_2025 = pd.DataFrame({
        "MÊS": ["TOTAL"],
        "FATURAMENTO": [tabela_2025["FATURAMENTO"].sum()],
        "DESPESA": [tabela_2025["DESPESA"].sum()],
        "RESULTADO": [tabela_2025["RESULTADO"].sum()],
        "VARIAÇÃO": [None]
    })

    tabela_2024 = pd.concat([tabela_2024, total_2024], ignore_index=True)
    tabela_2025 = pd.concat([tabela_2025, total_2025], ignore_index=True)

    # ============================================================
    # 6) FORMATAR EM R$
    # ============================================================

    def fmt(v):
        if pd.isna(v):
            return "-"
        return f"R$ {v:,.2f}".replace(",", ".")  # troca . por , se preferir

    for col in ["FATURAMENTO", "DESPESA", "RESULTADO", "VARIAÇÃO"]:
        tabela_2024[col] = tabela_2024[col].apply(fmt)
        tabela_2025[col] = tabela_2025[col].apply(fmt)

    # ============================================================
    # 7) EXIBIR TABELAS
    # ============================================================

    st.subheader("📄 Resultado Consolidado – Ano 2024")
    st.dataframe(tabela_2024, use_container_width=True)

    st.subheader("📄 Resultado Consolidado – Ano 2025")
    st.dataframe(tabela_2025, use_container_width=True)

    # ============================================================
    # 8) GRÁFICO – LINHA DO RESULTADO
    # ============================================================

    grafico = base.copy()
    grafico["RESULTADO_MILHÕES"] = grafico["RESULTADO"] / 1_000_000

    fig = px.line(
        grafico,
        x="MÊS_NUM",
        y="RESULTADO_MILHÕES",
        color="Ano",
        markers=True,
        title="Linha do Resultado (em Milhões)"
    )

    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Resultado (R$ milhões)"
    )

    st.plotly_chart(fig, use_container_width=True)



