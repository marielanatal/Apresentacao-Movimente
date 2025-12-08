import streamlit as st
import pandas as pd

def render():

    st.header("📊 Comparativo Ano x Ano – Faturamento x Despesas x Margem")
    st.markdown("Comparação direta mês a mês entre 2024 e 2025.")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    desp = pd.read_excel("despesas_2024_2025.xlsx")

    # =============================
    # 2) PADRONIZAR COLUNAS
    # =============================
    fat.columns = fat.columns.str.upper()
    desp.columns = desp.columns.str.upper()

    fat["ANO"] = fat["ANO"].astype(int)
    desp["ANO"] = desp["ANO"].astype(int)

    fat["MÊS"] = fat["MÊS"].astype(str)
    desp["MÊS"] = desp["MÊS"].astype(str)

    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 3) AGRUPAR MÊS/ANO
    # =============================
    fat_group = fat.groupby(["ANO", "MÊS"])["FATURAMENTO - VALOR"].sum().reset_index()
    desp_group = desp.groupby(["ANO", "MÊS"])["VALOR"].sum().reset_index()

    # =============================
    # 4) JUNTAR FAT + DESPESAS
    # =============================
    base = pd.merge(fat_group, desp_group, on=["ANO", "MÊS"], how="outer")
    base.rename(columns={"VALOR": "DESPESA", "FATURAMENTO - VALOR": "FATURAMENTO"}, inplace=True)

    # Ordenação por mês (01, 02, 03…)
    base["MES_NUM"] = base["MÊS"].str[:2].astype(int)
    base = base.sort_values(["MES_NUM", "ANO"])

    # =============================
    # 5) SEPARAR 2024 E 2025
    # =============================
    fat24 = base[base["ANO"] == 2024].set_index("MÊS")[["FATURAMENTO", "DESPESA"]]
    fat25 = base[base["ANO"] == 2025].set_index("MÊS")[["FATURAMENTO", "DESPESA"]]

    # =============================
    # 6) JUNTAR LADO A LADO
    # =============================
    tabela = pd.DataFrame()
    tabela["Mês"] = fat24.index

    tabela["Fat 2024"] = fat24["FATURAMENTO"].values
    tabela["Fat 2025"] = fat25["FATURAMENTO"].values

    tabela["Var R$"] = tabela["Fat 2025"] - tabela["Fat 2024"]
    tabela["Var %"] = (tabela["Var R$"] / tabela["Fat 2024"]) * 100

    tabela["Desp 2024"] = fat24["DESPESA"].values
    tabela["Desp 2025"] = fat25["DESPESA"].values

    tabela["Margem 2024"] = (1 - (tabela["Desp 2024"] / tabela["Fat 2024"])) * 100
    tabela["Margem 2025"] = (1 - (tabela["Desp 2025"] / tabela["Fat 2025"])) * 100

    # =============================
    # 7) FORMATAR VISUAL
    # =============================
    tabela_formatada = tabela.copy()

    cols_moeda = ["Fat 2024", "Fat 2025", "Var R$", "Desp 2024", "Desp 2025"]
    cols_pct = ["Var %", "Margem 2024", "Margem 2025"]

    for col in cols_moeda:
        tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    for col in cols_pct:
        tabela_formatada[col] = tabela_formatada[col].apply(lambda x: f"{x:.1f}%")

    # =============================
    # 8) EXIBIR TABELA
    # =============================
    st.dataframe(tabela_formatada, use_container_width=True)


