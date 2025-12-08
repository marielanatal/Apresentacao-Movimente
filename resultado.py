import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render():

    st.title("🧾 Resultado e Margens – Receita x Despesas")
    st.markdown("---")

    # ------------------------------
    # 1. FATURAMENTO
    # ------------------------------
    fat_path = "Consolidado de Faturamento - 2024 e 2025.xlsx"

    if not os.path.exists(fat_path):
        st.error(f"Arquivo de faturamento não encontrado: {fat_path}")
        return

    df_fat = pd.read_excel(fat_path)

    # Extrair número do mês da coluna "Mês"
    df_fat["MES_NUM"] = df_fat["Mês"].str[:2].astype(int)
    df_fat["MES"] = df_fat["MES_NUM"].map({
        1: "01 - Janeiro",
        2: "02 - Fevereiro",
        3: "03 - Março",
        4: "04 - Abril",
        5: "05 - Maio",
        6: "06 - Junho",
        7: "07 - Julho",
        8: "08 - Agosto",
        9: "09 - Setembro",
        10: "10 - Outubro",
        11: "11 - Novembro",
        12: "12 - Dezembro",
    })

    df_fat["Faturamento"] = pd.to_numeric(df_fat["Faturamento - Valor"], errors="coerce")

    fat_mensal = df_fat.groupby(["Ano", "MES_NUM", "MES"])["Faturamento"].sum().reset_index()

    # ------------------------------
    # 2. DESPESAS
    # ------------------------------
    desp_path = "despesas_2024_2025.xlsx"

    if not os.path.exists(desp_path):
        st.error(f"Arquivo de despesas não encontrado: {desp_path}")
        return

    df_desp = pd.read_excel(desp_path)
    df_desp.columns = df_desp.columns.str.upper()

    # Extrair número do mês — MESMO MÉTODO
    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)
    df_desp["MES"] = df_desp["MES_NUM"].map({
        1: "01 - Janeiro",
        2: "02 - Fevereiro",
        3: "03 - Março",
        4: "04 - Abril",
        5: "05 - Maio",
        6: "06 - Junho",
        7: "07 - Julho",
        8: "08 - Agosto",
        9: "09 - Setembro",
        10: "10 - Outubro",
        11: "11 - Novembro",
        12: "12 - Dezembro",
    })

    df_desp["ANO"] = pd.to_numeric(df_desp["ANO"])
    df_desp["VALOR"] = pd.to_numeric(df_desp["VALOR"], errors="coerce")

    desp_mensal = df_desp.groupby(["ANO", "MES_NUM", "MES"])["VALOR"].sum().reset_index()

    # ------------------------------
    # 3. MERGE — agora usando MES_NUM (padronizado)
    # ------------------------------
    base = fat_mensal.merge(
        desp_mensal,
        left_on=["Ano", "MES_NUM"],
        right_on=["ANO", "MES_NUM"],
        how="left"
    ).fillna(0)

    # ------------------------------
    # 4. CALCULOS
    # ------------------------------
    base["Resultado"] = base["Faturamento"] - base["VALOR"]
    base["Margem (%)"] = base["Resultado"] / base["Faturamento"] * 100

    # ------------------------------
    # 5. GRÁFICO
    # ------------------------------
    st.subheader("📉 Resultado Mensal (Lucro / Prejuízo)")

    fig = px.bar(
        base,
        x="MES",
        y="Resultado",
        color="Ano",
        text=base["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
        barmode="group",
        color_discrete_map={2024: "#FF8C00", 2025: "#005BBB"},
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 6. TABELA
    # ------------------------------
    st.subheader("📄 Tabela Consolidada")

    tabela = base[["Ano", "MES", "Faturamento", "VALOR", "Resultado", "Margem (%)"]].copy()

    tabela["Faturamento"] = tabela["Faturamento"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["VALOR"] = tabela["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Resultado"] = tabela["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Margem (%)"] = tabela["Margem (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(tabela, use_container_width=True)
