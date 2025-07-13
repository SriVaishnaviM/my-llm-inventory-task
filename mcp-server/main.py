# mcp-server/main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict
import httpx # For making HTTP requests to the Inventory Service
import json # To parse JSON response from LLM
import os # For environment variables (API Key)

# --- Configuration ---
# Replace with the actual URL of your Inventory Web Service
# If running locally, ensure the inventory-service is running on this host and port.
INVENTORY_SERVICE_BASE_URL = "http://localhost:8000"

# Gemini API Key - IMPORTANT: Replace with your actual API key or set as an environment variable
# It's recommended to use environment variables for sensitive information.
# Example: export GEMINI_API_KEY="YOUR_API_KEY_HERE"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") # Fallback to empty string if not set

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set. Please set it for LLM functionality.")
    print("You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey")


# Initialize the FastAPI application for the MCP server
app = FastAPI(
    title="MCP (Model Control Plane) Server",
    description="A GenAI-powered interface to convert natural language into inventory operations.",
    version="1.0.0",
)

# --- GLOBAL LLM PROMPT DEFINITION ---
# Moved outside the function to ensure it's always defined and accessible.
llm_prompt = """
You are an intelligent assistant that converts natural language inventory requests into structured JSON commands for an Inventory Management System.
The inventory system manages only two items: 'tshirts' and 'pants'.

Your task is to determine the 'operation' (GET or POST), the 'item' (if applicable), and the 'change' amount (if applicable) based on the user's query.
If the operation is 'GET', 'item' and 'change' should be null.
If the operation is 'POST', 'item' and 'change' are required.
Always provide a 'reasoning' for your decision.

Here are some examples:

User Query: "I sold 3 t shirts"
JSON Response: {{"operation": "POST", "item": "tshirts", "change": -3, "reasoning": "User indicates selling, which means reducing stock. Item is 'tshirts', amount is 3."}}

User Query: "Add 5 pants"
JSON Response: {{"operation": "POST", "item": "pants", "change": 5, "reasoning": "User indicates adding stock. Item is 'pants', amount is 5."}}

User Query: "How many pants and shirts do I have?"
JSON Response: {{"operation": "GET", "item": null, "change": null, "reasoning": "User is asking for current stock levels, which is a GET operation."}}

User Query: "What's the stock of tshirts?"
JSON Response: {{"operation": "GET", "item": "tshirts", "change": null, "reasoning": "User is asking for the stock of a specific item, which is a GET operation."}}

User Query: "Increase tshirts by 10"
JSON Response: {{"operation": "POST", "item": "tshirts", "change": 10, "reasoning": "User wants to increase stock. Item is 'tshirts', amount is 10."}}

User Query: "Reduce pants by 2"
JSON Response: {{"operation": "POST", "item": "pants", "change": -2, "reasoning": "User wants to reduce stock. Item is 'pants', amount is 2."}}

User Query: "Check inventory"
JSON Response: {{"operation": "GET", "item": null, "change": null, "reasoning": "User is asking for general inventory status, which is a GET operation."}}

User Query: "{user_query}"
JSON Response:
"""


# --- Pydantic Models for Request and Response Bodies ---

class NaturalLanguageQuery(BaseModel):
    """
    Pydantic model for the POST /process_query request.
    Takes a natural language string from the user.
    """
    query: str = Field(..., description="The natural language query for inventory management (e.g., 'I sold 3 t shirts', 'How many pants do I have?').")

class MCPResponse(BaseModel):
    """
    Pydantic model for the MCP server's response.
    Can return either the inventory state or a message.
    """
    message: str = Field(None, description="A human-readable message about the operation.")
    inventory_state: dict = Field(None, description="The current state of the inventory after the operation, if applicable.")
    error: str = Field(None, description="Error message if the operation failed.")

# --- Helper Function for LLM Interaction ---

async def call_gemini_llm(prompt: str) -> Dict:
    """
    Calls the Gemini LLM with the given prompt and returns the parsed JSON response.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable."
        )

    chat_history = []
    chat_history.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "contents": chat_history,
        "generationConfig": {
            "responseMimeType": "application/json", # Requesting JSON output
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "operation": {"type": "STRING", "enum": ["GET", "POST"]},
                    "item": {"type": "STRING", "enum": ["tshirts", "pants"], "nullable": True},
                    "change": {"type": "INTEGER", "nullable": True},
                    "reasoning": {"type": "STRING"} # LLM's reasoning for its decision
                },
                "required": ["operation", "reasoning"]
            }
        }
    }

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                api_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30.0 # Set a timeout for the LLM call
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            result = response.json()

            # --- DEBUGGING PRINTS ---
            print(f"DEBUG: Raw LLM API result from response.json(): {json.dumps(result, indent=2)}")

            if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                llm_response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"DEBUG: Extracted LLM response text (should be JSON string): {llm_response_text}")
                try:
                    parsed_json = json.loads(llm_response_text)
                    print(f"DEBUG: Successfully parsed LLM JSON: {json.dumps(parsed_json, indent=2)}")
                    return parsed_json
                except json.JSONDecodeError as e:
                    print(f"ERROR: JSONDecodeError - LLM response text was not valid JSON: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to parse JSON response from LLM. LLM returned malformed JSON. Raw text: {llm_response_text}"
                    )
            else:
                print(f"ERROR: LLM response did not contain expected 'candidates' structure. Raw result: {json.dumps(result, indent=2)}")
                raise ValueError(f"LLM response did not contain expected content structure. Raw result: {json.dumps(result, indent=2)}")

        except httpx.RequestError as exc:
            print(f"ERROR: httpx.RequestError - Failed to connect to Gemini API: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Gemini API: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            print(f"ERROR: httpx.HTTPStatusError - Gemini API returned an error: {exc.response.status_code} - {exc.response.text}")
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Gemini API returned an error: {exc.response.text}"
            )
        except HTTPException as e:
            # Re-raise HTTPExceptions that were already caught and formatted
            print(f"ERROR: HTTPException re-raised from call_gemini_llm: {e.detail}")
            raise e
        except Exception as e:
            # Catch any other unexpected errors and provide more detail
            print(f"CRITICAL ERROR: An unexpected error occurred during LLM call in call_gemini_llm: {type(e).__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during LLM call: {type(e).__name__}: {e}"
            )

# --- API Endpoint for Natural Language Processing ---

@app.post(
    "/process_query",
    response_model=MCPResponse,
    summary="Process natural language inventory query",
    description="Accepts a natural language query, interprets it using GenAI, and interacts with the Inventory Service.",
    status_code=status.HTTP_200_OK
)
async def process_natural_language_query(nl_query: NaturalLanguageQuery):
    """
    Processes a natural language query related to inventory.

    The query is sent to a Generative AI model which determines the
    appropriate action (GET or POST) and parameters (item, change)
    for the Inventory Web Service.
    """
    user_query = nl_query.query
    print(f"\nDEBUG: Received user query: '{user_query}'")

    try:
        # 1. Call LLM to interpret the query
        # llm_prompt is now globally defined
        llm_parsed_data = await call_gemini_llm(llm_prompt.format(user_query=user_query))
        print(f"DEBUG: LLM Parsed Data received by process_natural_language_query: {json.dumps(llm_parsed_data, indent=2)}")

        # Ensure llm_parsed_data is a dictionary and has 'operation' key
        if not isinstance(llm_parsed_data, dict) or "operation" not in llm_parsed_data:
            raise ValueError(f"LLM response is not a valid dictionary or missing 'operation' key. Received: {llm_parsed_data}")

        operation = llm_parsed_data.get("operation")
        item = llm_parsed_data.get("item")
        change = llm_parsed_data.get("change")
        reasoning = llm_parsed_data.get("reasoning", "No specific reasoning provided by LLM.")

        async with httpx.AsyncClient() as client:
            if operation == "GET":
                response = await client.get(f"{INVENTORY_SERVICE_BASE_URL}/inventory")
                response.raise_for_status()
                inventory_state = response.json()
                message = f"Successfully retrieved inventory. Reasoning: {reasoning}"
                if item:
                    item_count = inventory_state.get(item, 0)
                    message = f"Successfully retrieved inventory for {item}: {item_count}. Reasoning: {reasoning}"
                return MCPResponse(message=message, inventory_state=inventory_state)

            elif operation == "POST":
                if item is None or change is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"LLM failed to extract required 'item' or 'change' for POST operation. LLM Reasoning: {reasoning}"
                    )
                post_data = {"item": item, "change": change}
                response = await client.post(f"{INVENTORY_SERVICE_BASE_URL}/inventory", json=post_data)
                response.raise_for_status()
                updated_inventory = response.json()
                message = f"Successfully updated inventory for {item} by {change}. Reasoning: {reasoning}"
                return MCPResponse(message=message, inventory_state=updated_inventory)

            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"LLM returned an unsupported operation: '{operation}'. LLM Reasoning: {reasoning}"
                )

    except httpx.RequestError as exc:
        print(f"ERROR: httpx.RequestError - Failed to connect to Inventory Service: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Inventory Service at {INVENTORY_SERVICE_BASE_URL}: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        print(f"ERROR: httpx.HTTPStatusError - Inventory Service returned an error: {exc.response.status_code} - {exc.response.text}")
        error_detail = exc.response.json().get("detail", "No specific error detail from Inventory Service.")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Inventory Service returned an error: {error_detail} (HTTP {exc.response.status_code})"
        )
    except HTTPException as e:
        # This block will now print the actual detail of the HTTPException
        print(f"CRITICAL ERROR: HTTPException caught in process_natural_language_query. Detail: {e.detail}")
        raise e # Re-raise the original HTTPException to be sent to the client
    except Exception as e:
        print(f"CRITICAL ERROR: An unexpected non-HTTPException error occurred in process_natural_language_query: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {type(e).__name__}: {e}"
        )