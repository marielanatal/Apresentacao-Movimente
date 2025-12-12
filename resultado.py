import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Comparativo Faturamento, Despesas e Resultado")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # =============================
    # 2) AJUSTAR COLUNAS
    # =============================
    df_fat.columns = df_fat.columns.str.strip()
    df_desp.columns = df_desp.columns.str.strip()

    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_desp["ANO"] = df_desp["ANO"].astype(int)

    df_fat["MES_NUM"] = df_fat["Mês"].str[:2].astype(int)
    df_desp["MES_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # =============================
    # 3) AGRUPAMENTOS
    # =============================
    fat_ano = df_fat.groupby("Ano")["Faturamento - Valor"].sum()
    desp_ano = df_desp.groupby("ANO")["VALOR"].sum()

    total_fat_24 = fat_ano.get(2024, 0)
    total_fat_25 = fat_ano.get(2025, 0)
    total_desp_24 = desp_ano.get(2024, 0)
    total_desp_25 = desp_ano.get(2025, 0)

    total_res_24 = total_fat_24 - total_desp_24
    total_res_25 = total_fat_25 - total_desp_25

    # =============================
    # 4) FUNÇÃO PARA CARDS CORPORATIVOS
    # =============================
    def card_pequeno(titulo, valor, cor_fundo, icone=""):
        return f"""
            <div style="
                background-color:{cor_fundo};
                padding:14px 18px;
                border-radius:10px;
                color:white;
                font-size:16px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                margin-bottom:8px;">
                
                <div style="font-weight:600; opacity:0.85;">
                    {icone} {titulo}
                </div>

                <div style="font-size:22px; font-weight:700; margin-top:6px;">
                    R$ {valor:,.0f}
                </div>
            </div>
        """

    # =============================
    # 5) CARDS EM 3 COLUNAS
    # =============================
    st.markdown("## 📌 Visão Geral do Ano")

    colA, colB, colC = st.columns(3)

    # --- COLUNA 2024 ---
    with colA:
        st.markdown("### 🔵 2024")
        st.markdown(card_pequeno("Faturamento", total_fat_24, "#005BBB", "💰"), unsafe_allow_html=True)
        st.markdown(card_pequeno("Despesas", total_desp_24, "#B30000", "📉"), unsafe_allow_html=True)
        st.markdown(card_pequeno("Resultado", total_res_24, "#1E7B34", "📊"), unsafe_allow_html=True)

    # --- COLUNA 2025 ---
    with colB:
        st.markdown("### 🟣 2025")
        st.markdown(card_pequeno("Faturamento", total_fat_25, "#6A0DAD", "💰"), unsafe_allow_html=True)
        st.markdown(card_pequeno("Despesas", total_desp_25, "#900000", "📉"), unsafe_allow_html=True)
        st.markdown(card_pequeno("Resultado", total_res_25, "#2D8F4E", "📊"), unsafe_allow_html=True)

    # --- DIFERENÇAS ---
    with colC:
        st.markdown("### 📈 Diferença")
        st.markdown(card_pequeno("Crescimento Faturamento", total_fat_25 - total_fat_24, "#0F6CBD", "📈"), unsafe_allow_html=True)
        st.markdown(card_pequeno("Crescimento Resultado", total_res_25 - total_res_24, "#0F8F6C", "📈"), unsafe_allow_html=True)

    # =============================
    # 6) TABELAS MENSAL (igual estava antes)
    # =============================
    st.subheader("📄 Tabelas Comparativas")

    # --- Faturamento Mensal ---
    tabela_fat = df_fat.pivot_table(index="Mês", columns="Ano", values="Faturamento - Valor", aggfunc="sum").reset_index()
    st.markdown("### 📘 Faturamento Mensal")
    st.dataframe(tabela_fat, use_container_width=True)

    # --- Despesas Mensais ---
    tabela_desp = df_desp.pivot_table(index="MÊS", columns="ANO", values="VALOR", aggfunc="sum").reset_index()
    st.markdown("### 📕 Despesas Mensais")
    st.dataframe(tabela_desp, use_container_width=True)

    # --- Resultado Mensal ---
    tabela_res = pd.DataFrame({
        "Mês": tabela_fat["Mês"],
        "Faturamento 2024": tabela_fat.get(2024, 0),
        "Despesas 2024": tabela_desp.get(2024, 0),
        "Resultado 2024": tabela_fat.get(2024, 0) - tabela_desp.get(2024, 0),
        "Faturamento 2025": tabela_fat.get(2025, 0),
        "Despesas 2025": tabela_desp.get(2025, 0),
        "Resultado 2025": tabela_fat.get(2025, 0) - tabela_desp.get(2025, 0),
    })

    st.markdown("### 📗 Resultado Mensal")
    st.dataframe(tabela_res, use_container_width=True)

