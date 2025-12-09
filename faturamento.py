import streamlit as st
import pandas as pd
import plotly.express as px

st.header("📊 Dashboard Financeiro – Comparativo 2024 x 2025")

uploaded_file = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])

if uploaded_file:

    # ============================
    # CARREGAR PLANILHA
    # ============================
    df = pd.read_excel(uploaded_file)

    # Nome das colunas deve seguir o seu padrão:
    # "Ano", "Mês", "Valor"
    df["Ano"] = df["Ano"].astype(int)

    # Separar 2024 e 2025
    df_2024 = df[df["Ano"] == 2024]
    df_2025 = df[df["Ano"] == 2025]

    total_2024 = df_2024["Valor"].sum()
    total_2025 = df_2025["Valor"].sum()

    # ============================
    # MOSTRAR RESUMO ANUAL
    # ============================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ano 2024")
        st.metric("Total Faturado", f"R$ {total_2024:,.0f}".replace(",", "."))
    
    with col2:
        st.subheader("Ano 2025")
        st.metric("Total Faturado", f"R$ {total_2025:,.0f}".replace(",", "."))

    # ============================
    # PREPARAR DADOS MENSALIZADOS
    # ============================
    pivot = df.pivot_table(values="Valor", index="Mês", columns="Ano", aggfunc="sum")

    # Garantir ordem correta dos meses
    ordem_meses = [
        "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
        "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
        "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
    ]
    pivot = pivot.reindex(ordem_meses)

    pivot = pivot.reset_index()

    # ============================
    # GRÁFICO COMPARATIVO
    # ============================
    st.subheader("📈 Comparativo Mensal")

    graf = px.bar(
        pivot,
        x="Mês",
        y=[2024, 2025],
        barmode="group",
        text_auto=".2s",
        labels={"value": "Faturamento - Valor", "Mês": "Mês", "variable": "Ano"}
    )
    st.plotly_chart(graf, use_container_width=True)

    # ============================
    # CRIAR TABELA COM DIFERENÇAS
    # ============================

    tabela = pivot.copy()
    tabela = tabela.rename(columns={2024: "Valor_2024", 2025: "Valor_2025"})

    # Diferença em R$
    tabela["Diferença (R$)"] = tabela["Valor_2025"] - tabela["Valor_2024"]

    # Diferença em %
    tabela["Diferença (%)"] = (tabela["Diferença (R$)"] / tabela["Valor_2024"]) * 100

    # Formatação final
    tabela_formatada = tabela.copy()

    tabela_formatada["Valor_2024"] = tabela["Valor_2024"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    tabela_formatada["Valor_2025"] = tabela["Valor_2025"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    tabela_formatada["Diferença (R$)"] = tabela["Diferença (R$)"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    tabela_formatada["Diferença (%)"] = tabela["Diferença (%)"].apply(
        lambda x: f"{x:.2f}%"
    )

    # ============================
    # MOSTRAR TABELA FINAL
    # ============================
    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela_formatada, use_container_width=True)
