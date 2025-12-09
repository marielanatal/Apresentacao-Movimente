import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    # =============================
    # 1) CARREGAR PLANILHA AUTOMATICAMENTE
    # =============================
    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")

    # Padronizar colunas
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(int)
    df["Mês_num"] = df["Mês"].str[:2].astype(int)

    # =============================
    # 2) CARDS DE RESUMO
    # =============================
    resumo = df.groupby("Ano")["Faturamento - Valor"].sum().reset_index()

    fat_2024 = resumo.loc[resumo["Ano"] == 2024, "Faturamento - Valor"].values[0]
    fat_2025 = resumo.loc[resumo["Ano"] == 2025, "Faturamento - Valor"].values[0]

    col1, col2 = st.columns(2)
    col1.metric("Total 2024", f"R$ {fat_2024:,.0f}".replace(",", "."))
    col2.metric("Total 2025", f"R$ {fat_2025:,.0f}".replace(",", "."))

    # =============================
    # 3) GRÁFICO COM TEXTO REALMENTE GRANDE
    # =============================
    st.subheader("📊 Comparativo Mensal 2024 x 2025 (Lado a Lado)")

    tabela_mensal = df.groupby(
        ["Ano", "Mês_num", "Mês"]
    )["Faturamento - Valor"].sum().reset_index()

    tabela_mensal["Ano"] = tabela_mensal["Ano"].astype(str)
    tabela_mensal = tabela_mensal.sort_values(["Mês_num", "Ano"])

    # Criar texto manual
    tabela_mensal["label"] = tabela_mensal["Faturamento - Valor"].apply(
        lambda v: f"{v:,.0f}".replace(",", ".")
    )

    fig = px.bar(
        tabela_mensal,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",
        text="label",
        color_discrete_map={"2024": "#FF8C00", "2025": "#005BBB"}
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=50, family="Arial Black", color="black"),  # <<< TAMANHO AQUI
        cliponaxis=False
    )

    fig.update_layout(
        width=1400,     # <<< impede o Streamlit de esmagar o texto
        height=800,
        margin=dict(t=100, b=160),
        bargap=0.20,
        bargroupgap=0.05,
        xaxis_title="Mês",
        yaxis_title="Faturamento (R$)",
        legend_title="Ano"
    )

    st.plotly_chart(fig)   # <<< NÃO usar container_width, senão ele reduz a fonte

    # =============================
    # 4) TABELA COMPARATIVA FINAL
    # =============================

    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    tabela = tabela.sort_values("Mês")

    tabela["Diferença (R$)"] = tabela[2025] - tabela[2024]
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela[2024]) * 100

    # Formatação
    tabela_fmt = tabela.copy()
    tabela_fmt[2024] = tabela_fmt[2024].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt[2025] = tabela_fmt[2025].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (R$)"] = tabela_fmt["Diferença (R$)"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (%)"] = tabela_fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela_fmt, use_container_width=True)


