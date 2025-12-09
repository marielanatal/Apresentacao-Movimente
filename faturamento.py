import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    # =============================
    # 1) CARREGAR PLANILHA
    # =============================
    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(int)

    # =============================
    # CARDS INICIAIS
    # =============================
    resumo = df.groupby("Ano")["Faturamento - Valor"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Ano 2024", f"R$ {resumo[2024]:,.0f}".replace(",", "."))
    col2.metric("Ano 2025", f"R$ {resumo[2025]:,.0f}".replace(",", "."))

    # =============================
    # 2) GRÁFICO AGRUPADO SEM EMPILHAR
    # =============================
    df["Mês_num"] = df["Mês"].str[:2].astype(int)

    tabela = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()
    tabela = tabela.sort_values(["Mês_num", "Ano"])  # ESSENCIAL PARA NÃO EMPILHAR

    # Criar texto abreviado
    def abrev(v):
        return f"R$ {v/1_000_000:.1f}M"

    tabela["Label"] = tabela["Faturamento - Valor"].apply(abrev)

    fig = px.bar(
        tabela,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",          # GARANTE LADO A LADO
        text="Label",             # TEXTO DIRETO NO PX
        color_discrete_map={"2024": "#FF8C00", "2025": "#005BBB"}
    )

    # AUMENTAR TAMANHO DO TEXTO SEM PERDER O AGRUPAMENTO
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=26, color="black", family="Arial")
    )

    # NÃO USAR cliponaxis — isso QUEBRA o agrupamento no Plotly
    fig.update_layout(
        title="Comparativo Mensal",
        title_x=0.5,
        uniformtext_minsize=26,
        uniformtext_mode="show",
        bargap=0.25,              # deixa espaço entre grupos
        bargroupgap=0.05          # deixa coladas barras do mesmo grupo
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # 3) TABELA FINAL
    # =============================
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

