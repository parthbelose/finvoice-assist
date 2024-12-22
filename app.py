# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)

# # Route for the login page
# @app.route('/login')
# def login():
#     return render_template('login.html')

# # Route for the home page
# @app.route('/home')
# def home():
#     return render_template('home.html')

# # Route for the signup page
# @app.route('/signup')
# def signup():
#     return render_template('signUp.html')

# # Optional: Example API endpoint for chatbot interaction in home.html
# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     message = data.get('message', '')
#     # Generate a dummy response for now
#     response = {"message": f"Received: {message}"}
#     return jsonify(response)

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, jsonify,render_template
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
import numpy as np
from pymongo import MongoClient
from bson import ObjectId

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
    vector_store = FAISS.load_local(faiss_index_path, embeddings)
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
mongo_uri = "mongodb+srv://kartikgupta9867:123%40Password@cluster0.5vo6s.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["test"]
users_collection = db["embeddings"]

def calculate_distance(embedding1, embedding2):
    return np.linalg.norm(np.array(embedding1) - np.array(embedding2))

# ------------------------
# 6. Flask Routes
# ------------------------
@app.route('/login')
def login():
    return render_template('login.html')

# Route for the home page
@app.route('/home')
def home():
    return render_template('home.html')

# Route for the signup page
@app.route('/signup')
def signup():
    return render_template('signUp.html')

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
@app.route('/verify_face', methods=['POST'])
def verify_user():
    data = request.get_json()
    user_name = data.get("user_name").strip()
    input_embedding = data.get("embedding")
    # input_password = data.get("password")

    if not user_name or not input_embedding:
        return jsonify({"success": False, "message": "User name, password, and face embedding are required."}), 400

    try:
        user = users_collection.find_one({"user_name": user_name})

        if not user:
            return jsonify({"success": False, "message": f"User name '{user_name}' not found in the database."}), 404

        # stored_password = user.get("password")
        # if stored_password != input_password:
        #     return jsonify({"success": False, "message": "Invalid password."}), 401

        stored_embedding = user.get("embedding")
        if not stored_embedding:
            return jsonify({"success": False, "message": "No face embedding found for the user."}), 404

        if len(input_embedding) != len(stored_embedding):
            return jsonify({"success": False, "message": "Face embedding sizes do not match."}), 400

        distance = calculate_distance(input_embedding, stored_embedding)
        threshold = 0.6

        if distance < threshold:
            user_id = str(user["_id"])  # Convert ObjectId to string
            return jsonify({
                "success": True,
                "message": f"Face matched for user {user_name}.",
                "user_name": user_name,
                "user_id": user_id  # Include user_id in the response
            }), 200
        else:
            return jsonify({"success": False, "message": "Face does not match the stored data."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred during verification: {str(e)}"}), 500

@app.route('/verify_password', methods=['POST'])
def verify_password():
    data = request.get_json()
    user_name = data.get("user_name").strip()
    input_password = data.get("password").strip()
    # input_password = data.get("password")

    if not user_name or not input_password:
        return jsonify({"success": False, "message": "User name, password, and face embedding are required."}), 400

    try:
        user = users_collection.find_one({"user_name": user_name})

        if not user:
            return jsonify({"success": False, "message": f"User name '{user_name}' not found in the database."}), 404

        stored_password = user.get("password")
        if stored_password == input_password:
            user_id = str(user["_id"])  # Convert ObjectId to string
            return jsonify({
                "success": True,
                "message": f"Password matched for user {user_name}.",
                "user_name": user_name,
                "user_id": user_id  # Include user_id in the response
            }), 200
        else:
            return jsonify({"success": False, "message": "Face does not match the stored data."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred during verification: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
