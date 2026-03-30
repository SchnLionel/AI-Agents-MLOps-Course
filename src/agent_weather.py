import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import Tool
from src.tools.weather import get_weather, WeatherInput
from src.tools.calculator import Calculator, CalculatorInput

# Configuration du logging
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

# --- DÉFINITION DES OUTILS ---
tools = [
    Tool(
        name="Calculatrice",
        func=Calculator,
        description="Utile pour les calculs arithmétiques. Prend une expression mathématique comme chaîne, par ex. '2 + 2 * 3'.",
        args_schema=CalculatorInput
    ),
    Tool(
        name="GetWeather",
        func=get_weather,
        description="Obtient la météo actuelle pour une ville donnée. Renvoie un dictionnaire avec la température (Celsius).",
        args_schema=WeatherInput
    )
]

# Création de l'agent avec LangGraph
agent = create_react_agent(llm, tools)

def run_agent(question: str):
    print("\n" + "="*50)
    print(f"QUESTION: {question}")
    print("="*50)
    
    inputs = {"messages": [("user", question)]}
    
    try:
        # On affiche les étapes pour la transparence (Raisonnement)
        for chunk in agent.stream(inputs, stream_mode="values"):
            message = chunk["messages"][-1]
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    print(f"\n[AGENT RAISONNE] : Besoin de l'outil '{tool_call['name']}' avec les arguments {tool_call['args']}")
            elif message.content and message.type == "human":
                pass
            elif message.content:
                # C'est souvent la réponse finale ou une réflexion
                pass

        # Résultat final
        result = agent.invoke(inputs)
        final_answer = result["messages"][-1].content
        print(f"\n[RÉPONSE FINALE] : {final_answer}")
        
    except Exception as e:
        print(f"\n[ERREUR] : {e}")

if __name__ == "__main__":
    # Test multi-étapes : Météo -> Calcul
    query = "Quel temps fait-il à Paris et quel est le carré de sa température ?"
    run_agent(query)
    
    # Test simple : Juste météo
    # run_agent("Quelle est la météo à Lyon ?")
