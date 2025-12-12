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
    # 2) PADRONIZAR NOMES DAS COLUNAS
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
    tabela_fat = df_fat.groupby(["Ano", "MÊS_NUM"])["Faturamento - Valor"].sum().reset_index()
    tabela_desp = df_desp.groupby(["ANO", "MÊS_NUM"])["VALOR"].sum().reset_index()

    tabela_fat.rename(columns={"Ano": "ANO", "Faturamento - Valor": "FAT"}, inplace=True)
    tabela_desp.rename(columns={"VALOR": "DESP"}, inplace=True)

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
    # 8) FUNÇÃO FORMATO BRASILEIRO
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
# 🔷🔷🔷 10) CARDS CORPORATIVOS CORRIGIDOS
# =============================

st.markdown("## 📌 Visão Geral do Ano")

col1, col2, col3 = st.columns(3)

# -------- CARD 2024 --------
with col1:
    st.markdown(f"""
    <div style="
        background-color:#0A66C2;
        padding:20px;
        border-radius:12px;
        color:white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    ">
        <h3 style="margin-top:0; font-size:22px;">Ano 2024</h3>

        <p style="margin:6px 0 0;">📈 Faturamento</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_24['FAT_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">💸 Despesas</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_24['DESP_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">💰 Resultado</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_24['RESULT_TOTAL'])}</b></p>
    </div>
    """, unsafe_allow_html=True)

# -------- CARD 2025 --------
with col2:
    st.markdown(f"""
    <div style="
        background-color:#6F42C1;
        padding:20px;
        border-radius:12px;
        color:white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    ">
        <h3 style="margin-top:0; font-size:22px;">Ano 2025</h3>

        <p style="margin:6px 0 0;">📈 Faturamento</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['FAT_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">💸 Despesas</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['DESP_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">💰 Resultado</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['RESULT_TOTAL'])}</b></p>
    </div>
    """, unsafe_allow_html=True)

# -------- CARD VARIAÇÃO --------
with col3:
    st.markdown(f"""
    <div style="
        background-color:#0B5E55;
        padding:20px;
        border-radius:12px;
        color:white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    ">
        <h3 style="margin-top:0; font-size:22px;">Variação</h3>

        <p style="margin:6px 0 0;">📊 Faturamento</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['FAT_TOTAL'] - soma_24['FAT_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">📊 Despesas</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['DESP_TOTAL'] - soma_24['DESP_TOTAL'])}</b></p>

        <p style="margin:10px 0 0;">📊 Resultado</p>
        <p style="font-size:24px; margin:0;"><b>{fmt(soma_25['RESULT_TOTAL'] - soma_24['RESULT_TOTAL'])}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # =============================
    # 11) TABELA 2024
    # =============================
    df24_fmt = df24.copy()
    df25_fmt = df25.copy()

    for col in ["FAT", "DESP", "RESULT"]:
        df24_fmt[col] = df24[col].apply(fmt)
        df25_fmt[col] = df25[col].apply(fmt)

    st.subheader("📄 Resultado 2024")
    st.dataframe(df24_fmt, use_container_width=True)

    st.markdown(f"""
    ### **Totais 2024**
    • **Faturamento:** {fmt(soma_24['FAT_TOTAL'])}  
    • **Despesas:** {fmt(soma_24['DESP_TOTAL'])}  
    • **Resultado:** {fmt(soma_24['RESULT_TOTAL'])}  
    """)

    # =============================
    # 12) TABELA 2025
    # =============================
    st.subheader("📄 Resultado 2025")
    st.dataframe(df25_fmt, use_container_width=True)

    st.markdown(f"""
    ### **Totais 2025**
    • **Faturamento:** {fmt(soma_25['FAT_TOTAL'])}  
    • **Despesas:** {fmt(soma_25['DESP_TOTAL'])}  
    • **Resultado:** {fmt(soma_25['RESULT_TOTAL'])}  
    """)

    # =============================
    # 13) GRÁFICO DE RESULTADO
    # =============================
    graf = base.sort_values(["ANO", "MÊS_NUM"])

    fig = px.line(
        graf,
        x="MÊS_NUM",
        y="RESULT",
        color="ANO",
        markers=True,
        title="Linha do Resultado (2024 x 2025)",
        labels={"MÊS_NUM": "Mês", "RESULT": "Resultado (R$)"}
    )

    fig.update_layout(
        yaxis_tickformat=",",
        legend_title_text="Ano",
        height=450
    )

    fig.update_traces(
        hovertemplate="R$ %{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.plotly_chart(fig, use_container_width=True)

