import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

    # =============================================
    # 1) CARREGAR PLANILHA DIRETAMENTE DO REPOSITÓRIO
    # =============================================
    df = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")

    # Padronizar colunas
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Ano"].astype(int)

    # =============================================
    # 2) RESUMO POR ANO
    # =============================================
    resumo = df.groupby("Ano")["Faturamento - Valor"].sum().reset_index()

    fat_2024 = resumo.loc[resumo["Ano"] == 2024, "Faturamento - Valor"].values[0]
    fat_2025 = resumo.loc[resumo["Ano"] == 2025, "Faturamento - Valor"].values[0]

    # ---------------------------------------------
    # CARDS ESTILIZADOS
    # ---------------------------------------------
    def card(valor, titulo, cor):
        st.markdown(
            f"""
            <div style="
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border-left: 6px solid {cor};
                height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                margin-bottom: 10px;
            ">
                <span style="font-size:16px; color:#555;">{titulo}</span>
                <span style="font-size:34px; font-weight:700; color:{cor};">
                    R$ {valor/1_000_000:.2f}M
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)

    with col1:
        card(fat_2024, "Faturamento 2024", "#FF8C00")

    with col2:
        card(fat_2025, "Faturamento 2025", "#005BBB")

    # =============================================
    # 3) COMPARATIVO MENSAL
    # =============================================

    df["Mês_num"] = df["Mês"].str[:2].astype(int)
    tabela_mensal = df.groupby(["Ano", "Mês_num", "Mês"])["Faturamento - Valor"].sum().reset_index()

    # Ordenação correta
    tabela_mensal = tabela_mensal.sort_values(["Mês_num", "Ano"])

    # Criar coluna formatada
    tabela_mensal["Valor_fmt"] = tabela_mensal["Faturamento - Valor"].apply(
        lambda v: f"R$ {v/1_000_000:.1f}M"
    )

    # Gráfico
    fig = px.bar(
        tabela_mensal,
        x="Mês",
        y="Faturamento - Valor",
        color="Ano",
        barmode="group",
        color_discrete_map={2024: "#FF8C00", 2025: "#005BBB"},
        text="Valor_fmt",
        title="Comparativo Mensal"
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14, color="black")
    )

    fig.update_layout(
        yaxis_title="Faturamento",
        xaxis_title="Mês",
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        bargap=0.25
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============================================
    # 4) TABELA COMPARATIVA FINAL
    # =============================================

    tabela = df.pivot_table(
        index="Mês",
        columns="Ano",
        values="Faturamento - Valor",
        aggfunc="sum"
    ).reset_index()

    tabela = tabela.sort_values("Mês")

    tabela["Diferença (R$)"] = tabela[2025] - tabela[2024]
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela[2024]) * 100

    tabela_fmt = tabela.copy()

    tabela_fmt[2024] = tabela_fmt[2024].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt[2025] = tabela_fmt[2025].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (R$)"] = tabela_fmt["Diferença (R$)"].apply(lambda v: f"R$ {v:,.2f}".replace(",", "."))
    tabela_fmt["Diferença (%)"] = tabela_fmt["Diferença (%)"].apply(lambda v: f"{v:.1f}%")

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela_fmt, use_container_width=True)



