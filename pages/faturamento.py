import streamlit as st
import pandas as pd
import plotly.express as px
import os

def render():

    st.title("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    uploaded_file = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])

    ARQUIVO_PADRAO = "Consolidado de Faturamento - 2024 e 2025.xlsx"

    def carregar_planilha():
        if uploaded_file is not None:
            return pd.read_excel(uploaded_file)

        if os.path.exists(ARQUIVO_PADRAO):
            st.success(f"📁 Carregando arquivo padrão: {ARQUIVO_PADRAO}")
            return pd.read_excel(ARQUIVO_PADRAO)

        st.warning("Envie uma planilha Excel para visualizar o dashboard.")
        return None

    df = carregar_planilha()

    if df is None:
        return

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype(int)
    df["Faturamento - Valor"] = pd.to_numeric(df["Faturamento - Valor"], errors="coerce")
    df["Meta"] = pd.to_numeric(df["Meta"], errors="coerce")
    df["Mes_Num"] = df["Mês"].str[:2].astype(int)

    def format_short(num):
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"

    st.subheader("📌 Resumo por Ano")
    col1, col2 = st.columns(2)

    for ano, col in zip([2024, 2025], [col1, col2]):
        dados_ano = df[df["Ano"] == ano]
        fat_total = dados_ano["Faturamento - Valor"].sum()
        meta_total = dados_ano["Meta"].sum()
        ating = (fat_total / meta_total * 100) if meta_total > 0 else 0

        col.metric(
            label=f"Ano {ano}",
            value=f"Faturamento: R$ {fat_total:,.0f}".replace(",", "."),
            delta=f"{ating:.1f}% da Meta (Meta: R$ {meta_total:,.0f})".replace(",", ".")
        )

    st.subheader("📊 Comparativo Mensal 2024 x 2025 (Lado a Lado)")

    df_plot = df.groupby(
        ["Mês", "Mes_Num", "Ano"], as_index=False
    )["Faturamento - Valor"].sum()

    df_plot = df_plot.sort_values(["Mes_Num", "Ano"])
    df_plot["Ano"] = df_plot["Ano"].astype(str)
    df_plot["Valor_fmt"] = df_plot["Faturamento - Valor"].apply(format_short)

    fig = px.bar(
        df_plot,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",
        text="Valor_fmt",
        color_discrete_map={
            "2024": "#FF8C00",
            "2025": "#005BBB",
        }
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=26, color="black", family="Arial Black"),
        cliponaxis=False
    )

    fig.update_layout(
        yaxis_title="Faturamento (R$)",
        xaxis_title="Mês",
        bargap=0.28,
        height=700,
        plot_bgcolor="white",
        margin=dict(t=80, b=80)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Tabela Comparativa por Ano")

    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    for ano in tabela.columns[1:]:
        tabela[ano] = tabela[ano].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    st.dataframe(tabela, use_container_width=True)
