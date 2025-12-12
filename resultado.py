import streamlit as st
import pandas as pd
import plotly.express as px

def render():
    st.header("📊 Comparativo Ano x Ano – Faturamento x Despesas x Margem")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    desp = pd.read_excel("despesas_2024_2025.xlsx")

    # Padronizar colunas
    fat.columns = fat.columns.str.upper()
    desp.columns = desp.columns.str.upper()

    # =============================
    # 2) CRIAR "MES_NUM"
    # =============================
    fat["MES_NUM"] = fat["MÊS"].str[:2].astype(int)
    desp["MES_NUM"] = desp["MÊS"].str[:2].astype(int)

    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 3) AGRUPAMENTOS
    # =============================
    fat_group = (
        fat.groupby(["ANO", "MES_NUM"])["FATURAMENTO - VALOR"]
        .sum()
        .reset_index()
        .rename(columns={"FATURAMENTO - VALOR": "FATURAMENTO"})
    )

    desp_group = (
        desp.groupby(["ANO", "MES_NUM"])["VALOR"]
        .sum()
        .reset_index()
        .rename(columns={"VALOR": "DESPESA"})
    )

    # =============================
    # 4) CRIAR BASE
    # =============================
    meses = range(1, 13)
    anos = [2024, 2025]

    base = pd.MultiIndex.from_product([anos, meses], names=["ANO", "MES_NUM"])
    base = pd.DataFrame(index=base).reset_index()

    base = base.merge(fat_group, on=["ANO", "MES_NUM"], how="left")
    base = base.merge(desp_group, on=["ANO", "MES_NUM"], how="left")

    base["FATURAMENTO"] = base["FATURAMENTO"].fillna(0)
    base["DESPESA"] = base["DESPESA"].fillna(0)

    # =============================
    # 5) SEPARAR ANOS
    # =============================
    fat24 = base[base["ANO"] == 2024].set_index("MES_NUM")
    fat25 = base[base["ANO"] == 2025].set_index("MES_NUM")

    # =============================
    # 6) CRIAR TABELA YOY
    # =============================
    tabela = pd.DataFrame()
    tabela["Mês"] = list(meses)

    tabela["Fat 2024"] = fat24["FATURAMENTO"].values
    tabela["Fat 2025"] = fat25["FATURAMENTO"].values

    tabela["Desp 2024"] = fat24["DESPESA"].values
    tabela["Desp 2025"] = fat25["DESPESA"].values

    tabela["Res 2024"] = tabela["Fat 2024"] - tabela["Desp 2024"]
    tabela["Res 2025"] = tabela["Fat 2025"] - tabela["Desp 2025"]

    tabela["Margem 2024"] = (tabela["Res 2024"] / tabela["Fat 2024"].replace(0, pd.NA)) * 100
    tabela["Margem 2025"] = (tabela["Res 2025"] / tabela["Fat 2025"].replace(0, pd.NA)) * 100

    # =============================
    # 7) SOMATÓRIO PARA CARDS
    # =============================
    total_fat_24 = tabela["Fat 2024"].sum()
    total_fat_25 = tabela["Fat 2025"].sum()

    total_desp_24 = tabela["Desp 2024"].sum()
    total_desp_25 = tabela["Desp 2025"].sum()

    total_res_24 = total_fat_24 - total_desp_24
    total_res_25 = total_fat_25 - total_desp_25

    # =============================
# 8) CARDS CORPORATIVOS – VERSÃO COMPACTA
# =============================

st.markdown("## 📌 Visão Geral do Ano")

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
    # 9) TABELA FINAL (SEM ALTERAÇÕES)
    # =============================
    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela, use_container_width=True)

    # =============================
    # 10) GRÁFICOS
    # =============================
    st.subheader("📈 Faturamento – 2024 x 2025")
    st.line_chart(tabela[["Fat 2024", "Fat 2025"]])

    st.subheader("💸 Despesas – 2024 x 2025")
    st.line_chart(tabela[["Desp 2024", "Desp 2025"]])

    st.subheader("📉 Resultado – 2024 x 2025")
    st.line_chart(tabela[["Res 2024", "Res 2025"]])
