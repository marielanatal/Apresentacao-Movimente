import streamlit as st
import pandas as pd
import plotly.express as px

def render():
    st.header("📊 Comparativo 2024 x 2025 – Faturamento, Despesas e Margem")

    fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    desp = pd.read_excel("despesas_2024_2025.xlsx")

    fat = fat.rename(columns=lambda x: x.upper())
    desp = desp.rename(columns=lambda x: x.upper())

    fat["MES_NUM"] = fat["MÊS"].str[:2].astype(int)
    desp["MES_NUM"] = desp["MÊS"].str[:2].astype(int)

    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    fat_group = fat.groupby(["ANO","MES_NUM"])["FATURAMENTO - VALOR"].sum().reset_index()
    desp_group = desp.groupby(["ANO","MES_NUM"])["VALOR"].sum().reset_index()

    meses = list(range(1,13))
    tabela = pd.DataFrame({"Mês": meses})

    f24 = fat_group[fat_group["ANO"]==2024].set_index("MES_NUM")["FATURAMENTO - VALOR"]
    f25 = fat_group[fat_group["ANO"]==2025].set_index("MES_NUM")["FATURAMENTO - VALOR"]

    d24 = desp_group[desp_group["ANO"]==2024].set_index("MES_NUM")["VALOR"]
    d25 = desp_group[desp_group["ANO"]==2025].set_index("MES_NUM")["VALOR"]

    tabela["Fat 2024"] = tabela["Mês"].map(f24).fillna(0)
    tabela["Fat 2025"] = tabela["Mês"].map(f25).fillna(0)
    tabela["Desp 2024"] = tabela["Mês"].map(d24).fillna(0)
    tabela["Desp 2025"] = tabela["Mês"].map(d25).fillna(0)

    tabela["Var R$"] = tabela["Fat 2025"] - tabela["Fat 2024"]
    tabela["Var %"] = tabela["Var R$"] / tabela["Fat 2024"].replace(0, pd.NA) * 100

    tabela["Margem 2024"] = (1 - tabela["Desp 2024"]/tabela["Fat 2024"].replace(0,pd.NA)) * 100
    tabela["Margem 2025"] = (1 - tabela["Desp 2025"]/tabela["Fat 2025"].replace(0,pd.NA)) * 100

    st.subheader("📄 Tabela Comparativa")
    st.dataframe(tabela, use_container_width=True)

    st.subheader("📈 Faturamento")
    st.line_chart(tabela[["Fat 2024","Fat 2025"]])

    st.subheader("💸 Despesas")
    st.line_chart(tabela[["Desp 2024","Desp 2025"]])

    st.subheader("📉 Margem (%)")
    st.line_chart(tabela[["Margem 2024","Margem 2025"]])
