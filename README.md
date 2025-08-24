AI-Powered Customer Support Agent
This project is an automated AI agent that processes incoming customer support emails, analyzes them using the Gemini API, and takes a corresponding action:

Replies with an automated response for simple queries.

Escalates the issue to a human agent by creating a Trello card for complex or sensitive cases.

Logs all interactions and decisions to a Firebase Firestore database.

The application is designed to be run as a stateless cron job.

 Getting Started
1. Prerequisites
Python 3.9+

A Gemini API key

A Trello account, API key, and token

A Firebase project with Firestore enabled and a service account JSON file

An email account with IMAP enabled and an App Password

2. Installation
Clone the repository and install the dependencies:

git clone <your-repo-url>
cd ai-support-agent
pip install -r requirements.txt

3. Configuration
Create a .env file in the root directory and populate it with your credentials:

cp .env.example .env

Open the .env file and replace the placeholder values. Ensure the FIREBASE_CONFIG_PATH points to your downloaded service account JSON file.

4. Running the Cron Job
You can test the script by running it directly from your terminal:

python main.py

To schedule it as a cron job, add the following line to your crontab. This example runs the agent every 5 minutes:

*/5 * * * * cd /path/to/your/ai-support-agent && python3 main.py >> /var/log/ai-agent.log 2>&1

Note: Adjust the path cd /path/to/your/ai-support-agent to your project's absolute path.

5. Dockerization (Optional)
You can containerize the application for easier deployment:

# Build the Docker image
docker build -t ai-support-agent .

# Run the container (you'll need to pass environment variables)
docker run --rm --env-file ./.env ai-support-agent

6. API Documentation
The project's internal logic and interactions are documented using an OpenAPI specification in docs/redoc_spec.json. You can use a tool like Redocly or a similar service to generate a professional, interactive documentation page from this file.

# Example command using Redocly to generate static HTML
npx @redocly/cli build-docs docs/redoc_spec.json -o docs/index.html
