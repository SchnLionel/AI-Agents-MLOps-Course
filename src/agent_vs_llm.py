import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import Tool
from src.tools.calculator import Calculator, CalculatorInput

# Configuration du logging pour voir les appels d'outils
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv(override=True)
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialisation du LLM (via le pont OpenAI pour Groq)
llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

question = "Calculate (123.45 * 456.78) / 789.01 + 12.34"

# --- PARTIE 1: LLM SEUL ---
print("\n" + "="*50)
print("TEST 1: LLM SEUL (Sans outils)")
print("="*50)
try:
    response = llm.invoke(question)
    print(f"Q: {question}")
    print(f"A: {response.content}")
except Exception as e:
    print(f"Erreur LLM seul: {e}")

# --- PARTIE 2: AGENT AVEC OUTIL ---
print("\n" + "="*50)
print("TEST 2: AGENT AVEC OUTIL (Calculatrice)")
print("="*50)

# Définition de l'outil
tools = [
    Tool(
        name="Calculatrice",
        func=Calculator,
        description=(
            "Useful for arithmetic operations. "
            "Takes a mathematical expression as a string, e.g., '2 + 2 * 3' or 'sqrt(144) + 5'."
        ),
        args_schema=CalculatorInput
    )
]

# Création de l'agent avec LangGraph (plus robuste)
agent = create_react_agent(llm, tools)

try:
    # Exécution
    inputs = {"messages": [("user", question)]}
    print(f"Question: {question}")
    
    for chunk in agent.stream(inputs, stream_mode="values"):
        message = chunk["messages"][-1]
        if hasattr(message, "tool_calls") and message.tool_calls:
            print(f"--- Agent appelle l'outil: {message.tool_calls[0]['name']} avec {message.tool_calls[0]['args']} ---")
        elif message.content:
            # On affiche seulement le résultat final ou les réflexions importantes
            pass

    final_message = agent.invoke(inputs)["messages"][-1]
    print(f"\nA (Agent): {final_message.content}")
except Exception as e:
    print(f"Erreur Agent: {e}")

print("\n" + "="*50)
print("FIN DE LA COMPARAISON")
print("="*50)
