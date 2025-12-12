import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(int)

    resumo = df.groupby("Ano")["Faturamento - Valor"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Ano 2024", f"R$ {resumo[2024]:,.0f}".replace(",", "."))
    col2.metric("Ano 2025", f"R$ {resumo[2025]:,.0f}".replace(",", "."))

    # ============================
    # GRÁFICO DEFINITIVO (SEM EMPILHAR)
    # ============================
    df["Mês_num"] = df["Mês"].str[:2].astype(int)
    tabela = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()
    tabela = tabela.sort_values(["Mês_num", "Ano"])

    meses = tabela["Mês"].unique()
    valores_2024 = tabela[tabela["Ano"] == 2024]["Faturamento - Valor"].tolist()
    valores_2025 = tabela[tabela["Ano"] == 2025]["Faturamento - Valor"].tolist()

    # Texto formatado
    label_2024 = [f"R$ {v/1_000_000:.1f}M" for v in valores_2024]
    label_2025 = [f"R$ {v/1_000_000:.1f}M" for v in valores_2025]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=meses,
        y=valores_2024,
        name="2024",
        marker_color="#FF8C00",
        text=label_2024,
        textposition="outside",
        textfont=dict(size=60)
    ))

    fig.add_trace(go.Bar(
        x=meses,
        y=valores_2025,
        name="2025",
        marker_color="#005BBB",
        text=label_2025,
        textposition="outside",
        textfont=dict(size=18)
    ))

    fig.update_layout(
        barmode="group",          # GARANTE LADO A LADO FORÇADO
        bargap=0.20,              # espaço entre grupos
        bargroupgap=0.05,         # espaço entre barras do mesmo grupo
        title="Comparativo Mensal",
        title_x=0.5,
        yaxis_title="Faturamento",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # ============================
    # TABELA FINAL
    # ============================
    tabela_final = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    tabela_final["Diferença (R$)"] = tabela_final[2025] - tabela_final[2024]
    tabela_final["Diferença (%)"] = (tabela_final["Diferença (R$)"] / tabela_final[2024]) * 100

    fmt = tabela_final.copy()
    for col in [2024, 2025, "Diferença (R$)"]:
        fmt[col] = fmt[col].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))

    fmt["Diferença (%)"] = fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(fmt, use_container_width=True)
