# FAR Chatbot
[//]: # ([![Build Status]&#40;https://travis-ci.com/chyke007/credible.svg?branch=master&#41;]&#40;https://travis-ci.com/chyke007/credible&#41;)
![version](https://img.shields.io/badge/version-0.4.0-blue)
![Python Version](https://img.shields.io/badge/Python-v3.9.x-yellow)

## Development Setup
The `development` branch utilizes Docker containers for development. To get started, clone the repository and run the following commands from within the project directory:
```bash
docker compose build --no-cache
docker compose up
```
Test that the application is running by visiting `http://localhost:8000/api/v1/health` in your browser. This route should return a response `Ok`.

The `Nginx` proxy server runs on port `8000`. It sends traffic to the `Gunicorn` WSGI server that runs on port `9001` (not publicly accessible).

The `redis` instance runs on port `6379`. It stores chat histories.

### Environment Variables
The application uses environment variables for configuration. Create a `.env` file in the root directory and add the following variables (you will need to get some of these from Chris Puzzuoli):
```bash
APP_ENV=development
OPENAI_API_KEY=[your key]
OPENAI_ORGANIZATION=[your organization]
OPENAI_BASE=https://api.umgpt.umich.edu/azure-openai-api
OPENAI_VERSION=[version]
OPENAI_GPT_MODEL=[model]
OPENAI_EMBED_MODEL=text-embedding-ada-002
OPENAI_TYPE=azure
PINECONE_API_KEY=[your key]
PINECONE_ENV=gcp-starter
LANGCHAIN_API_KEY=[your key]
LANGCHAIN_TRACING_V2=true
LDAP_PASS=[ldap password]

# Dev Miserver
DB_HOST=[dev host]
DB_USER=[dev username]
DB_PASS=[dev password]
DB_NAME=far_chatbot_test
DB_PORT=3306