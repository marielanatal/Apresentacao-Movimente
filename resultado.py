import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📊 Resultado – Comparativo 2024 x 2025")
    st.markdown("Faturamento x Despesas x Margem por mês, separado por ano.")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    desp = pd.read_excel("despesas_2024_2025.xlsx")

    fat.columns = fat.columns.str.upper()
    desp.columns = desp.columns.str.upper()

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
    # 2) AGRUPAR DADOS
    # =============================
    fat_group = fat.groupby(["ANO", "MES_NUM"])["FATURAMENTO - VALOR"].sum().reset_index()
    fat_group = fat_group.rename(columns={"FATURAMENTO - VALOR": "FATURAMENTO"})

    desp_group = desp.groupby(["ANO", "MES_NUM"])["VALOR"].sum().reset_index()
    desp_group = desp_group.rename(columns={"VALOR": "DESPESA"})

    # =============================
    # 3) CRIAR BASE COMPLETA
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
    # 4) CONSTRUIR TABELAS POR ANO
    # =============================
    def montar_tabela(ano):
        df = base[base["ANO"] == ano].copy()
        df = df.sort_values("MES_NUM")

        df["RESULTADO"] = df["FATURAMENTO"] - df["DESPESA"]
        df["MARGEM"] = (df["RESULTADO"] / df["FATURAMENTO"].replace(0, pd.NA)) * 100

        # Totais
        total_fat = df["FATURAMENTO"].sum()
        total_desp = df["DESPESA"].sum()
        total_res = total_fat - total_desp
        margem_media = (df["RESULTADO"].sum() / df["FATURAMENTO"].sum()) * 100 if total_fat > 0 else 0

        total_row = pd.DataFrame({
            "MES_NUM": ["TOTAL"],
            "FATURAMENTO": [total_fat],
            "DESPESA": [total_desp],
            "RESULTADO": [total_res],
            "MARGEM": [margem_media]
        })

        df = pd.concat([df, total_row], ignore_index=True)

        # Formatadores
        def fmt_real(v):
            return f"R$ {v:,.2f}".replace(",", ".")

        def fmt_pct(v):
            return f"{v:.1f}%" if pd.notna(v) else "-"

        df_fmt = df.copy()

        for col in ["FATURAMENTO", "DESPESA", "RESULTADO"]:
            df_fmt[col] = df_fmt[col].apply(fmt_real)

        df_fmt["MARGEM"] = df["MARGEM"].apply(fmt_pct)

        df_fmt.rename(columns={
            "MES_NUM": "Mês",
            "FATURAMENTO": "Faturamento",
            "DESPESA": "Despesas",
            "RESULTADO": "Resultado",
            "MARGEM": "Margem (%)"
        }, inplace=True)

        return df_fmt

    # =============================
    # 5) EXIBIR TABELAS
    # =============================
    st.subheader("📘 Resultado 2024")
    tabela_2024 = montar_tabela(2024)
    st.dataframe(tabela_2024, use_container_width=True)

    st.subheader("📗 Resultado 2025")
    tabela_2025 = montar_tabela(2025)
    st.dataframe(tabela_2025, use_container_width=True)

    # =============================
    # 6) GRÁFICOS
    # =============================
    st.subheader("📈 Comparativo Faturamento, Despesas e Resultado")

    tabela_graf = base.copy()
    tabela_graf["RESULTADO"] = tabela_graf["FATURAMENTO"] - tabela_graf["DESPESA"]

    fig = px.line(
        tabela_graf,
        x="MES_NUM",
        y=["FATURAMENTO", "DESPESA", "RESULTADO"],
        color="ANO",
        markers=True,
        labels={"value": "R$", "MES_NUM": "Mês"},
        title="Linha do Resultado"
    )

    st.plotly_chart(fig, use_container_width=True)
