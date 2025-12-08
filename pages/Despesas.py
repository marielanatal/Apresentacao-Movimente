import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Despesas – 2024 e 2025", layout="wide")

st.title("💸 Dashboard de Despesas – 2024 x 2025")

# ==============================
# 1. Upload do arquivo
# ==============================
uploaded_file = st.file_uploader("Envie a planilha de despesas (xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ==============================
    # 2. Padronizar colunas
    # ==============================
    df.columns = [col.strip().upper() for col in df.columns]

    # Ajuste da coluna ANO
    if "ANO" not in df.columns:
        st.error("A coluna 'ANO' não foi encontrada na planilha!")
        st.stop()

    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")

    # Ajuste da coluna MÊS
    if "MÊS" not in df.columns:
        st.error("A coluna 'MÊS' não foi encontrada na planilha!")
        st.stop()

    # Ajuste da coluna VALOR
    if "VALOR" not in df.columns:
        st.error("A coluna 'VALOR' não foi encontrada na planilha!")
        st.stop()

    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

    # ==============================
    # 3. Tabela dinâmica (despesas por mês x ano)
    # ==============================
    tabela = df.pivot_table(
        values="VALOR",
        index="MÊS",
        columns="ANO",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    st.subheader("📊 Tabela Resumo por Mês")
    st.dataframe(tabela.style.format("{:,.2f}"))

    # ==============================
    # 4. Gráfico comparativo lado a lado
    # ==============================
    tabela_melt = tabela.melt(id_vars="MÊS", var_name="Ano", value_name="Valor")

    fig = px.bar(
        tabela_melt,
        x="MÊS",
        y="Valor",
        color="Ano",
        barmode="group",
        text="Valor",
        color_discrete_sequence=["darkorange", "royalblue"],
        title="Comparativo de Despesas – 2024 x 2025 (Lado a Lado)"
    )

    # Aumenta o tamanho dos números e formata como moeda
    fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside",
        textfont_size=16
    )

    fig.update_layout(
        yaxis_title="Valor (R$)",
        xaxis_title="Mês",
        bargap=0.25,
        title_font_size=24
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📌 Envie o arquivo **despesas_2024_2025.xlsx** para visualizar o dashboard.")

