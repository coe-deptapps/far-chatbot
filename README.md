# FAR Chatbot
[//]: # ([![Build Status]&#40;https://travis-ci.com/chyke007/credible.svg?branch=master&#41;]&#40;https://travis-ci.com/chyke007/credible&#41;)
![version](https://img.shields.io/badge/version-0.4.0-blue)
![Python Version](https://img.shields.io/badge/Python-v3.9.x-yellow)

## Development Setup
The `development` branch utilizes Docker containers for development. To get started, clone the repository and run Docker build from within the project directory:
```bash
docker compose build --no-cache
```
On Mac and Linux, you will need to add the path to this directory in Docker in `Settings > Resources > File sharing`. Otherwise you might get an error similar to 
`The path /path/to/far-chatbot is not shared from the host and is not known to Docker.`

### Starting the Docker containers
To start the Docker containers, run the following command:
```bash
docker compose up
```
If this is your first time running the project, you will need to follow the instructions in the "Local Database" and "Local environment variables" sections to create the database schema and set up the environment variables.
Otherwise, you can skip down to the "Running the application" section.

### Local database
<strong>The first time you run the application, you need to create the database schema.</strong>

The copy of the database .sql file that is being used for testing queries for chat accuracy is NOT included in this repo. Ask Chris Puzzuoli for this.

The first time you run this project, also run the following command to copy the schema into the database container:
```bash
docker exec -i ai_db mariadb --user=[user from .env file] --password=[password from .env file] far < /local/path/to/far.sql
```

The local installation uses a Docker container for the database. The database is accessible on your machine on port `3307`.

### Local environment variables
You will need to create a `.env` file in the root of the project directory. The following environment variables are required:
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

# Dev Local (docker container 'db')
DB_ROOT_PASSWORD=secret
DB_CONNECTION=mysql
DB_HOST=db
DB_NAME=far
DB_USER=root
DB_PASS=secret
DB_PORT=3306
```

### Running the application

Test that the application is running by visiting `http://localhost:8000/api/v1/health` in your browser. This route should return a response `Ok`.

The `Nginx` proxy server runs on port `8000`. It sends traffic to the `Gunicorn` WSGI server that runs on port `9001` (not publicly accessible).

The `redis` instance runs on port `6379`. It stores chat histories.