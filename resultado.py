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

    # Padronizar meses (problema real corrigido)
    fat["MÊS"] = fat["MÊS"].str.upper().str.strip()
    desp["MÊS"] = desp["MÊS"].str.upper().str.strip()

    # Converter valores numéricos
    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 2) AGRUPAR DADOS
    # =============================
    fat_group = fat.groupby(["ANO", "MÊS"])["FATURAMENTO - VALOR"].sum().reset_index()
    desp_group = desp.groupby(["ANO", "MÊS"])["VALOR"].sum().reset_index()

    # =============================
    # 3) CRIAR TABELA BASE COM TODOS OS MESES
    # =============================
    meses = sorted(list(set(fat_group["MÊS"]).union(set(desp_group["MÊS"]))))

    base = pd.MultiIndex.from_product([[2024, 2025], meses], names=["ANO", "MÊS"])
    base = pd.DataFrame(index=base).reset_index()

    # =============================
    # 4) JUNTAR FATURAMENTO E DESPESAS
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
    # 5) SEPARAR ANOS
    # =============================
    fat24 = base[base["ANO"] == 2024].set_index("MÊS")
    fat25 = base[base["ANO"] == 2025].set_index("MÊS")

    # =============================
    # 6) MONTAR TABELA FINAL
    # =============================
   
