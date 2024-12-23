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
from langchain.tools import tool
from pymongo import MongoClient
from bson import ObjectId
from langchain.chains import LLMChain
from langchain_community.utilities import SerpAPIWrapper
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
SERP_API="ff667c4cb40ba9e12a67c8e6aace52c4d33ccab55af97549d0f716154438ca29"
# Load environment variables (for API key)
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY environment variable not set.")

# ------------------------
# 1. Load FAISS Model
# ------------------------

# Load the embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key="AIzaSyBgUML1bdtLTMHPmHJfXNYkNv8HBj_dXg4"
    )
llm=get_llm()
# Load the FAISS index from saved files
faiss_index_path = "faiss_index"  # Make sure this path is correct
try:
    vector_store = FAISS.load_local(faiss_index_path, embeddings
                                    ,allow_dangerous_deserialization=True
                                    )
    retriever = vector_store.as_retriever()
except Exception as e:
    print(f"Error loading FAISS index: {e}")
    exit() # Exit if the FAISS index cannot be loaded

# ------------------------
# 2. Finance Tool
# ------------------------
search = SerpAPIWrapper(serpapi_api_key=SERP_API)
search_tool = Tool(
name="Search",
func=search.run,
description="Use this tool to search the web for up-to-date information on job postings."
)

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

@tool("check_balance")
def check_balance_tool(user_id) -> str:
    """
    Check the balance of a specific user.

    Arguments:
    - user_id: ID of the user

    Returns the balance of the user or an error if not found.
    """
    try:
        user_id=str(user_id).strip()
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return "Error: User not found."
        return f"User ID: {user_id}, Balance: {user['balance']}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    
    

prompt_template = """
You are a financial advisor with extensive knowledge of investing, financial planning, and budgeting.
Answer the following query with sound financial advice:

Query: {query}

Response:
"""

# Create a Langchain prompt template
prompt = PromptTemplate(input_variables=["query"], template=prompt_template)

# Create an LLM chain
llm_chain = LLMChain(llm=llm, prompt=prompt)

# Define a tool using the LLM chain
@tool("generate_financial_advice")
def financial_advice_tool(query: str):
    """
    This tool generates financial advice based on a user's query.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The financial query from the user.

    Returns:
    str: The financial advice generated by the LLM.
    """
    return llm_chain.run(query)

# ------------------------
# 3. LLM Model Setup (Function to create new instance)
# ------------------------
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
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

# Initialize the OpenAI LLM
# Define a budgeting advice tool
@tool("generate_budgeting_advice")
def budgeting_advice_tool(query: str):
    """
    This tool generates advice on creating and managing a budget.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The budgeting-related query from the user.

    Returns:
    str: The budgeting advice generated by the LLM.
    """
    budgeting_prompt_template = """
    You are a budgeting expert with deep knowledge of personal finance. 
    Provide step-by-step advice to address the following query:

    Query: {query}

    Response:
    """
    budgeting_prompt = PromptTemplate(input_variables=["query"], template=budgeting_prompt_template)
    budgeting_llm_chain = LLMChain(llm=llm, prompt=budgeting_prompt)
    return budgeting_llm_chain.run(query)

@tool("generate_investment_advice")
def investment_advice_tool(query: str):
    """
    This tool generates investment advice based on the user's financial goals.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The investment-related query from the user.

    Returns:
    str: The investment advice generated by the LLM.
    """
    investment_prompt_template = """
    You are an investment strategist with expertise in diverse markets. 
    Provide clear and actionable advice for the following query:

    Query: {query}

    Response:
    """
    investment_prompt = PromptTemplate(input_variables=["query"], template=investment_prompt_template)
    investment_llm_chain = LLMChain(llm=llm, prompt=investment_prompt)
    return investment_llm_chain.run(query)

@tool("generate_retirement_plan")
def retirement_planning_tool(query: str):
    """
    This tool helps users create a retirement plan based on their current situation.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The retirement planning query from the user.

    Returns:
    str: The retirement plan advice generated by the LLM.
    """
    retirement_prompt_template = """
    You are a retirement planning specialist. Assist with the following query:

    Query: {query}

    Response:
    """
    retirement_prompt = PromptTemplate(input_variables=["query"], template=retirement_prompt_template)
    retirement_llm_chain = LLMChain(llm=llm, prompt=retirement_prompt)
    return retirement_llm_chain.run(query)

@tool("generate_debt_management_advice")
def debt_management_tool(query: str):
    """
    This tool provides advice on managing and paying off debts efficiently.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The debt-related query from the user.

    Returns:
    str: The debt management advice generated by the LLM.
    """
    debt_prompt_template = """
    You are a debt management advisor with expertise in handling loans and credit. 
    Provide detailed advice for the following query:

    Query: {query}

    Response:
    """
    debt_prompt = PromptTemplate(input_variables=["query"], template=debt_prompt_template)
    debt_llm_chain = LLMChain(llm=llm, prompt=debt_prompt)
    return debt_llm_chain.run(query)

@tool("generate_tax_advice")
def tax_advice_tool(query: str):
    """
    This tool provides advice on optimizing taxes and understanding tax regulations.
    It processes the query using a pre-defined prompt and returns 
    the response generated by the LLM.

    Args:
    query (str): The tax-related query from the user.

    Returns:
    str: The tax optimization advice generated by the LLM.
    """
    tax_prompt_template = """
    You are a tax advisor with extensive knowledge of tax laws and optimization strategies. 
    Provide guidance for the following query:

    Query: {query}

    Response:
    """
    tax_prompt = PromptTemplate(input_variables=["query"], template=tax_prompt_template)
    tax_llm_chain = LLMChain(llm=llm, prompt=tax_prompt)
    return tax_llm_chain.run(query)


# Add tools to LangChain
tools = [
    Tool(name="Check Balance", func=check_balance_tool, description="Check the balance of a user."),
    Tool(name="Generate Financial Advice", func=financial_advice_tool, description="Generate responses to user queries."),
    Tool(name="Generate Budgeting Advice", func=budgeting_advice_tool, description="Generate advice on creating and managing a budget."),
    Tool(name="Generate Investment Advice", func=investment_advice_tool, description="Generate advice on investment strategies."),
    Tool(name="Generate Retirement Plan", func=retirement_planning_tool, description="Help users create a retirement plan based on their current situation."),
    Tool(name="Generate Debt Management Advice", func=debt_management_tool, description="Provide advice on managing and paying off debts."),
    Tool(name="Generate Tax Advice", func=tax_advice_tool, description="Provide advice on optimizing taxes and understanding tax regulations."),
    retrieval_tool,
    stock_tool,
    search_tool
]

# ------------------------
# 5. Agent Setup (Function to create new instance)
# ------------------------
def get_agent():
    # tools = [stock_tool, retrieval_tool]
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


@app.route('/registerUser', methods=['POST'])
def registerUser():
    try:
        # Extract data from the request
        user_data = request.json
        
        # Validate required fields
        required_fields = ["user_name", "embeddings", "password"]
        for field in required_fields:
            if field not in user_data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Check if the user already exists
        existing_user = users_collection.find_one({"user_name": user_data["username"]})
        if existing_user:
            return jsonify({"error": "User with this email already exists."}), 409

        # Insert user into the database
        new_user = {
            "username": user_data["username"],
            "embeddings": user_data["embeddings"],
            "password": user_data["password"]  # Consider hashing passwords in a real application
        }
        users_collection.insert_one(new_user)

        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
                "_id": user_id # Include user_id in the response
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
                "user_id": user_id # Include user_id in the response
            }), 200
        else:
            return jsonify({"success": False, "message": "Face does not match the stored data."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred during verification: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=False)