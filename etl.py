import pandas as pd
import os
import logging
from pathlib import Path
import  unicodedata
import re


# -- Importante o módulo de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# -------- Paths --------
folder_path = Path("/Users/viniciusrocha/Desktop/pluv_city/data/raw")
output_path = Path("/Users/viniciusrocha/Desktop/pluv_city/data/processed")


df_anos = []


def listar_arquivos(path):
    arquivos = []
    for f in os.listdir(path):
        if not f.startswith("."):
            arquivos.append(f)
    return arquivos

def normalize_metadata_key(key: str) -> str:
    """
    Normaliza a chave de metadado:
      1) Remove acentos (NFKD → descarta combining marks).
      2) Elimina qualquer caractere que não seja letra/número/espaco.
      3) Converte tudo para minúsculas e substitui espaços por underscore.
      4) Remove eventuais underlines finais.
    Exemplo de saída: "REGI?O:" ou "REGIÃO:" → "regiao"
    """
    # 1) Descompor acentos (NFKD) e descartar marcas de acentuação
    nfkd = unicodedata.normalize("NFKD", key)
    sem_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))

    # 2) Remover qualquer caractere que não seja letra, número ou espaço
    apenas_alnum_espaco = re.sub(r"[^A-Za-z0-9 ]+", "", sem_acentos)

    # 3) Transformar em minúsculas e trocar espaços por underscore
    minusculo = apenas_alnum_espaco.strip().lower()
    com_underscore = minusculo.replace(" ", "_")

    # 4) Remover eventual underscore no final
    return com_underscore.rstrip("_")

anos = sorted(listar_arquivos(folder_path))

logger.info(f"Anos disponiveis: {anos}")


for ano in anos:

    logger.info(f"Iniciando o processamento dos dados brutos do ano {ano}")

    dfs_por_ano = []

    path_ano = os.path.join(folder_path, ano)

    arquivos_do_ano = listar_arquivos(path_ano)

    for arquivo in arquivos_do_ano:

        file = os.path.join(path_ano, arquivo)
        # Ler os metadados do arquivo, ou seja,as primeiras linahs do dataframe que contem informacoes sobre a estacao de medicao
            # 1) Definir chaves “esperadas” de metadado e inicializar com None
        metadata= {}
        with open(file, "r", encoding="latin1") as f:
            for _ in range(8):
                line = f.readline().strip()
                if ";" not in line:
                    continue
                key_raw, val = line.split(";", 1)
                key = normalize_metadata_key(key_raw)
                if key == 'regio':
                    key ='regiao'
                if key == 'estaco':
                    key ='estacao'

                metadata[key] = val

        # Agora que lemos os metadados, vamos criar o dataframe puro lendo os arquivos da base
        # Como os dados estao acentuadas e com virgula separando os decimais, foi necessario incluir o parametro encoding e decimal
        df_raw = pd.read_csv(file, sep=";", skiprows=8, encoding="latin1", decimal=",")

        df_raw.columns = [
            "DATA (YYYY-MM-DD)",
            "HORA (UTC)",
            "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)",
            "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)",
            "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)",
            "RADIACAO GLOBAL (KJ/m²)",
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            "TEMPERATURA DO PONTO DE ORVALHO (°C)",
            "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)",
            "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)",
            "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)",
            "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)",
            "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)",
            "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)",
            "UMIDADE RELATIVA DO AR, HORARIA (%)",
            "VENTO, DIREÇÃO HORARIA (gr) (° (gr))",
            "VENTO, RAJADA MAXIMA (m/s)",
            "VENTO, VELOCIDADE HORARIA (m/s)",
            "Unnamed: 19",
        ]

        df_raw["DATA (YYYY-MM-DD)"] = pd.to_datetime(df_raw["DATA (YYYY-MM-DD)"])

        # Retirando o UTC da hora e convertendo ela em um numero com 4 digitos
        df_raw["HORA (UTC)"] = (
            df_raw["HORA (UTC)"].str.replace(" UTC", "", regex=False).str.zfill(4)
        )

        # Pegando apenas os dois primeiros digitos da hora
        df_raw["hora_int"] = (
            df_raw["HORA (UTC)"].str.slice(0, 2).astype(int)
        )  # “00” → 0, “01” → 1, …, “23” → 23

        # Criando o campo data_hora
        df_raw["data_hora"] = df_raw["DATA (YYYY-MM-DD)"] + pd.to_timedelta(
            df_raw["hora_int"], unit="h"
        )

        # Agora vamos selecionar apenas os campos relevantes para seguir com a análise
        df = df_raw[
            [
                "data_hora",
                "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
                "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)",
                "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)",
                "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)",
                "RADIACAO GLOBAL (KJ/m²)",
                "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
                "TEMPERATURA DO PONTO DE ORVALHO (°C)",
                "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)",
                "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)",
                "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)",
                "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)",
                "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)",
                "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)",
                "UMIDADE RELATIVA DO AR, HORARIA (%)",
                "VENTO, DIREÇÃO HORARIA (gr) (° (gr))",
                "VENTO, RAJADA MAXIMA (m/s)",
                "VENTO, VELOCIDADE HORARIA (m/s)",
            ]
        ].copy()

        # Renomeando as colunas para facilitar os proximos passos
        df.columns = [
            "data_hora",
            "precipitacao_mm",
            "pressao_hora",
            "pressao_max_hora_ant",
            "pressao_min_hora_ant",
            "radiacao_global",
            "temp_bulbo_seco",
            "temp_ponto_orvalho",
            "temp_max_hora_ant",
            "temp_min_hora_ant",
            "dewpoint_max_hora_ant",
            "dewpoint_min_hora_ant",
            "umid_max_hora_ant",
            "umid_min_hora_ant",
            "umid_horaria",
            "vento_direcao_graus",
            "vento_rajada",
            "vento_velocidade",
        ]

        # Agora vamos garantir que todos os dados numericos estejam com o tipo correto, caso haja algum outra informação vamos converter para NaN
        to_numeric_cols = [
            "precipitacao_mm",
            "pressao_hora",
            "pressao_max_hora_ant",
            "pressao_min_hora_ant",
            "radiacao_global",
            "temp_bulbo_seco",
            "temp_ponto_orvalho",
            "temp_max_hora_ant",
            "temp_min_hora_ant",
            "dewpoint_max_hora_ant",
            "dewpoint_min_hora_ant",
            "umid_max_hora_ant",
            "umid_min_hora_ant",
            "umid_horaria",
            "vento_rajada",
            "vento_velocidade",
        ]

        for col in to_numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df['latitude'] = df['latitude'].astype(str).str.replace(',', '.', regex=False)
        df['latitude'] = df['latitude'].str.strip()
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')

        df['longitude'] = df['longitude'].astype(str).str.replace(',', '.', regex=False)
        df['longitude'] = df['longitude'].str.strip()
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        # Extraindo as variáveis temporais (ano, mês, dia_da_semana, hora) ---
        df["ano"] = df["data_hora"].dt.year
        df["mes"] = df["data_hora"].dt.month
        df["dia_semana"] = df["data_hora"].dt.dayofweek  # 0=segunda … 6=domingo
        df["hora_do_dia"] = df["data_hora"].dt.hour

        # Adicionando os metadados
        df["regiao"] = metadata["regiao"]
        df["uf"] = metadata["uf"]
        df["estacao"] = metadata["estacao"]
        df["codigo_wmo"] = metadata["codigo_wmo"]
        df["latitude"] = metadata["latitude"]
        df["longitude"] = metadata["longitude"]
        df["altitude"] = metadata["altitude"]

        # Agora vamos criar variável alvo binária “choveu” ---
        df["choveu"] = (df["precipitacao_mm"] > 0).astype(int)

        dfs_por_ano.append(df)

    if dfs_por_ano:
        df_ano = pd.concat(dfs_por_ano, ignore_index=True)
        df_anos.append(df_ano)

    logger.info(f"Dados do ano {ano} salvos com sucesso")


arquivo_saida = os.path.join(output_path, f"medicoes_precipitacao.parquet")

df_todos_os_anos = pd.concat(df_anos, ignore_index=True)

df_todos_os_anos.to_parquet(arquivo_saida, compression="gzip")
