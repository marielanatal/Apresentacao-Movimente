import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # ============ 1) Carregar planilhas ============
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # ============ 2) Ajustar colunas ============
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_desp["ANO"] = df_desp["ANO"].astype(int)

    df_fat["MES_NUM"] = df_fat["Mês"].str[:2].astype(int)
    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # ============ 3) Totais por ano ============
    fat_ano = df_fat.groupby("Ano")["Faturamento - Valor"].sum()
    desp_ano = df_desp.groupby("ANO")["VALOR"].sum()

    fat24 = fat_ano.get(2024, 0)
    fat25 = fat_ano.get(2025, 0)
    desp24 = desp_ano.get(2024, 0)
    desp25 = desp_ano.get(2025, 0)

    res24 = fat24 - desp24
    res25 = fat25 - desp25

    # ============ 4) Função para cards ============
    def card(titulo, valor, cor):
        html = f"""
        <div style="
            background:{cor};
            padding:12px 16px;
            border-radius:10px;
            color:white;
            font-weight:600;
            box-shadow:0 2px 6px rgba(0,0,0,0.15);
            margin-bottom:10px;">
            
            <div style="font-size:15px; opacity:0.85;">
                {titulo}
            </div>

            <div style="font-size:22px; font-weight:700; margin-top:4px;">
                R$ {valor:,.0f}
            </div>

        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    # ============ 5) CARDS EM 3 COLUNAS ============
    st.subheader("📌 Visão Geral do Ano")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔵 2024")
        card("💰 Faturamento", fat24, "#005BBB")
        card("📉 Despesas", desp24, "#B30000")
        card("📊 Resultado", res24, "#1E7B34")

    with col2:
        st.markdown("### 🟣 2025")
        card("💰 Faturamento", fat25, "#6A0DAD")
        card("📉 Despesas", desp25, "#8A0000")
        card("📊 Resultado", res25, "#2D8F4E")

    with col3:
        st.markdown("### 📈 Diferença")
        card("Crescimento Faturamento", fat25 - fat24, "#0F6CBD")
        card("Crescimento Resultado", res25 - res24, "#0F8F6C")

    # ============ 6) Tabelas — NÃO ALTERADAS ============
    st.subheader("📄 Tabelas Comparativas (Mensal)")

    tabela_fat = df_fat.pivot_table(index="Mês", columns="Ano",
                                    values="Faturamento - Valor", aggfunc="sum").reset_index()
    st.markdown("### 📘 Faturamento Mensal")
    st.dataframe(tabela_fat, use_container_width=True)

    tabela_desp = df_desp.pivot_table(index="MÊS", columns="ANO",
                                      values="VALOR", aggfunc="sum").reset_index()
    st.markdown("### 📕 Despesas Mensais")
    st.dataframe(tabela_desp, use_container_width=True)

    tabela_res = pd.DataFrame({
        "Mês": tabela_fat["Mês"],
        "Fat 2024": tabela_fat.get(2024, 0),
        "Desp 2024": tabela_desp.get(2024, 0),
        "Res 2024": tabela_fat.get(2024, 0) - tabela_desp.get(2024, 0),
        "Fat 2025": tabela_fat.get(2025, 0),
        "Desp 2025": tabela_desp.get(2025, 0),
        "Res 2025": tabela_fat.get(2025, 0) - tabela_desp.get(2025, 0),
    })

    st.markdown("### 📗 Resultado Mensal")
    st.dataframe(tabela_res, use_container_width=True)

