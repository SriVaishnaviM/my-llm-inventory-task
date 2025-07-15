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

- Go to Google AI Studio.

- Sign in with your Google account.

   - Create a new API key and copy it immediately.
   - Gemini API: AIzaSyA1CZDReoxHPTSd_BP9qFGsSo1WpiDH3aE (used for this project)

2. Set as Environment Variable:

- Open your shell configuration file (e.g., .zshrc for zsh, .bash_profile or .bashrc for bash):
```
nano ~/.zshrc # Or ~/.bash_profile
```
- Add the following line to the very end of the file, replacing YOUR_ACTUAL_GEMINI_API_KEY_HERE with your copied key:
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
- Open a new Terminal window/tab and activate your virtual environment:
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
```
  curl -X POST "http://localhost:8001/process_query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "How many pants and shirts do I have?"}'
```
- Sell 2 t-shirts:

```
  curl -X POST "http://localhost:8001/process_query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "I sold two t-shirts"}'
```
- Add 7 pants
```
  curl -X POST "http://localhost:8001/process_query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "Add 7 pants to the stock"}'
```
- Check stock of a specific item:
```
curl -X POST "http://localhost:8001/process_query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the current stock of tshirts?"}'
```
- Test an unsupported query (expected error):
```
curl -X POST "http://localhost:8001/process_query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "I want to buy a spaceship."}'
```
## Output Screenshots

The screenshots attached below shows brief execution of the code on the local host 

### 1. Inventory Web Service

![Screenshot of Inventory Web Service API Documentation](https://raw.githubusercontent.com/SriVaishnaviM/my-llm-inventory-task/main/result_images/Inventory%20Web%20Service%202.png)

![Screenshot of Inventory Web Service API Documentation](https://raw.githubusercontent.com/SriVaishnaviM/my-llm-inventory-task/main/result_images/Inventory%20Web%20Service%201.png)

![Screenshot of Inventory Web Service API Documentation](https://raw.githubusercontent.com/SriVaishnaviM/my-llm-inventory-task/main/result_images/Inventory%20Web%20Sevice%203.png)

### 2. MCP-Server

After performing Curl operations in the demo the number of t-shirts:9 and pants:25

![Screenshot of MCP Server API Documentation](https://raw.githubusercontent.com/SriVaishnaviM/my-llm-inventory-task/main/result_images/MCP-Server%201.png)

![Screenshot of MCP Server API Documentation](https://raw.githubusercontent.com/SriVaishnaviM/my-llm-inventory-task/main/result_images/MCP-SERVER%202.png)


## Design Choices and Reasoning

- Why Python and FastAPI?

  - FastAPI's High Performance: Built on top of Starlette for web and Pydantic for data, FastAPI achieves high performance on par with Node.js and Go. This is well-suited for high-throughput API services.

  - Ease of Use & Rapid Development: FastAPI provides a modern, straightforward, and developer-friendly experience with minimal boilerplate, accelerating API development.

  - Automatic OpenAPI/Swagger UI Generation: It features an automatic generation of interactive API documentation (Swagger UI at /docs) and machine-readable OpenAPI specifications (/openapi.json). This makes it much easier for API understanding, testing, as well as integration by human developers and other services.

  - Strong Type Hinting with Pydantic: Pydantic models are used for data validation and serialization/deserialization, which includes strong data handling, explicit API contracts, and fewer runtime errors.

  - Asynchronous Capabilities: FastAPI supports async/await natively, which is essential for I/O-bound operations efficiently, such as non-blocking HTTP requests to external services like the Gemini LLM or the Inventory Service.

- Why Google Gemini API?

  - Powerful Natural Language Understanding: Gemini excels at interpreting complex natural language queries and extracting structured information from them.

  - Structured Output Enforcement (responseSchema): A key capability utilized is the responseSchema feature within the Gemini API's generationConfig. This allows the MCP server to explicitly request the LLM to return its interpretation in a predefined JSON format (e.g., specifying operation, item, change). This is vital for reliably translating unstructured user queries into actionable, programmatic commands.
  -  Performance for Intent Recognition: Gemini 2.0 Flash offers a good balance of speed and capability for this specific task of intent recognition and parameter extraction, making it suitable for real-time API interactions.

- Leveraging OpenAPI (FastAPI's Automatic Documentation):
   - FastAPI inherently provides comprehensive API documentation through the OpenAPI specification.
   - The /docs endpoint renders an interactive Swagger UI, allowing developers to visually explore all endpoints, understand request/response schemas, and even execute API calls directly from the browser.
   - The /openapi.json endpoint provides a machine-readable JSON representation of the API. This acts as a formal contract, enabling automated tools (like code generators, API gateways, or even other microservices) to understand and interact with the API without manual parsing. This significantly improves discoverability and integration efficiency.

- Object-Oriented Programming (OOP) Concepts:
   - Application Object: The app = FastAPI(...) instance serves as the central object representing the web application, encapsulating its routes, middleware, and configuration.
   - Pydantic Models (BaseModel): Classes like InventoryResponse, InventoryUpdateRequest, NaturalLanguageQuery, and MCPResponse are direct applications of OOP. They define clear, reusable data structures with type hints, acting as schemas for API request and response bodies. This promotes data integrity, readability, and maintainability by clearly separating data definitions from business logic.
   - Modular Functions: Each API endpoint (get_inventory, update_inventory, process_natural_language_query) and helper function (call_gemini_llm) is encapsulated within its own function, each responsible for a specific task. This modularity enhances code organization, reusability, and testability.

- Prompt Design for LLM Interaction:

  - The llm_prompt in mcp-server/main.py is meticulously crafted to guide the LLM's behavior.
  - Clear Role Assignment: The prompt explicitly tells the LLM its function: "an intelligent assistant that converts natural language inventory requests into structured JSON commands."
  - Specific Instructions and Constraints: It defines the exact fields (operation, item, change, reasoning) and their allowed values (e.g., operation as "GET" or "POST", item as "tshirts" or "pants"), ensuring the LLM's output is predictable and parseable.
  - Few-Shot Examples: Providing multiple concrete examples of user queries and their corresponding desired JSON responses is crucial for "few-shot learning." This significantly improves the LLM's ability to accurately interpret new, unseen queries and consistently generate the correct structured output, even with variations in phrasing.
  - JSON Schema Enforcement: The responseSchema in the Gemini API call reinforces the prompt's instructions by programmatically enforcing the desired JSON structure, making the LLM's output highly reliable for downstream processing.

- MCP Server Logic Flow:
   - Input Reception: The MCP server receives a natural language query from the client via its /process_query endpoint.
   - LLM Interpretation: It constructs a detailed prompt, incorporating the user's query, and sends this to the call_gemini_llm helper function.
   - Action Determination: The call_gemini_llm function interacts with the Google Gemini API, which returns a structured JSON object (thanks to responseSchema) containing the intended operation (GET/POST), item, change, and reasoning.
   - Inventory Service Interaction: Based on the LLM's interpreted operation and parameters, the MCP server then makes a precise HTTP request to the local Inventory Web Service (either a GET /inventory or a POST /inventory with the relevant item and change amount).
   - Response Generation: Finally, the MCP server compiles the result from the Inventory Service (or an appropriate error message) into an MCPResponse object, providing a clear message and the inventory_state to the original client.
   - Robust Error Handling: Comprehensive try-except blocks are implemented throughout to gracefully handle potential issues such as network connectivity problems, errors returned by the Gemini API, malformed LLM responses, or errors from the Inventory Service.

## Known Limitations
  
This project is a functional prototype and has certain limitations:
  - In-Memory Data Store: The inventory data is stored in memory and will reset to its initial state (tshirts: 20, pants: 15) whenever the inventory-service is restarted. For production, a persistent database (e.g., PostgreSQL, MongoDB, SQLite) would be required.
  - Limited Item Support: The system currently only supports 'tshirts' and 'pants' as inventory items, as per the task requirements. Extending this would involve updating both the Inventory Service and the LLM's prompt/schema.
  - LLM Interpretation Variability: While prompt engineering helps, LLMs can occasionally misinterpret highly ambiguous, very complex, or out-of-scope natural language queries. Robust production systems might require more sophisticated fallback mechanisms or human-in-the-loop validation.
  - Basic Error Handling: The error handling is functional but could be enhanced for a production environment (e.g., more specific error codes, custom error responses, comprehensive logging, and monitoring).
  - No Authentication/Authorization: Neither API has any security measures (authentication or authorization) implemented. For a real-world application, secure access control would be paramount.
  - No Dynamic API Discovery: The MCP server is hardcoded with the Inventory Service's URL and endpoint structure. In a more complex microservice architecture, dynamic service discovery or reading the Inventory Service's OpenAPI spec at runtime could be considered for greater flexibility.


  


