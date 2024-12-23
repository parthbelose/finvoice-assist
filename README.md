# Finvoice Assist
**A Voice-Based AI Customer Care for the Visually Impaired**

Finvoice Assist is an innovative application designed to help visually impaired individuals interact with customer care systems through voice commands. The platform leverages artificial intelligence (AI) and voice recognition technology to provide a seamless, accessible, and efficient experience for users. It enables users to handle tasks like checking account balances, managing transactions, and requesting support—all via voice.

## Features

- **Voice Recognition**: Allows users to communicate with the system through voice commands.
- **AI-Powered Assistance**: An intelligent assistant that can respond to queries and perform tasks based on user commands.
- **Accessibility**: Specifically designed for visually impaired users, ensuring that the system is intuitive and easy to navigate using voice alone.
- **Secure Authentication**: Users can authenticate using biometric data, ensuring a secure and personalized experience.
- **Customizable**: Support for various customer care tasks such as account information, transaction queries, and more.

## Technology Stack

- **Backend**: Python (Flask)
- **Voice Recognition**: Web Speech API (SpeechRecognition), Google Speech-to-Text
- **AI**: Custom AI/ML models for voice processing and response generation
- **Database**: MongoDB (for storing user data, queries, responses, etc.)
- **Frontend**: HTML, CSS, JavaScript (for interacting with the web application)
- **Speech Synthesis**: Google Text-to-Speech API

## How It Works

1. **User Authentication**: The system starts by authenticating the user through biometric data or a secure login process.
2. **Voice Command Input**: Once authenticated, users can speak commands such as "Check my balance," "Pay my bill," or "Talk to an agent."
3. **AI Processing**: The AI processes the speech input, uses natural language processing (NLP) to understand the command, and interacts with the backend to retrieve data or execute tasks.
4. **Response**: The system provides a voice response or takes action (e.g., making a transaction, fetching account details).
5. **Feedback**: If the user needs further assistance or clarification, they can continue issuing commands, and the system will respond accordingly.

## Installation

### Prerequisites

- **Python 3.x** installed on your system
- **MongoDB** for storing user and transaction data
- **Node.js** and **npm** for running front-end dependencies
- **Google Cloud API** key for speech-to-text and text-to-speech services (optional for advanced features)


## Installation

### Backend Setup

1. **Create a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

2. **Install the backend dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up MongoDB connection** in your environment variables (or `config.py`):
    ```bash
    export MONGO_URI="your-mongo-uri"
    ```

4. **Run the Flask server**:
    ```bash
    flask run
    ```
    The server will be available at `http://localhost:5000`.

### Frontend Setup

1. **Install front-end dependencies**:
    ```bash
    npm install
    ```

2. **Serve the frontend**:
    ```bash
    npm start
    ```
    The front-end app will be available at `http://localhost:3000`.

### Google Cloud APIs

If you're using Google Cloud's Text-to-Speech and Speech-to-Text APIs:

1. **Create a project** in the Google Cloud Console.
2. **Enable the Speech-to-Text and Text-to-Speech APIs**.
3. **Set up authentication** and download your service account key file (JSON).
4. **Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable** to the path of your service account key.

---

## Usage

1. **Sign Up**: Register by providing the necessary details (name, email, password).
2. **Log In**: Use your credentials to log in or authenticate via biometric data.
3. **Voice Interaction**: Speak your request to the system (e.g., "Check my balance," "Transfer funds").
4. **AI Assistant**: The system will process your command, retrieve the requested information, or perform the task.
5. **Error Handling**: If the system cannot process the command, it will request clarification or provide suggestions.

---

## Contributing

We welcome contributions from the community! Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request on GitHub.

---

## Acknowledgments

- Special thanks to the open-source libraries and APIs used in this project:
  - Google Speech-to-Text and Text-to-Speech APIs
  - Flask (for the backend)
  - MongoDB (for data storage)
  - Web Speech API (for voice recognition)
- All contributors who help improve the accessibility of technology for visually impaired users.

---
Special thanks to the open-source libraries and APIs used in this project:
Google Speech-to-Text and Text-to-Speech APIs
Flask (for the backend)
MongoDB (for data storage)
Web Speech API (for voice recognition)
All contributors who help improve the accessibility of technology for visually impaired users.
