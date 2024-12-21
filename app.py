from flask import Flask, request, jsonify
import numpy as np
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = "mongodb+srv://kartikgupta9867:123%40Password@cluster0.5vo6s.mongodb.net/"  # Replace with your MongoDB URI
client = MongoClient(mongo_uri)
db = client["test"]  # Use your database name
users_collection = db["embeddings"]  # Use your collection name

def calculate_distance(embedding1, embedding2):
    """
    Calculate the Euclidean distance between two embeddings.
    """
    return np.linalg.norm(np.array(embedding1) - np.array(embedding2))

@app.route('/verify', methods=['POST'])
def verify_user():
    """
    Verify user by checking user_name, password, and then matching face embedding.
    """
    data = request.get_json()  # Get input data from the frontend
    print(data)
    
    user_name = data.get("user_name").strip()  # Strip any leading or trailing spaces
    input_embedding = data.get("embedding")
    input_password = data.get("password")

    # Validate input from the frontend
    if not user_name or not input_password or not input_embedding:
        return jsonify({"success": False, "message": "User name, password, and face embedding are required."}), 400

    try:
        # Log the user_name being queried
        print(f"Searching for user with user_name: {user_name}")
        
        # Check if the user exists in the database using user_name
        user = users_collection.find_one({"user_name": user_name})

        if not user:
            return jsonify({"success": False, "message": f"User name '{user_name}' not found in the database."}), 404

        # Verify password (plaintext check)
        stored_password = user.get("password")  # Assuming password is stored as plaintext
        if stored_password != input_password:
            return jsonify({"success": False, "message": "Invalid password."}), 401

        # Verify face embedding
        stored_embedding = user.get("embedding")
        if not stored_embedding:
            return jsonify({"success": False, "message": "No face embedding found for the user."}), 404

        # Check if embeddings are of the same size
        if len(input_embedding) != len(stored_embedding):
            return jsonify({"success": False, "message": "Face embedding sizes do not match."}), 400

        # Calculate the distance between the input embedding and stored embedding
        distance = calculate_distance(input_embedding, stored_embedding)
        threshold = 0.6  # Define a suitable threshold for face matching

        # Check if the face matches the stored data
        if distance < threshold:
            return jsonify({"success": True, "message": f"Face matched for user {user_name}.", "user_name": user_name}), 200
        else:
            return jsonify({"success": False, "message": "Face does not match the stored data."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred during verification: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
