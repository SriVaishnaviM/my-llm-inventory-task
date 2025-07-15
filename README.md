## GenAI-Powered Inventory Management System

### Project Overview

This project implements a two-tiered system for inventory management, featuring a core Inventory Web Service and a Model Control Plane (MCP) Server. The MCP Server leverages Generative AI (specifically Google Gemini) to interpret natural language queries for inventory operations, translating them into structured API calls for the Inventory Web Service.

This solution demonstrates API design, microservice interaction, and the integration of Large Language Models (LLMs) for intuitive user interfaces.

### Project Structure
The repository is organized as follows:

```
.
├── inventory-service/
│   └── main.py              # Inventory Web Service implementation
├── mcp-server/
│   └── main.py              # Model Control Plane (MCP) Server implementation
├── .gitignore               # Specifies intentionally untracked files to ignore by Git
└── README.md                # This documentation file
```
FastAPI automatically generates OpenAPI specifications for both services, accessible at /openapi.json (e.g., http://localhost:8000/openapi.json for the Inventory Service). The interactive documentation (Swagger UI) is available at /docs (e.g., http://localhost:8000/docs).

Setup Instructions
Follow these steps to set up and run the project on your local machine (macOS instructions provided).

#### Prerequisites
1. Python 3.9+
2. Homebrew (recommended for macOS for Python installation)
3. Git

### 1. Clone the Repository

First, clone this GitHub repository to your local machine:

```
git clone https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME].git
cd [YOUR_REPO_NAME] # e.g., cd my-llm-inventory-task
```
### 2. Python Environment Setup
It is highly recommended to use a Python virtual environment to manage dependencies.

```
# Navigate to the project root directory
cd ~/Documents/InternshipTask # Or wherever you cloned the repo

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# IMPORTANT: You must run this command in each new terminal session you open for this project.
source venv/bin/activate
```
### 3. Install Dependencies
With your virtual environment activated, install the required Python packages
```
pip install fastapi uvicorn pydantic httpx
```
### 4. Obtain and Configure Gemini API Key

The MCP Server requires a Google Gemini API key to interact with the Generative AI model.

1. Get your API Key:

Go to Google AI Studio.

Sign in with your Google account.

Create a new API key and copy it immediately.

2. Set as Environment Variable:

- Open your shell configuration file (e.g., .zshrc for zsh, .bash_profile or .bashrc for bash):
```
nano ~/.zshrc # Or ~/.bash_profile
```
- Add the following line to the very end of the file, replacing
- YOUR_ACTUAL_GEMINI_API_KEY_HERE with your copied key:
```
  export GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```
- Save and Exit nano ( Ctrl+O or Ctrl+X)
- Apply the changes to your current terminal:
```
source ~/.zshrc # Or ~/.bash_profile
```
- Crucially, open a BRAND NEW Terminal window/tab
- Verify the key is set in the new terminal: (It should display the API key)
```
    echo $GEMINI_API_KEY
```
## Running the Services
Both services must be running concurrently in separate terminal windows/tabs.

### 1. Run Inventory Web Service
- Open a new Terminal window/tab.

- Activate your virtual environment:
```
source venv/bin/activate
```
- Navigate to the inventory-service directory:
```
cd inventory-service
```
- Start the service: Leave the terminal running
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
### 2. Run Model Control Plane (MCP) Server
- Open another new Terminal window/tab.

- Activate your virtual environment:
```
  source venv/bin/activate
```
- Navigate to the mcp-server directory:
```
  cd mcp-server
```
- Start the service:
```
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
## API Endpoints and Testing

You can test the APIs using curl commands in a third terminal window (with venv activated) or via the interactive Swagger UI in your web browser.

Inventory Web Service (http://localhost:8000)
Access Swagger UI: http://localhost:8000/docs

GET /inventory
Retrieves the current stock levels for tshirts and pants.
```
curl -X GET "http://localhost:8000/inventory" \
     -H "accept: application/json"
```
POST /inventory
Modifies the count of a specific item (tshirts or pants) in the inventory.

- Sell 5 t-shirts:
```
curl -X POST "http://localhost:8000/inventory" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"item": "tshirts", "change": -5}'
```
- Add 10 pants:
```
curl -X POST "http://localhost:8000/inventory" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"item": "pants", "change": 10}'
```
- Test Invalid item
```
curl -X POST "http://localhost:8000/inventory" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"item": "socks", "change": 1}'
```
- Test reducing stock below zero (expected error):
```
curl -X POST "http://localhost:8000/inventory" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"item": "tshirts", "change": -100}'
```
Model Control Plane (MCP) Server (http://localhost:8001)
Access Swagger UI: http://localhost:8001/docs

POST /process_query
Processes a natural language query, interprets it using GenAI, and interacts with the Inventory Service.

- Get current inventory:





  


