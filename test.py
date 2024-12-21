from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import os

app = Flask(__name__)

# MongoDB connection using your Atlas URI
mongo_uri = os.getenv(
    "MONGO_URI", 
    "mongodb+srv://kartikgupta9867:123%40Password@cluster0.5vo6s.mongodb.net/"
)
client = MongoClient(mongo_uri)

# Access the database and collections
db = client["banking_system"]
users_collection = db["users"]
transactions_collection = db["transactions"]

# MongoDB Schemas
# User Schema
# {
#     "_id": ObjectId,
#     "name": str,
#     "balance": float
# }

# Transaction Schema
# {
#     "_id": ObjectId,
#     "type": str,  # e.g., "bill_payment", "transfer"
#     "amount": float,
#     "sender": ObjectId,  # Reference to users._id
#     "receiver": ObjectId,  # Reference to users._id or None for bill payments
#     "timestamp": datetime
# }

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json
    print(data)
    # Validate the input
    name = data.get("name")
    balance = data.get("balance")
    
    if not name or not isinstance(balance, (int, float)):
        return jsonify({"error": "Invalid input. Please provide 'name' and 'balance'."}), 400
    
    # Create the new user document
    new_user = {
        "name": name,
        "balance": balance
    }
    
    # Insert the new user into the 'users' collection
    result = users_collection.insert_one(new_user)
    
    # Return a response with the new user's information
    return jsonify({
        "message": "User added successfully.",
        "user_id": str(result.inserted_id),
        "name": name,
        "balance": balance
    }), 201


@app.route("/check_balance/<user_id>", methods=["GET"])
def check_balance(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": user_id, "balance": user["balance"]})


@app.route("/pay_bill", methods=["POST"])
def pay_bill():
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount")
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Deduct balance and log transaction
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$inc": {"balance": -amount}})
    transaction = {
        "type": "bill_payment",
        "amount": amount,
        "sender": ObjectId(user_id),
        "receiver": None,
        "timestamp": datetime.datetime.now()
    }
    transactions_collection.insert_one(transaction)
    
    return jsonify({"message": "Bill paid successfully", "new_balance": user["balance"] - amount})


@app.route("/transfer_money", methods=["POST"])
def transfer_money():
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    amount = data.get("amount")
    
    sender = users_collection.find_one({"_id": ObjectId(sender_id)})
    receiver = users_collection.find_one({"_id": ObjectId(receiver_id)})
    
    if not sender or not receiver:
        return jsonify({"error": "Sender or receiver not found"}), 404
    
    if sender["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Perform transfer
    users_collection.update_one({"_id": ObjectId(sender_id)}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"_id": ObjectId(receiver_id)}, {"$inc": {"balance": amount}})
    
    transaction = {
        "type": "transfer",
        "amount": amount,
        "sender": ObjectId(sender_id),
        "receiver": ObjectId(receiver_id),
        "timestamp": datetime.datetime.now()
    }
    transactions_collection.insert_one(transaction)
    
    return jsonify({"message": "Transfer successful", "new_balance": sender["balance"] - amount})


if __name__ == "__main__":
    app.run(debug=True)
