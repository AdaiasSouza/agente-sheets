# src/tools.py
import json
import os
# import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
from src.logger import configurar_logger

load_dotenv()

logger = configurar_logger()
# ─── Configurações ────────────────────────────────────────────────────────────

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "config/credenciais.json")
OUTPUT_PATH      = os.getenv("OUTPUT_PATH", "data/parquet")
LOG_PATH         = os.getenv("LOG_PATH", "logs/agente.log")
SHEETS_CONFIG    = os.getenv("SHEETS_CONFIG", "config/sheets.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ─── Ferramenta 1: Conectar ao Google Sheets ──────────────────────────────────

def conectar_sheets() -> gspread.Client:
    """Autentica com a Service Account e retorna o cliente gspread."""
    try:
        creds  = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
        registrar_log("INFO", "Autenticação com Google Sheets realizada com sucesso")
        return client
    except Exception as e:
        registrar_log("ERROR", f"Falha na autenticação com Google Sheets: {e}")
        raise

# ─── Ferramenta 2: Ler planilha ───────────────────────────────────────────────

def ler_planilha(client: gspread.Client, sheet_id: str, aba: str, nome: str) -> pd.DataFrame:
    """Lê os dados de uma planilha e retorna um DataFrame."""
    try:
        registrar_log("INFO", f"Conectando à planilha: {nome}")
        sheet  = client.open_by_key(sheet_id).worksheet(aba)
        dados  = sheet.get_all_records()
        df     = pd.DataFrame(dados)
        registrar_log("INFO", f"Planilha {nome} lida com sucesso — {len(df)} linhas, {len(df.columns)} colunas")
        return df
    except Exception as e:
        registrar_log("ERROR", f"Falha ao ler planilha {nome}: {e}")
        raise

# ─── Ferramenta 3: Salvar Parquet ─────────────────────────────────────────────

def salvar_parquet(df: pd.DataFrame, nome: str) -> str:
    """Salva o DataFrame como Parquet na pasta data/parquet."""
    try:
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{nome}_{timestamp}.parquet"
        caminho     = os.path.join(OUTPUT_PATH, nome_arquivo)
        # Converte colunas com tipos misturados para string
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str)

        df.to_parquet(caminho, index=False)
        registrar_log("INFO", f"Arquivo salvo: {caminho} — {len(df)} linhas")
        return caminho
    except Exception as e:
        registrar_log("ERROR", f"Falha ao salvar Parquet {nome}: {e}")
        raise

# ─── Ferramenta 4: Registrar log ──────────────────────────────────────────────

def registrar_log(nivel: str, mensagem: str) -> None:
    """Registra eventos usando o logger centralizado."""
    niveis = {
        "INFO":    logger.info,
        "WARNING": logger.warning,
        "ERROR":   logger.error,
        "DEBUG":   logger.debug
    }
    log_func = niveis.get(nivel.upper(), logger.info)
    log_func(mensagem)

# ─── Função auxiliar: carregar config das planilhas ───────────────────────────

def carregar_config_sheets() -> list:
    """Lê o arquivo sheets.json e retorna a lista de planilhas."""
    try:
        with open(SHEETS_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config["planilhas"]
    except Exception as e:
        registrar_log("ERROR", f"Falha ao carregar config das planilhas: {e}")
        raise