import streamlit as st
import pandas as pd
import plotly.express as px

def render():

    st.header("📈 Comparativo Faturamento, Despesas e Resultado")

    # =============================
    # 1) CARREGAR PLANILHAS
    # =============================
    df_fat = pd.read_excel("Consolidado de Faturamento - 2024 e 2025.xlsx")
    df_desp = pd.read_excel("despesas_2024_2025.xlsx")

    # =============================
    # 2) PADRONIZAR NOMES
    # =============================
    df_fat.columns = df_fat.columns.astype(str).str.strip()
    df_desp.columns = df_desp.columns.astype(str).str.strip()

    # =============================
    # 3) AJUSTAR FATURAMENTO
    # =============================
    df_fat["Ano"] = df_fat["Ano"].astype(int)
    df_fat["MÊS_NUM"] = df_fat["Mês"].str[:2].astype(int)

    # =============================
    # 4) AJUSTAR DESPESAS
    # =============================
    df_desp["ANO"] = df_desp["ANO"].astype(int)
    df_desp["MÊS_NUM"] = df_desp["MÊS"].str[:2].astype(int)

    # =============================
    # 5) AGRUPAR
    # =============================
    tabela_fat = (
        df_fat.groupby(["Ano", "MÊS_NUM"])["Faturamento - Valor"]
        .sum()
        .reset_index()
        .rename(columns={"Ano": "ANO", "Faturamento - Valor": "FAT"})
    )

    tabela_desp = (
        df_desp.groupby(["ANO", "MÊS_NUM"])["VALOR"]
        .sum()
        .reset_index()
        .rename(columns={"VALOR": "DESP"})
    )

    # =============================
    # 6) MERGE
    # =============================
    base = pd.merge(tabela_fat, tabela_desp, on=["ANO", "MÊS_NUM"], how="outer")
    base["DESP"] = base["DESP"].fillna(0)
    base["RESULT"] = base["FAT"] - base["DESP"]

    # =============================
    # 7) SEPARAR ANOS
    # =============================
    df24 = base[base["ANO"] == 2024].sort_values("MÊS_NUM")
    df25 = base[base["ANO"] == 2025].sort_values("MÊS_NUM")

    # =============================
    # 8) FUNÇÃO FORMATAÇÃO
    # =============================
    def fmt(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # =============================
    # 9) SOMATÓRIOS
    # =============================
    soma_24 = {
        "FAT_TOTAL": df24["FAT"].sum(),
        "DESP_TOTAL": df24["DESP"].sum(),
        "RESULT_TOTAL": df24["RESULT"].sum()
    }

    soma_25 = {
        "FAT_TOTAL": df25["FAT"].sum(),
        "DESP_TOTAL": df25["DESP"].sum(),
        "RESULT_TOTAL": df25["RESULT"].sum()
    }

    # =============================
    # 10) CARDS
    # =============================
    st.markdown("## 📌 Visão Geral do Ano")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background:#0A66C2;padding:20px;border-radius:12px;color:white;">
        <h3>Ano 2024</h3>
        📈 Faturamento<br><b>{fmt(soma_24['FAT_TOTAL'])}</b><br><br>
        💸 Despesas<br><b>{fmt(soma_24['DESP_TOTAL'])}</b><br><br>
        💰 Resultado<br><b>{fmt(soma_24['RESULT_TOTAL'])}</b>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:#6F42C1;padding:20px;border-radius:12px;color:white;">
        <h3>Ano 2025</h3>
        📈 Faturamento<br><b>{fmt(soma_25['FAT_TOTAL'])}</b><br><br>
        💸 Despesas<br><b>{fmt(soma_25['DESP_TOTAL'])}</b><br><br>
        💰 Resultado<br><b>{fmt(soma_25['RESULT_TOTAL'])}</b>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background:#0B5E55;padding:20px;border-radius:12px;color:white;">
        <h3>Variação</h3>
        📊 Faturamento<br><b>{fmt(soma_25['FAT_TOTAL'] - soma_24['FAT_TOTAL'])}</b><br><br>
        📊 Despesas<br><b>{fmt(soma_25['DESP_TOTAL'] - soma_24['DESP_TOTAL'])}</b><br><br>
        📊 Resultado<br><b>{fmt(soma_25['RESULT_TOTAL'] - soma_24['RESULT_TOTAL'])}</b>
        </div>
        """, unsafe_allow_html=True)

    # =============================
    # 11) TABELAS
    # =============================
    st.subheader("📄 Resultado 2024")
    st.dataframe(df24.assign(
        FAT=df24["FAT"].apply(fmt),
        DESP=df24["DESP"].apply(fmt),
        RESULT=df24["RESULT"].apply(fmt)
    ), use_container_width=True)

    st.subheader("📄 Resultado 2025")
    st.dataframe(df25.assign(
        FAT=df25["FAT"].apply(fmt),
        DESP=df25["DESP"].apply(fmt),
        RESULT=df25["RESULT"].apply(fmt)
    ), use_container_width=True)

    # =============================
    # 12) GRÁFICO
    # =============================
    fig = px.line(
        base.sort_values(["ANO", "MÊS_NUM"]),
        x="MÊS_NUM",
        y="RESULT",
        color="ANO",
        markers=True,
        title="Resultado Mensal (2024 x 2025)"
    )

    fig.update_traces(
        hovertemplate="R$ %{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.plotly_chart(fig, use_container_width=True)

