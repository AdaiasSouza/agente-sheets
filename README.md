# Agente de Ingestão de Planilhas

Agente baseado em LangChain + Ollama que extrai dados
do Google Sheets, converte para Parquet e registra logs
do processo.

---

## Funcionalidades

- Conecta ao Google Sheets via Service Account
- Lê dados de múltiplas planilhas
- Salva em formato Parquet em repositório específico
- Registra log detalhado de cada execução

---

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3.11 | Linguagem principal |
| LangChain | Framework do agente |
| Ollama + Llama 3.2 | LLM local |
| gspread | Conexão com Google Sheets |
| pandas + pyarrow | Conversão para Parquet |

---

## Pré-requisitos

- Python 3.11+
- Ollama instalado e rodando
- Service Account configurada no Google Cloud
- WSL com Ubuntu

---

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/agente-sheets.git
cd agente-sheets

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com seus valores
```

---

## Configuração do Google Sheets

1. Crie uma Service Account no Google Cloud Console
2. Baixe o arquivo JSON e salve em `config/credenciais.json`
3. Compartilhe cada planilha com o e-mail da Service Account
4. Configure os IDs das planilhas em `config/sheets.json`

Consulte a documentação completa em `docs/Service_Account_Google_Cloud.pdf`

---

## Configuração das planilhas

Edite o arquivo `config/sheets.json`:

```json
{
  "planilhas": [
    {
      "nome": "Planilha 1",
      "id": "SEU_ID_AQUI",
      "aba": "Sheet1"
    },
    {
      "nome": "Planilha 2",
      "id": "SEU_ID_AQUI",
      "aba": "Sheet1"
    }
  ]
}
```

---

## Como usar

```bash
# Ativar o Ollama
ollama serve

# Rodar o agente
python src/agent.py
```

---

## Estrutura do log