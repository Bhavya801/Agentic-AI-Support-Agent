AI-Powered Customer Support Agent
This project is an automated AI agent that processes incoming customer support emails, analyzes them using the Gemini API, and takes a corresponding action:

Replies with an automated response for simple queries.

Escalate the issue to a human agent by creating a Trello card for complex or sensitive cases.

Logs all interactions and decisions to a Firebase Firestore database.

Leverages Typesense for high-speed, semantic search and contextual understanding.

The application is designed to be run as a stateless cron job.

Getting Started
1. Prerequisites
Python 3.9+

A Gemini API key

A Trello account, API key, and token

A Firebase project with Firestore enabled and a service account JSON file

An email account with IMAP enabled and an App Password

A running Typesense instance

2. Installation
Clone the repository and install the dependencies:

git clone https://github.com/Bhavya801/Agentic-AI-Support-Agent
cd ai-support-agent
pip install -r requirements.txt



3. Configuration
Create a .env file in the root directory and populate it with your credentials:

cp .env.example .env



Open the .env file and replace the placeholder values. Ensure the FIREBASE_CONFIG_PATH points to your downloaded service account JSON file and add your Typesense connection details.

Running the Cron Job
You can test the script by running it directly from your terminal:

python main.py



To schedule it as a cron job, add the following line to your crontab. This example runs the agent every 5 minutes:

*/5 * * * * cd /path/to/your/ai-support-agent && python3 main.py >> /var/log/ai-agent.log 2>&1



Note: Adjust the path cd /path/to/your/ai-support-agent to your project's absolute path.

Running the API
If you want to run the application as a web service, you can use Uvicorn. The uvicorn command below will start the server on all available network interfaces at port 3218:

uvicorn main:app --host 0.0.0.0 --port 3218



API Documentation
The project's internal logic and interactions are documented using an OpenAPI specification in docs/redoc_spec.json. You can use a tool like Redocly or a similar service to generate a professional, interactive documentation page from this file