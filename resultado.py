import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render():

    st.title("🧾 Resultado e Margens – Receita x Despesas")
    st.markdown("---")

    # ==================================================================
    # 1. CARREGAR PLANILHA DE FATURAMENTO
    # ==================================================================
    fat_path = "Consolidado de Faturamento - 2024 e 2025.xlsx"

    if not os.path.exists(fat_path):
        st.error(f"Arquivo de faturamento não encontrado: {fat_path}")
        return

    df_fat = pd.read_excel(fat_path)

    # Extrair número do mês
    df_fat["MES_NUM"] = df_fat["Mês"].str[:2].astype(int)

    meses_dict = {
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
        12: "12 - Dezembro"
    }

    # Nome do mês padronizado
    df_fat["MES"] = df_fat["MES_NUM"].map(meses_dict)

    # Garantir tipos
    df_fat["Faturamento"] = pd.to_numeric(df_fat["Faturamento - Valor"], errors="coerce")
    df_fat["Ano"] = pd.to_numeric(df_fat["Ano"], errors="coerce")

    # Consolidar faturamento por mês/ano
    fat_mensal = df_fat.groupby(["Ano", "MES_NUM", "MES"])["Faturamento"].sum().reset_index()

    # ==================================================================
    # 2. CARREGAR PLANILHA DE DESPESAS
    # ==================================================================
    desp_path = "despesas_2024_2025.xlsx"

    if not os.path.exists(desp_path):
        st.error(f"Arquivo de despesas não encontrado: {desp_path}")
        return

    df_desp = pd.read_excel(desp_path)
    df_desp.columns = df_desp.columns.str.upper()

    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)
    df_desp["MES"] = df_desp["MES_NUM"].map(meses_dict)

    df_desp["ANO"] = pd.to_numeric(df_desp["ANO"], errors="coerce")
    df_desp["VALOR"] = pd.to_numeric(df_desp["VALOR"], errors="coerce")

    desp_mensal = df_desp.groupby(["ANO", "MES_NUM", "MES"])["VALOR"].sum().reset_index()

    # ==================================================================
    # 3. MERGE – UNIR FATURAMENTO + DESPESAS
    # ==================================================================
    base = fat_mensal.merge(
        desp_mensal,
        left_on=["Ano", "MES_NUM"],
        right_on=["ANO", "MES_NUM"],
        how="left"
    ).fillna(0)

    # Remover colunas duplicadas
    drop_cols = [c for c in ["ANO"] if c in base.columns]
    if drop_cols:
        base = base.drop(columns=drop_cols)

    # ==================================================================
    # 4. CALCULAR RESULTADO E MARGEM
    # ==================================================================
    base["Resultado"] = base["Faturamento"] - base["VALOR"]

    base["Margem (%)"] = base.apply(
        lambda row: (row["Resultado"] / row["Faturamento"] * 100) if row["Faturamento"] > 0 else 0,
        axis=1
    )

    base["Ano"] = base["Ano"].astype(str)

    # ==================================================================
    # 5. PREPARAR DATAFRAME PARA O GRÁFICO (ESSENCIAL!)
    # ==================================================================
    plot_df = base.copy()

    plot_df["MES"] = plot_df["MES"].astype(str)
    plot_df["Resultado"] = pd.to_numeric(plot_df["Resultado"], errors="coerce")
    plot_df["Ano"] = plot_df["Ano"].astype(str)

    # Remover qualquer coluna problemática do merge
    cols_to_drop = [c for c in plot_df.columns if c.endswith("_x") or c.endswith("_y")]
    if cols_to_drop:
        plot_df = plot_df.drop(columns=cols_to_drop)

    # ==================================================================
    # 6. GRÁFICO – RESULTADO MENSAL
    # ==================================================================
    st.subheader("📉 Resultado Mensal (Lucro / Prejuízo)")

    fig = px.bar(
        data_frame=plot_df,  # <-- ESSA LINHA EVITA O ERRO DO PLOTLY!
        x="MES",
        y="Resultado",
        color="Ano",
        text=plot_df["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
        barmode="group",
        color_discrete_map={
            "2024": "#FF8C00",
            "2025": "#005BBB"
        }
    )

    fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=16)
    fig.update_layout(height=600, plot_bgcolor="white")

    st.plotly_chart(fig, use_container_width=True)

    # ==================================================================
    # 7. TABELA CONSOLIDADA
    # ==================================================================
    st.subheader("📄 Tabela Consolidada: Faturamento x Despesas x Margem")

    tabela = base[["Ano", "MES", "Faturamento", "VALOR", "Resultado", "Margem (%)"]].copy()

    tabela["Faturamento"] = tabela["Faturamento"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["VALOR"] = tabela["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Resultado"] = tabela["Resultado"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    tabela["Margem (%)"] = tabela["Margem (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(tabela, use_container_width=True)

