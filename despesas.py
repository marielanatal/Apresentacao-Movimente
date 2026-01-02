import streamlit as st
import pandas as pd
import plotly.express as px

def render():
    st.header("💰 Dashboard de Despesas – 2024 x 2025")
    st.markdown("---")

    # ---------------------------------------------------------
    # 1. Carregar arquivo automaticamente
    # ---------------------------------------------------------
    FILE_PATH = "despesas_2024_2025.xlsx"
    df = pd.read_excel(FILE_PATH)

    # ---------------------------------------------------------
    # 2. Padronizar colunas
    # ---------------------------------------------------------
    df.columns = df.columns.str.upper().str.replace(" ", "_")

    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype(int)
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

    # Formatação de moeda
    def fmt_real(v):
        return f"R$ {v:,.2f}".replace(",", ".")

    # ---------------------------------------------------------
    # 3. Cards Resumo
    # ---------------------------------------------------------
    total_2024 = df[df["ANO"] == 2024]["VALOR"].sum()
    total_2025 = df[df["ANO"] == 2025]["VALOR"].sum()

    dif_percentual = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💸 Total 2024", fmt_real(total_2024))
    col2.metric("💸 Total 2025", fmt_real(total_2025))
    col3.metric("📉 Diferença %", f"{dif_percentual:.1f}%")

    st.markdown("---")

    # ---------------------------------------------------------
    # 4. Despesas por categoria (RAIZ PRINCIPAL)
    # ---------------------------------------------------------
    st.subheader("🏷️ Despesas por Categoria")

    g1 = df.groupby("RAIZ_PRINCIPAL")["VALOR"].sum().reset_index()
    g1["VALOR_FMT"] = g1["VALOR"].apply(fmt_real)

    fig1 = px.bar(
        g1,
        x="VALOR",
        y="RAIZ_PRINCIPAL",
        orientation="h",
        text="VALOR_FMT",
        color="RAIZ_PRINCIPAL",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig1.update_traces(
        textposition="outside",
        textfont_size=14
    )

    fig1.update_layout(
        xaxis_title="Despesas (R$)",
        showlegend=False,
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 5. Top 10 fornecedores
    # ---------------------------------------------------------
    st.subheader("🏆 Top 10 Fornecedores por Gasto")

    top = (
        df.groupby("EMPRESA/PESSOA")["VALOR"]
        .sum()
        .reset_index()
        .sort_values(by="VALOR", ascending=False)
        .head(10)
    )

    top["VALOR"] = top["VALOR"].apply(fmt_real)

    st.dataframe(top, hide_index=True, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 6. Resumo mensal por ano
    # ---------------------------------------------------------
    st.subheader("📊 Resumo Mensal por Ano")

    resumo = df.pivot_table(
        values="VALOR",
        index="MÊS",
        columns="ANO",
        aggfunc="sum",
        fill_value=0
    )

    # Ordenar meses
    ordem_meses = [
        "01 - JANEIRO", "02 - FEVEREIRO", "03 - MARÇO", "04 - ABRIL",
        "05 - MAIO", "06 - JUNHO", "07 - JULHO", "08 - AGOSTO",
        "09 - SETEMBRO", "10 - OUTUBRO", "11 - NOVEMBRO", "12 - DEZEMBRO"
    ]
    resumo = resumo.reindex(ordem_meses)

    # Diferenças
    anos = resumo.columns.tolist()
    if len(anos) == 2:
        ano_antigo, ano_recente = anos[0], anos[1]
        resumo["DIFERENÇA (R$)"] = resumo[ano_recente] - resumo[ano_antigo]
        resumo["VARIAÇÃO (%)"] = (resumo["DIFERENÇA (R$)"] / resumo[ano_antigo] * 100).replace([float('inf'), -float('inf')], 0)
    else:
        resumo["DIFERENÇA (R$)"] = 0
        resumo["VARIAÇÃO (%)"] = 0

    # Formatar tabela
    resumo_fmt = resumo.copy()

    for col in anos + ["DIFERENÇA (R$)"]:
        resumo_fmt[col] = resumo_fmt[col].apply(fmt_real)

    resumo_fmt["VARIAÇÃO (%)"] = resumo_fmt["VARIAÇÃO (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(resumo_fmt, use_container_width=True)

