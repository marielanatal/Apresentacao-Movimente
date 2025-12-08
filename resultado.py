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

    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 3) AGRUPAR FATURAMENTO E DESPESAS
    # =============================
    fat_group = fat.groupby(["ANO", "MÊS"])["FATURAMENTO - VALOR"].sum().reset_index()
    desp_group = desp.groupby(["ANO", "MÊS"])["VALOR"].sum().reset_index()

    # =============================
    # 4) CRIAR BASE COM TODOS OS MESES POSSÍVEIS
    # =============================
    meses = sorted(list(fat_group["MÊS"].unique()))
    anos = [2024, 2025]

    base = pd.MultiIndex.from_product([anos, meses], names=["ANO", "MÊS"])
    base = pd.DataFrame(index=base).reset_index()

    # =============================
    # 5) JUNTAR DADOS E PREENCHER FALTANTES
    # =============================
    base = base.merge(fat_group, on=["ANO", "MÊS"], how="left")
    base = base.merge(desp_group, on=["ANO", "MÊS"], how="left")

    base.rename(columns={
        "FATURAMENTO - VALOR": "FATURAMENTO",
        "VALOR": "DESPESA"
    }, inplace=True)

    base["FATURAMENTO"] = base["FATURAMENTO"].fillna(0)
    base["DESPESA"] = base["DESPESA"].fillna(0)

    # =============================
    # 6) GERAR TABELA ANUAL LADO A LADO
    # =============================
    fat24 = base[base["ANO"] == 2024].set_index("MÊS")
    fat25 = base[base["ANO"] == 2025].set_index("MÊS")

    tabela = pd.DataFrame()
    tabela["Mês"] = meses

    tabela["Fat 2024"] = fat24["FATURAMENTO"].values
    tabela["Fat 2025"] = fat25["FATURAMENTO"].values

    tabela["Var R$"] = tabela["Fat 2025"] - tabela["Fat 2024"]
    tabela["Var %"] = (tabela["Var R$"] / tabela["Fat 2024"].replace(0, pd.NA)) * 100

    tabela["Desp 2024"] = fat24["DESPESA"].values
    tabela["Desp 2025"] = fat25["DESPESA"].values

    tabela["Margem 2024"] = (1 - (tabela["Desp 2024"] / tabela["Fat 2024"].replace(0, pd.NA))) * 100
    tabela["Margem 2025"] = (1 - (tabela["Desp 2025"] / tabela["Fat 2025"].replace(0, pd.NA))) * 100

    # =============================
    # 7) FORMATAR VISUALMENTE
    # =============================
    tabela_format = tabela.copy()

    for col in ["Fat 2024", "Fat 2025", "Var R$", "Desp 2024", "Desp 2025"]:
        tabela_format[col] = tabela_format[col].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    for col in ["Var %", "Margem 2024", "Margem 2025"]:
        tabela_format[col] = tabela_format[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")

    st.dataframe(tabela_format, use_container_width=True)


