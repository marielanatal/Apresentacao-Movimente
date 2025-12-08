import streamlit as st
import pandas as pd
import plotly.express as px
import os

def render():

    st.title("💰 Dashboard de Despesas – 2024 x 2025")
    st.markdown("---")

    FILE_PATH = "./despesas_2024_2025.xlsx"

    if not os.path.exists(FILE_PATH):
        st.error(f"❌ Arquivo não encontrado: {FILE_PATH}")
        st.stop()

    df = pd.read_excel(FILE_PATH)

    df.columns = df.columns.str.upper().str.replace(" ", "_")
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype(int)
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

    total_2024 = df[df["ANO"] == 2024]["VALOR"].sum()
    total_2025 = df[df["ANO"] == 2025]["VALOR"].sum()

    dif_percentual = 0
    if total_2024 > 0:
        dif_percentual = ((total_2025 - total_2024) / total_2024) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💸 Total 2024", f"R$ {total_2024:,.0f}".replace(",", "."))
    col2.metric("💸 Total 2025", f"R$ {total_2025:,.0f}".replace(",", "."))
    col3.metric("📉 Diferença % (25 vs 24)", f"{dif_percentual:.1f}%")
    col4.metric("📊 Média Mensal (Geral)", f"R$ {df['VALOR'].mean():,.0f}".replace(",", "."))

    st.markdown("---")

    st.subheader("🏷️ Despesas por Categoria (RAIZ_PRINCIPAL)")

    g1 = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().reset_index()

    fig1 = px.bar(
        g1,
        x="VALOR",
        y="RAIZ_PRINCIPAL",
        orientation="h",
        text=g1["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".")),
        color="RAIZ_PRINCIPAL",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig1.update_traces(textposition="outside", textfont_size=14)
    fig1.update_layout(height=500, showlegend=False)

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    st.subheader("🏆 Top 10 Fornecedores por Gasto")

    top = (
        df.groupby("EMPRESA/PESSOA")["VALOR"]
        .sum()
        .reset_index()
        .sort_values(by="VALOR", ascending=False)
        .head(10)
    )

    top["VALOR"] = top["VALOR"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    st.dataframe(top, hide_index=True)

    st.markdown("---")

    st.subheader("📊 Resumo Mensal por Ano")

    resumo = df.pivot_table(
        values="VALOR",
        index="MÊS",
        columns="ANO",
        aggfunc="sum",
        fill_value=0
    )

    ordem_meses = [
        "01 - JANEIRO", "02 - FEVEREIRO", "03 - MARÇO", "04 - ABRIL",
        "05 - MAIO", "06 - JUNHO", "07 - JULHO", "08 - AGOSTO",
        "09 - SETEMBRO", "10 - OUTUBRO", "11 - NOVEMBRO", "12 - DEZEMBRO"
    ]
    resumo = resumo.reindex(ordem_meses)

    anos = resumo.columns.tolist()
    if len(anos) == 2:
        ano_antigo, ano_recente = anos[0], anos[1]
        resumo["DIFERENÇA (R$)"] = resumo[ano_recente] - resumo[ano_antigo]
        resumo["VARIAÇÃO (%)"] = (resumo["DIFERENÇA (R$)"] / resumo[ano_antigo]) * 100
    else:
        resumo["DIFERENÇA (R$)"] = 0
        resumo["VARIAÇÃO (%)"] = 0

    resumo_formatado = resumo.copy()

    for col in resumo.columns:
        if col in anos or col == "DIFERENÇA (R$)":
            resumo_formatado[col] = resumo[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
        elif col == "VARIAÇÃO (%)":
            resumo_formatado[col] = resumo[col].apply(lambda x: f"{x:.1f}%")

    st.dataframe(resumo_formatado, use_container_width=True)

