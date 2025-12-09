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

    # Padronizar colunas
    fat.columns = fat.columns.str.upper()
    desp.columns = desp.columns.str.upper()

    # =============================
    # 2) CRIAR "MES_NUM" PARA GARANTIR JUNÇÃO SEGURA
    # =============================
    def extrair_mes_num(x):
        try:
            return int(str(x)[0:2])
        except:
            return None

    fat["MES_NUM"] = fat["MÊS"].apply(extrair_mes_num)
    desp["MES_NUM"] = desp["MÊS"].apply(extrair_mes_num)

    # Converter valores
    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 3) AGRUPAR FATURAMENTO & DESPESAS
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
    # 4) CRIAR TABELA FINAL COM TODOS OS MESES E ANOS
    # =============================
    meses = range(1, 13)
    anos = [2024, 2025]

    base = pd.MultiIndex.from_product([anos, meses], names=["ANO", "MES_NUM"])
    base = pd.DataFrame(index=base).reset_index()

    # =============================
    # 5) JUNTAR FATURAMENTO E DESPESA
    # =============================
    base = base.merge(fat_group, on=["ANO", "MES_NUM"], how="left")
    base = base.merge(desp_group, on=["ANO", "MES_NUM"], how="left")

    base["FATURAMENTO"] = base["FATURAMENTO"].fillna(0)
    base["DESPESA"] = base["DESPESA"].fillna(0)

    # =============================
    # 6) CRIAR TABELA YOY
    # =============================
    fat24 = base[base["ANO"] == 2024].set_index("MES_NUM")
    fat25 = base[base["ANO"] == 2025].set_index("MES_NUM")

    tabela = pd.DataFrame()
    tabela["Mês"] = fat24.index

    tabela["Fat 2024"] = fat24["FATURAMENTO"].values
    tabela["Fat 2025"] = fat25["FATURAMENTO"].values

    tabela["Var R$"] = tabela["Fat 2025"] - tabela["Fat 2024"]
    tabela["Var %"] = (tabela["Var R$"] / tabela["Fat 2024"].replace(0, pd.NA)) * 100

    tabela["Desp 2024"] = fat24["DESPESA"].values
    tabela["Desp 2025"] = fat25["DESPESA"].values

    tabela["Margem 2024"] = (1 - (tabela["Desp 2024"] / tabela["Fat 2024"].replace(0, pd.NA))) * 100
    tabela["Margem 2025"] = (1 - (tabela["Desp 2025"] / tabela["Fat 2025"].replace(0, pd.NA))) * 100

    # =============================
    # 7) FORMATAR VALORES
    # =============================
    def fmt_money(v):
        return f"R$ {v:,.0f}".replace(",", ".")

    def fmt_pct(v):
        return f"{v:.1f}%" if pd.notna(v) else "-"

    tabela_fmt = tabela.copy()
    for col in ["Fat 2024", "Fat 2025", "Var R$", "Desp 2024", "Desp 2025"]:
        tabela_fmt[col] = tabela_fmt[col].apply(fmt_money)

    for col in ["Var %", "Margem 2024", "Margem 2025"]:
        tabela_fmt[col] = tabela_fmt[col].apply(fmt_pct)

    # =============================
    # 8) EXIBIR
    # =============================
    st.dataframe(tabela_fmt, use_container_width=True)

