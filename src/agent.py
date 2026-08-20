# src/agent.py
import json
from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from src.tools import (
    conectar_sheets,
    ler_planilha,
    salvar_parquet,
    carregar_config_sheets,
    registrar_log
)

load_dotenv()

# ─── Inicializa o LLM ─────────────────────────────────────────────────────────

llm = OllamaLLM(model="llama3.2", temperature=0)

# ─── Estado compartilhado entre ferramentas ───────────────────────────────────

estado = {
    "client":    None,
    "planilhas": [],
    "resultados": []
}

# ─── Ferramentas do agente ────────────────────────────────────────────────────

def tool_conectar(_input: str) -> str:
    try:
        estado["client"]    = conectar_sheets()
        estado["planilhas"] = carregar_config_sheets()
        nomes = [p["nome"] for p in estado["planilhas"]]
        return f"Conectado com sucesso. Planilhas disponíveis: {nomes}"
    except Exception as e:
        return f"Erro ao conectar: {e}"

def tool_ingerir(_input: str) -> str:
    if not estado["client"]:
        return "Erro: conectar ao Google Sheets primeiro"
    resultados = []
    for p in estado["planilhas"]:
        try:
            df      = ler_planilha(estado["client"], p["id"], p["aba"], p["nome"])
            caminho = salvar_parquet(df, p["nome"])
            resultados.append(f"{p['nome']}: {len(df)} linhas salvas em {caminho}")
            estado["resultados"].append({"planilha": p["nome"], "linhas": len(df), "caminho": caminho, "status": "sucesso"})
        except Exception as e:
            resultados.append(f"{p['nome']}: erro — {e}")
            estado["resultados"].append({"planilha": p["nome"], "status": "erro", "erro": str(e)})
    return "\n".join(resultados)

def tool_relatorio(_input: str) -> str:
    if not estado["resultados"]:
        return "Nenhuma ingestão realizada ainda"
    total    = len(estado["resultados"])
    sucessos = sum(1 for r in estado["resultados"] if r["status"] == "sucesso")
    erros    = total - sucessos
    linhas   = [
        "Relatorio de ingestao:",
        f"Total de planilhas: {total}",
        f"Sucesso: {sucessos}",
        f"Erros: {erros}",
    ]
    for r in estado["resultados"]:
        if r["status"] == "sucesso":
            linhas.append(f"  - {r['planilha']}: {r['linhas']} linhas -> {r['caminho']}")
        else:
            linhas.append(f"  - {r['planilha']}: ERRO — {r['erro']}")
    return "\n".join(linhas)

# ─── Definição das ferramentas para o LangChain ───────────────────────────────

tools = [
    Tool(
        name="conectar_google_sheets",
        func=tool_conectar,
        description="Conecta ao Google Sheets e carrega a lista de planilhas configuradas. Use sempre como primeiro passo."
    ),
    Tool(
        name="ingerir_planilhas",
        func=tool_ingerir,
        description="Le todas as planilhas do Google Sheets e salva em formato Parquet. Use apos conectar_google_sheets."
    ),
    Tool(
        name="gerar_relatorio",
        func=tool_relatorio,
        description="Gera um relatorio com o resultado da ingestao. Use como ultimo passo."
    )
]

# ─── Prompt do agente ─────────────────────────────────────────────────────────

prompt = PromptTemplate.from_template("""
Você é um agente de ingestão de dados. Seu objetivo é:
1. Conectar ao Google Sheets
2. Ler todas as planilhas configuradas
3. Salvar os dados em formato Parquet
4. Gerar um relatório do processo

Responda sempre em português.

Ferramentas disponíveis:
{tools}

Nomes das ferramentas: {tool_names}

Use o formato:
Thought: o que preciso fazer
Action: nome_da_ferramenta
Action Input: entrada para a ferramenta
Observation: resultado da ferramenta
... (repita até concluir)
Thought: concluí todas as etapas
Final Answer: resumo do que foi feito

{agent_scratchpad}

Objetivo: {input}
""")

# ─── Criar e executar o agente ────────────────────────────────────────────────

def executar_agente():
    registrar_log("INFO", "Iniciando agente de ingestao")

    agente   = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agente,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    resultado = executor.invoke({
        "input": "Conecte ao Google Sheets, ingira todas as planilhas configuradas e gere um relatorio do processo."
    })

    registrar_log("INFO", f"Agente concluido: {resultado['output']}")
    print("\nResultado final:", resultado["output"])

if __name__ == "__main__":
    executar_agente()