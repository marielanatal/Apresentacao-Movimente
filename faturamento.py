import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    # =============================
    # 1) CARREGAR PLANILHA DIRETO DO REPOSITÓRIO
    # =============================
    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")

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
    # 3) COMPARATIVO MENSAL — GRÁFICO LADO A LADO + NÚMEROS GIGANTES
    # =============================

    df["Mês_num"] = df["Mês"].str[:2].astype(int)

    tabela_mensal = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()
    tabela_mensal["Ano"] = tabela_mensal["Ano"].astype(str)
    tabela_mensal = tabela_mensal.sort_values(["Mês_num", "Ano"])

    # Rótulos formatados
    tabela_mensal["label"] = tabela_mensal["Faturamento - Valor"].apply(
        lambda v: f"{v:,.0f}".replace(",", ".")
    )

    st.subheader("📊 Comparativo Mensal 2024 x 2025 (Lado a Lado)")

    fig = px.bar(
        tabela_mensal,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        text="label",
        barmode="group",
        color_discrete_map={"2024": "#FF8C00", "2025": "#005BBB"},
    )

    # 🔥 TRUQUE PARA OS NÚMEROS FICAREM REALMENTE GRANDES
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=38, family="Arial Black", color="black"),
        textangle=0,
        cliponaxis=False
    )

    # 🔥 IMPEDIR STREAMLIT DE COMPRIMIR O GRÁFICO
    fig.update_layout(
        autosize=False,
        width=1900,
        height=900,
        margin=dict(l=40, r=40, t=120, b=200),
        bargap=0.20,
        bargroupgap=0.05,
        xaxis=dict(tickfont=dict(size=22)),
        yaxis=dict(tickfont=dict(size=22)),
        legend=dict(font=dict(size=26)),
    )

    st.plotly_chart(fig, use_container_width=False)

    # =============================
    # 4) TABELA COMPARATIVA FINAL + DIFERENÇA
    # =============================

    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    tabela["Diferença (R$)"] = tabela[2025] - tabela[2024]
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela[2024]) * 100

    # Formatação
    tabela_fmt = tabela.copy()
    tabela_fmt[2024] = tabela_fmt[2024].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt[2025] = tabela_fmt[2025].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (R$)"] = tabela_fmt["Diferença (R$)"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (%)"] = tabela_fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa Final")
    st.dataframe(tabela_fmt, use_container_width=True)
