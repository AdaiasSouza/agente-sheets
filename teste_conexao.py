import json
import gspread
import traceback
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds  = Credentials.from_service_account_file(
    "config/credenciais.json",
    scopes=scopes
)
client = gspread.authorize(creds)

with open("config/sheets.json", "r") as f:
    config = json.load(f)

for planilha in config["planilhas"]:
    try:
        sheet = client.open_by_key(planilha["id"]).worksheet(planilha["aba"])
        dados = sheet.get_all_records()
        print(f" {planilha['nome']} — {len(dados)} linhas encontradas")
    except Exception as e:
        print(f" {planilha['nome']} — Erro: {e}")
        traceback.print_exc()