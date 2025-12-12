import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def render():
    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # ------------------------------------------------------------
    # 1) CARREGAR PLANILHA DO REPOSITÓRIO
    # ------------------------------------------------------------
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # Padronizar
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_desp["Ano"] = df_desp["Ano"].astype(int)

    # ------------------------------------------------------------
    # 2) AGRUPAR FATURAMENTO
    # ------------------------------------------------------------
    fat = df_fat.groupby(["Ano", "Mês", "Mês_num"])["Faturamento - Valor"].sum().reset_index()

    # ------------------------------------------------------------
    # 3) AGRUPAR DESPESAS
    # ------------------------------------------------------------
    desp = df_desp.groupby(["Ano", "Mês", "Mês_num"])["Valor"].sum().reset_index()

    # ------------------------------------------------------------
    # 4) MONTAR TABELA FINAL UNIFICADA
    # ------------------------------------------------------------
    tabela = (
        fat.merge(desp, on=["Ano", "Mês", "Mês_num"], how="outer", suffixes=("_fat", "_desp"))
        .sort_values("Mês_num")
    )

    tabela.rename(columns={
        "Faturamento - Valor": "Faturamento",
        "Valor": "Despesa"
    }, inplace=True)

    # ------------------------------------------------------------
    # 5) SEPARAR 2024 E 2025
    # ------------------------------------------------------------
    tab_2024 = tabela[tabela["Ano"] == 2024].copy()
    tab_2025 = tabela[tabela["Ano"] == 2025].copy()

    # Calcular resultado e variação
    tab_2024["Resultado"] = tab_2024["Faturamento"] - tab_2024["Despesa"]
    tab_2024["Variação %"] = (tab_2024["Resultado"] / tab_2024["Faturamento"]) * 100

    tab_2025["Resultado"] = tab_2025["Faturamento"] - tab_2025["Despesa"]
    tab_2025["Variação %"] = (tab_2025["Resultado"] / tab_2025["Faturamento"]) * 100

    # ------------------------------------------------------------
    # 6) ADICIONAR TOTAIS DAS TABELAS
    # ------------------------------------------------------------
    total_2024 = pd.DataFrame({
        "Mês": ["TOTAL 2024"],
        "Faturamento": [tab_2024["Faturamento"].sum()],
        "Despesa": [tab_2024["Despesa"].sum()],
        "Resultado": [tab_2024["Resultado"].sum()],
        "Variação %": [(tab_2024["Resultado"].sum() / tab_2024["Faturamento"].sum()) * 100]
    })

    total_2025 = pd.DataFrame({
        "Mês": ["TOTAL 2025"],
        "Faturamento": [tab_2025["Faturamento"].sum()],
        "Despesa": [tab_2025["Despesa"].sum()],
        "Resultado": [tab_2025["Resultado"].sum()],
        "Variação %": [(tab_2025["Resultado"].sum() / tab_2025["Faturamento"].sum()) * 100]
    })

    tab_2024 = pd.concat([tab_2024, total_2024], ignore_index=True)
    tab_2025 = pd.concat([tab_2025, total_2025], ignore_index=True)

    # ------------------------------------------------------------
    # 7) FORMATAR TABELAS
    # ------------------------------------------------------------
    def fmt(df):
        df = df.copy()
        df["Faturamento"] = df["Faturamento"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))
        df["Despesa"] = df["Despesa"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))
        df["Resultado"] = df["Resultado"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "."))
        df["Variação %"] = df["Variação %"].apply(lambda x: f"{x:.1f}%")
        return df

    st.subheader("📄 Tabela 2024")
    st.dataframe(fmt(tab_2024), use_container_width=True)

    st.subheader("📄 Tabela 2025")
    st.dataframe(fmt(tab_2025), use_container_width=True)

    # ------------------------------------------------------------
    # 8) GRÁFICO — OPÇÃO 2 (EIXO DUPLO: FAT/DESP + RESULTADO)
    # ------------------------------------------------------------
    st.subheader("📊 Faturamento, Despesas e Resultado – Gráfico Comparativo")

    graf = tabela.sort_values("Mês_num")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Faturamento
    fig.add_trace(
        go.Bar(x=graf["Mês"], y=graf[graf["Ano"] == 2024]["Faturamento"], name="Fat 2024", marker_color="#005BBB")
    )
    fig.add_trace(
        go.Bar(x=graf["Mês"], y=graf[graf["Ano"] == 2025]["Faturamento"], name="Fat 2025", marker_color="#00A6FF")
    )

    # Despesas
    fig.add_trace(
        go.Bar(x=graf["Mês"], y=graf[graf["Ano"] == 2024]["Despesa"], name="Desp 2024", marker_color="#FF8C00")
    )
    fig.add_trace(
        go.Bar(x=graf["Mês"], y=graf[graf["Ano"] == 2025]["Despesa"], name="Desp 2025", marker_color="#FFC04D")
    )

    # Resultado (linha)
    fig.add_trace(
        go.Scatter(
            x=graf[graf["Ano"] == 2024]["Mês"],
            y=graf[graf["Ano"] == 2024]["Faturamento"] - graf[graf["Ano"] == 2024]["Despesa"],
            name="Res 2024",
            mode="lines+markers",
            line=dict(color="green", width=3)
        ),
        secondary_y=True
    )

    fig.add_trace(
        go.Scatter(
            x=graf[graf["Ano"] == 2025]["Mês"],
            y=graf[graf["Ano"] == 2025]["Faturamento"] - graf[graf["Ano"] == 2025]["Despesa"],
            name="Res 2025",
            mode="lines+markers",
            line=dict(color="darkgreen", width=3, dash="dot")
        ),
        secondary_y=True
    )

    fig.update_layout(
        height=600,
        barmode="group",
        title="Comparativo Geral – Faturamento, Despesas e Resultado",
        xaxis_title="Mês",
        legend_title="Legenda"
    )

    fig.update_yaxes(title_text="Receita / Despesa (R$)", secondary_y=False)
    fig.update_yaxes(title_text="Resultado (R$)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

