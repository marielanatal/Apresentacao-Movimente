iimport streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(str)   # <---- ESSENCIAL para não empilhar

    # =============== RESUMO POR ANO ==================
    resumo = df.groupby("Ano")["Faturamento - Valor"].sum().reset_index()

    fat_2024 = resumo.loc[resumo["Ano"] == "2024", "Faturamento - Valor"].values[0]
    fat_2025 = resumo.loc[resumo["Ano"] == "2025", "Faturamento - Valor"].values[0]

    col1, col2 = st.columns(2)
    col1.metric("Ano 2024", f"R$ {fat_2024:,.0f}".replace(",", "."))
    col2.metric("Ano 2025", f"R$ {fat_2025:,.0f}".replace(",", "."))

    # =============== AJUSTE DOS MESES ==================
    df["Mês_num"] = df["Mês"].str[:2].astype(int)
    df = df.sort_values(["Mês_num", "Ano"])

    tabela_mensal = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()

    # =============== GRÁFICO ==================
    fig = px.bar(
        tabela_mensal,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",   # <----- GARANTE LADO A LADO
        color_discrete_map={"2024": "#FF8C00", "2025": "#005BBB"},
    )

    # Texto formatado em R$
    tabela_mensal["texto"] = tabela_mensal["Faturamento - Valor"].apply(lambda v: f"R$ {v:,.0f}".replace(",", "."))

    fig.update_traces(
        text=tabela_mensal["texto"],
        texttemplate="%{text}",
        textposition="outside",
        textfont_size=18,
        cliponaxis=False
    )

    # eixo X categórico para evitar empilhamento escondido
    fig.update_xaxes(type="category", tickfont_size=16)
    fig.update_yaxes(tickfont_size=16)

    fig.update_layout(
        title="Comparativo Mensal",
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============== TABELA FINAL ==================
    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    tabela = tabela.sort_values("Mês")

    tabela["Diferença (R$)"] = tabela["2025"] - tabela["2024"]
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela["2024"]) * 100

    # Formatação
    tabela_fmt = tabela.copy()
    tabela_fmt["2024"] = tabela_fmt["2024"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["2025"] = tabela_fmt["2025"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (R$)"] = tabela_fmt["Diferença (R$)"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (%)"] = tabela_fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela_fmt, use_container_width=True)
