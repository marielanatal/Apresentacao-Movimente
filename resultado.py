import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📈 Comparativo Faturamento, Despesas e Resultado")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # =============================
    # 2) PADRONIZAR NOMES DAS COLUNAS
    # =============================
    df_fat.columns = df_fat.columns.astype(str).str.strip()
    df_desp.columns = df_desp.columns.astype(str).str.strip()

    # =============================
    # 3) AJUSTAR DADOS FATURAMENTO
    # =============================
    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_fat["MÊS_NUM"] = df_fat["Mês"].str[:2].astype(int)

    # =============================
    # 4) AJUSTAR DADOS DESPESAS
    # =============================
    df_desp["ANO"] = df_desp["ANO"].astype(int)
    df_desp["MÊS_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # =============================
    # 5) AGRUPAR POR ANO/MÊS
    # =============================
    tabela_fat = df_fat.groupby(["Ano", "MÊS_NUM"])["Faturamento - Valor"].sum().reset_index()
    tabela_desp = df_desp.groupby(["ANO", "MÊS_NUM"])["VALOR"].sum().reset_index()

    tabela_fat.rename(columns={"Ano": "ANO", "Faturamento - Valor": "FAT"}, inplace=True)
    tabela_desp.rename(columns={"VALOR": "DESP"}, inplace=True)

    # =============================
    # 6) JUNTAR TABELAS
    # =============================
    base = pd.merge(tabela_fat, tabela_desp, on=["ANO", "MÊS_NUM"], how="outer")
    base["DESP"] = base["DESP"].fillna(0)
    base["RESULT"] = base["FAT"] - base["DESP"]

    # =============================
    # 7) SEPARAR 2024 E 2025
    # =============================
    df24 = base[base["ANO"] == 2024].sort_values("MÊS_NUM")
    df25 = base[base["ANO"] == 2025].sort_values("MÊS_NUM")

    # =============================
    # 8) FORMATAR R$ PARA TABELAS
    # =============================
    def fmt(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    df24_fmt = df24.copy()
    df25_fmt = df25.copy()

    for col in ["FAT", "DESP", "RESULT"]:
        df24_fmt[col] = df24[col].apply(fmt)
        df25_fmt[col] = df25[col].apply(fmt)

    # =============================
    # 9) SOMATÓRIO FINAL DAS TABELAS
    # =============================
    soma_24 = {
        "FAT_TOTAL": df24["FAT"].sum(),
        "DESP_TOTAL": df24["DESP"].sum(),
        "RESULT_TOTAL": df24["RESULT"].sum()
    }

    soma_25 = {
        "FAT_TOTAL": df25["FAT"].sum(),
        "DESP_TOTAL": df25["DESP"].sum(),
        "RESULT_TOTAL": df25["RESULT"].sum()
    }

    # =============================
    # 10) MOSTRAR TABELA 2024
    # =============================
    st.subheader("📄 Resultado 2024")
    st.dataframe(df24_fmt, use_container_width=True)

    st.markdown(f"""
    ### **Totais 2024**
    • **Faturamento:** {fmt(soma_24['FAT_TOTAL'])}  
    • **Despesas:** {fmt(soma_24['DESP_TOTAL'])}  
    • **Resultado:** {fmt(soma_24['RESULT_TOTAL'])}  
    """)

    # =============================
    # 11) MOSTRAR TABELA 2025
    # =============================
    st.subheader("📄 Resultado 2025")
    st.dataframe(df25_fmt, use_container_width=True)

    st.markdown(f"""
    ### **Totais 2025**
    • **Faturamento:** {fmt(soma_25['FAT_TOTAL'])}  
    • **Despesas:** {fmt(soma_25['DESP_TOTAL'])}  
    • **Resultado:** {fmt(soma_25['RESULT_TOTAL'])}  
    """)

    # =============================
    # 12) GRÁFICO LIMPO LINHA DO RESULTADO
    # =============================
    graf = base.sort_values(["ANO", "MÊS_NUM"])

    fig = px.line(
        graf,
        x="MÊS_NUM",
        y="RESULT",
        color="ANO",
        markers=True,
        title="Linha do Resultado (2024 x 2025)",
        labels={"MÊS_NUM": "Mês", "RESULT": "Resultado (R$)"}
    )

    fig.update_layout(
        yaxis_tickformat=",",
        legend_title_text="Ano",
        height=450
    )

    # Formatar números como R$
    fig.update_traces(
        hovertemplate="R$ %{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.plotly_chart(fig, use_container_width=True)

