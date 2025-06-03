import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# 1. Título e Descrição da Aplicação
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("PluvCity: Cada Milímetro Conta ")

st.sidebar.header("Dados metereológicos do INMET")

# -----------------------------------------------------------------------------
# 2. Importando os dados
# -----------------------------------------------------------------------------
df = pd.read_parquet("dados_agrupados_inmet.parquet")


# Obtendo a lista de anos únicos no DataFrame
min_year = int(df["ano"].min())
max_year = int(df["ano"].max())


# Criando o slider de ano
selected_years = st.sidebar.slider(
    "Selecione o Intervalo de Anos",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),  # Valor padrão: todo o intervalo
    step=1,
)

# Filtro de UF com multiselect (seleciona todas por padrão)
ufs_disponiveis = sorted(df["uf"].unique())
ufs_opcoes = ["Todas"] + ufs_disponiveis

uf_selecionada = st.sidebar.selectbox("Selecione a UF:", options=ufs_opcoes)

# Filtro
if uf_selecionada == "Todas":
    df_filtered = df[
        (df["ano"] >= selected_years[0]) & (df["ano"] <= selected_years[1])
    ]

else:
    df_filtered = df[
        (
            (df["ano"] >= selected_years[0])
            & (df["ano"] <= selected_years[1])
            & (df["uf"] == uf_selecionada)
        )
    ]


st.sidebar.markdown("---")
st.sidebar.subheader("Sobre os Dados")
st.sidebar.write(f"Ano Inicial: {min_year}")
st.sidebar.write(f"Ano Final: {max_year}")
st.sidebar.write(f"Total de Registros: {len(df)}")
st.sidebar.write(f"Registros Filtrados: {len(df_filtered)}")

# -----------------------------------------------------------------------------
# 3. Criação das Colunas e Inserção dos Gráficos
# -----------------------------------------------------------------------------

# --- Criação das Abas ---
tab1, tab2 = st.tabs(["Visão Executiva", "Por Região/UF"])

with tab1:
    st.header("Visão Executiva")

    ## Métricas chaves
    media_precipiticao_ano = (
        df_filtered.groupby(["ano"]).precipitacao_total.mean().reset_index()
    )
    media_precipiticao_anual = media_precipiticao_ano.precipitacao_total.mean()

    media_pressao_ano = df_filtered.groupby(["ano"]).pressao_media.mean().reset_index()
    media_pressao_anual = media_pressao_ano.pressao_media.mean()

    media_temperatura_ano = (
        df_filtered.groupby(["ano"]).temperatura_media.mean().reset_index()
    )
    media_temperatura_anual = media_temperatura_ano.temperatura_media.mean()

    media_umidade_ano = df_filtered.groupby(["ano"]).umidade_media.mean().reset_index()
    media_umidade_anual = media_umidade_ano.umidade_media.mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Precipitação média diária (mm)",
            value=f"{media_precipiticao_anual:,.2f}",
        )
    with col2:
        st.metric(
            label="Temperatura Média diária (°C)",
            value=f"{media_temperatura_anual:,.2f}",
        )
    with col3:
        st.metric(
            label="Pressão Média diária (mB)", value=f"{media_pressao_anual:,.2f}"
        )
    with col4:
        st.metric(label="Umidade Média diária (%)", value=f"{media_umidade_anual:,.2f}")

    st.markdown("---")  # Linha divisória para organizar
    st.subheader("Visão Temporal")

    col1, col2 = st.columns(2)

    with col1:

        # Precipitação por mês
        precipitacao_por_mes = (
            df_filtered.groupby("ano")["precipitacao_total"].sum().reset_index()
        )
        precipitacao_por_mes.columns = ["Ano", "Precipitacao"]

        fig_precipitacao_mes = px.line(
            precipitacao_por_mes,
            x="Ano",
            y="Precipitacao",
            title=f"Variação do Precipitacao Total por Mês em {selected_years[0]} - {selected_years[1]}",
            labels={"Ano": "Ano", "Precipitacao": "Precipitacao (mm)"},
            markers=True,  # Adiciona marcadores para cada ponto de dados
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )  # Outra paleta de cores
        fig_precipitacao_mes.update_traces(
            hovertemplate="Ano: %{x}<br>Precipitacao: %{y:.2f} mm<extra></extra>"
        )  # Formata tooltip
        fig_precipitacao_mes.update_xaxes(
            tickformat="%b %Y"
        )  # Formata o tick do eixo X para mostrar Mês Ano
        st.plotly_chart(fig_precipitacao_mes, use_container_width=True)
    with col2:

        # Temperatura por mês
        temperatura_por_mes = (
            df_filtered.groupby("ano")["temperatura_media"].mean().reset_index()
        )
        temperatura_por_mes.columns = ["Ano", "Temperatura"]

        fig_temperatura_mes = px.line(
            temperatura_por_mes,
            x="Ano",
            y="Temperatura",
            title=f"Variação da Temperatura por Ano em {selected_years[0]} - {selected_years[1]}",
            labels={"Ano": "Ano", "Temperatura": "Temperatura (°C)"},
            markers=True,  # Adiciona marcadores para cada ponto de dados
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )  # Outra paleta de cores
        fig_temperatura_mes.update_traces(
            hovertemplate="Ano: %{x}<br>Temperatura:%{y:.2f}°C<extra></extra>"
        )  # Formata tooltip
        fig_temperatura_mes.update_xaxes(
            tickformat="%b %Y"
        )  # Formata o tick do eixo X para mostrar Ano
        st.plotly_chart(fig_temperatura_mes, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Precipitação por mês
        pressao_por_mes = (
            df_filtered.groupby("ano")["pressao_media"].mean().reset_index()
        )
        pressao_por_mes.columns = ["Ano", "Pressao"]

        fig_pressao_mes = px.line(
            pressao_por_mes,
            x="Ano",
            y="Pressao",
            title=f"Variação do Pressao Total por Mês em {selected_years[0]} - {selected_years[1]}",
            labels={"Ano": "Ano", "Pressao": "Pressao (mB)"},
            markers=True,  # Adiciona marcadores para cada ponto de dados
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )  # Outra paleta de cores
        fig_pressao_mes.update_traces(
            hovertemplate="Ano: %{x}<br>Pressao: %{y:.2f} mB<extra></extra>"
        )  # Formata tooltip
        fig_pressao_mes.update_xaxes(
            tickformat="%b %Y"
        )  # Formata o tick do eixo X para mostrar Mês Ano
        st.plotly_chart(fig_pressao_mes, use_container_width=True)
    with col2:
        # Precipitação por mês
        umidade_por_mes = (
            df_filtered.groupby("ano")["umidade_media"].mean().reset_index()
        )
        umidade_por_mes.columns = ["Ano", "Umidade"]

        fig_umidade_mes = px.line(
            umidade_por_mes,
            x="Ano",
            y="Umidade",
            title=f"Variação do Umidade Total por Mês em {selected_years[0]} - {selected_years[1]}",
            labels={"Ano": "Ano", "Umidade": "Umidade (%    )"},
            markers=True,  # Adiciona marcadores para cada ponto de dados
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )  # Outra paleta de cores
        fig_umidade_mes.update_traces(
            hovertemplate="Ano: %{x}<br>Umidade: %{y:.2f} %<extra></extra>"
        )  # Formata tooltip
        fig_umidade_mes.update_xaxes(
            tickformat="%b %Y"
        )  # Formata o tick do eixo X para mostrar Mês Ano
        st.plotly_chart(fig_umidade_mes, use_container_width=True)

with tab2:
    st.header("Por Região/UF")

    st.subheader("Precipitação por Região do Brasil")
    precipitacao_por_regiao = (
        df_filtered.groupby("regiao")["precipitacao_total"].sum().reset_index()
    )
    precipitacao_por_regiao.columns = [
        "Regiao",
        "Precipitacao",
    ]
    fig_precipitacao_regiao = px.bar(
        precipitacao_por_regiao,
        x="Regiao",
        y="Precipitacao",
        title="Precipitação por Região",
        labels={
            "Regiao": "Regiao",
            "Precipitacao": "Precipitacao",
        },
        color_discrete_sequence=px.colors.qualitative.Dark2,
    )  # Outra paleta de cores
    fig_precipitacao_regiao.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=precipitacao_por_regiao["Regiao"],
        )
    )  # Garante todos os ticks numéricos
    st.plotly_chart(fig_precipitacao_regiao, use_container_width=True)

    st.subheader("Precipitação por Estado do Brasil")

    precipitacao_por_estado = (
        df_filtered.groupby("uf")["precipitacao_total"]
        .sum()
        .reset_index()
        .sort_values(by="precipitacao_total")
    )
    precipitacao_por_estado.columns = [
        "Estado",
        "Precipitacao",
    ]

    fig_precipitacao_estado = px.bar(
        precipitacao_por_estado,
        y="Estado",
        x="Precipitacao",
        title="Precipitação por Estado",
        labels={
            "Estado": "Estado",
            "Precipitacao": "Precipitacao",
        },
        color_discrete_sequence=px.colors.qualitative.Dark2,
        orientation="h",
    )  # Outra paleta de cores
    fig_precipitacao_estado.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=precipitacao_por_estado["Estado"],
        )
    )  # Garante todos os ticks numéricos
    st.plotly_chart(fig_precipitacao_estado, use_container_width=True)
