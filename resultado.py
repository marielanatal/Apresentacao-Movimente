import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Resultado – Comparativo 2024 x 2025")
    st.markdown("Faturamento x Despesas x Margem por mês.")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    desp = pd.read_excel("despesas_2024_2025.xlsx")

    # Padronizar colunas
    fat.columns = fat.columns.str.upper()
    desp.columns = desp.columns.str.upper()

    # =============================
    # 2) EXTRAIR MÊS
    # =============================
    def extrair_mes_num(x):
        try:
            return int(str(x)[:2])
        except:
            return None

    fat["MES_NUM"] = fat["MÊS"].apply(extrair_mes_num)
    desp["MES_NUM"] = desp["MÊS"].apply(extrair_mes_num)

    fat["FATURAMENTO - VALOR"] = pd.to_numeric(fat["FATURAMENTO - VALOR"], errors="coerce")
    desp["VALOR"] = pd.to_numeric(desp["VALOR"], errors="coerce")

    # =============================
    # 3) AGRUPAR
    # =============================
    fat_group = fat.groupby(["ANO", "MES_NUM"])["FATURAMENTO - VALOR"].sum().reset_index()
    fat_group = fat_group.rename(columns={"FATURAMENTO - VALOR": "FATURAMENTO"})

    desp_group = desp.groupby(["ANO", "MES_NUM"])["VALOR"].sum().reset_index()
    desp_group = desp_group.rename(columns={"VALOR": "DESPESA"})

    # =============================
    # 4) CRIAR BASE DE MESES
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
    # 6) MONTAR TABELA NUMÉRICA
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

    tabela["Dif R$"] = tabela["Res 2025"] - tabela["Res 2024"]
    tabela["Dif %"] = (tabela["Dif R$"] / tabela["Res 2024"].replace(0, pd.NA)) * 100

    # =============================
    # 7) FORMATAR PARA EXIBIÇÃO (SEM QUEBRAR GRÁFICOS)
    # =============================
    def fmt_real(v):
        return f"R$ {v:,.2f}".replace(",", ".")

    def fmt_pct(v):
        return f"{v:.1f}%" if pd.notna(v) else "-"

    tabela_fmt = tabela.copy()

    for col in ["Fat 2024", "Fat 2025", "Desp 2024", "Desp 2025", "Res 2024", "Res 2025", "Dif R$"]:
        tabela_fmt[col] = tabela_fmt[col].apply(fmt_real)

    for col in ["Margem 2024", "Margem 2025", "Dif %"]:
        tabela_fmt[col] = tabela_fmt[col].apply(fmt_pct)

    # =============================
    # 8) MOSTRAR TABELA
    # =============================
    st.subheader("📄 Tabela Comparativa de Resultados")
    st.dataframe(tabela_fmt, use_container_width=True)

    # =============================
    # 9) GRÁFICOS (USAM A TABELA NUMÉRICA)
    # =============================

    tabela_graf = tabela.copy()

    # Margens precisam ser numéricas
    tabela_graf["Margem 2024"] = pd.to_numeric(tabela_graf["Margem 2024"], errors="coerce")
    tabela_graf["Margem 2025"] = pd.to_numeric(tabela_graf["Margem 2025"], errors="coerce")

    # ---- FATURAMENTO ----
    st.subheader("📈 Faturamento – 2024 x 2025")

    fig_fat = px.line(
        tabela_graf,
        x="Mês",
        y=["Fat 2024", "Fat 2025"],
        markers=True,
        labels={"value": "R$"}
    )
    st.plotly_chart(fig_fat, use_container_width=True)

    # ---- DESPESAS ----
    st.subheader("💸 Despesas – 2024 x 2025")

    fig_desp = px.line(
        tabela_graf,
        x="Mês",
        y=["Desp 2024", "Desp 2025"],
        markers=True,
        labels={"value": "R$"}
    )
    st.plotly_chart(fig_desp, use_container_width=True)

    # ---- MARGEM ----
    st.subheader("📉 Margem (%) – 2024 x 2025")

    fig_margem = px.line(
        tabela_graf,
        x="Mês",
        y=["Margem 2024", "Margem 2025"],
        markers=True,
        labels={"value": "%"}
    )
    st.plotly_chart(fig_margem, use_container_width=True)


