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

The `Nginx` proxy server runs on port `8080`. It sends traffic to the `Gunicorn` WSGI server that runs on port `9001` (not publicly accessible).

The `redis` instance runs on port `6379`. It stores chat histories.

### TODO

1. Figure out what aspects of langchain to keep for prod