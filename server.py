# from flask import Flask, request, jsonify
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain_community.vectorstores import FAISS
# from langchain.tools import Tool
# from langchain.agents import initialize_agent, AgentType
# import yfinance as yf
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_huggingface import HuggingFaceEmbeddings
# import os

# app = Flask(__name__)

# # Load environment variables (for API key)
# # GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# # if not GOOGLE_API_KEY:
# #     raise ValueError("GOOGLE_API_KEY environment variable not set.")

# # ------------------------
# # 1. Load FAISS Model
# # ------------------------

# # Load the embeddings model
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# # Load the FAISS index from saved files
# faiss_index_path = "faiss_index"  # Make sure this path is correct
# try:
#     vector_store = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
#     retriever = vector_store.as_retriever()
# except Exception as e:
#     print(f"Error loading FAISS index: {e}")
#     exit() # Exit if the FAISS index cannot be loaded

# # ------------------------
# # 2. Finance Tool
# # ------------------------

# def get_stock_price(symbol: str) -> str:
#     try:
#         stock = yf.Ticker(symbol)
#         price = stock.history(period="1d")['Close'].iloc[-1]
#         return f"The latest closing price for {symbol.upper()} is ${price:.2f}."
#     except Exception as e:
#         return f"Error fetching stock price for {symbol}: {e}"

# stock_tool = Tool(
#     name="StockPriceChecker",
#     func=get_stock_price,
#     description="Fetches the latest closing price of a stock. Input should be a valid stock ticker symbol (e.g., 'AAPL')."
# )

# # ------------------------
# # 3. LLM Model Setup (Function to create new instance)
# # ------------------------
# def get_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         api_key="AIzaSyDIdDEjglq41x2sKnbqlLKU6dIQ4j9YV-8"
#     )

# # ------------------------
# # 4. RetrievalQA Chain Setup
# # ------------------------
# def get_retrieval_chain():
#     llm = get_llm()  # Get a new LLM instance for the chain
#     return RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type="stuff"
#     )

# retrieval_chain = get_retrieval_chain()

# retrieval_tool = Tool(
#     name="KnowledgeBaseRetriever",
#     func=retrieval_chain.run,
#     description="Fetches information from a knowledge base using the given query."
# )

# # ------------------------
# # 5. Agent Setup (Function to create new instance)
# # ------------------------
# def get_agent():
#     tools = [stock_tool, retrieval_tool]
#     llm = get_llm() # Get a new LLM instance for the Agent
#     return initialize_agent(
#         tools=tools,
#         agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
#         llm=llm,
#         verbose=True
#     )

# # Create the agent outside the route for efficiency.
# agent = get_agent()

# # ------------------------
# # 6. Flask Routes
# # ------------------------

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_input = request.get_json().get("message")
#     print(user_input)
#     if not user_input:
#         return jsonify({"error": "No message provided"}), 400

#     if user_input.lower() in ["exit", "quit"]:
#         return jsonify({"message": "Exiting chatbot. Goodbye!"})

#     try:
#         response = agent.run(user_input)
#         return jsonify({"message": response})
#     except Exception as e:
#         print(f"Error processing request: {e}")
#         return jsonify({"message": "Sorry, I encountered an error processing your request."}), 500  # Return 500 for server errors

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
import yfinance as yf
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables (for API key)
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY environment variable not set.")

# ------------------------
# 1. Load FAISS Model
# ------------------------

# Load the embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Load the FAISS index from saved files
faiss_index_path = "faiss_index"  # Make sure this path is correct
try:
    vector_store = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever()
except Exception as e:
    print(f"Error loading FAISS index: {e}")
    exit() # Exit if the FAISS index cannot be loaded

# ------------------------
# 2. Finance Tool
# ------------------------

def get_stock_price(symbol: str) -> str:
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return f"The latest closing price for {symbol.upper()} is ${price:.2f}."
    except Exception as e:
        return f"Error fetching stock price for {symbol}: {e}"

stock_tool = Tool(
    name="StockPriceChecker",
    func=get_stock_price,
    description="Fetches the latest closing price of a stock. Input should be a valid stock ticker symbol (e.g., 'AAPL')."
)

# ------------------------
# 3. LLM Model Setup (Function to create new instance)
# ------------------------
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key="AIzaSyDIdDEjglq41x2sKnbqlLKU6dIQ4j9YV-8"
    )

# ------------------------
# 4. RetrievalQA Chain Setup
# ------------------------
def get_retrieval_chain():
    llm = get_llm()  # Get a new LLM instance for the chain
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

retrieval_chain = get_retrieval_chain()

retrieval_tool = Tool(
    name="KnowledgeBaseRetriever",
    func=retrieval_chain.run,
    description="Fetches information from a knowledge base using the given query."
)

# ------------------------
# 5. Agent Setup (Function to create new instance)
# ------------------------
def get_agent():
    tools = [stock_tool, retrieval_tool]
    llm = get_llm() # Get a new LLM instance for the Agent
    return initialize_agent(
        tools=tools,
        agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        llm=llm,
        verbose=True
    )

# Create the agent outside the route for efficiency.
agent = get_agent()

# ------------------------
# 6. Flask Routes
# ------------------------

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.get_json().get("message")
    print(user_input)
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    if user_input.lower() in ["exit", "quit"]:
        return jsonify({"message": "Exiting chatbot. Goodbye!"})

    try:
        response = agent.run(user_input)
        return jsonify({"message": response})
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"message": "Sorry, I encountered an error processing your request."}), 500  # Return 500 for server errors

if __name__ == "__main__":
    app.run(debug=True)
