from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict

# Initialize the FastAPI application
app = FastAPI(
    title="Inventory Web Service",
    description="A simple web service to manage inventory for tshirts and pants.",
    version="1.0.0",
)

# In-memory data store for inventory
# Using a dictionary to store item counts.
# Initial inventory values are set as per the example.
inventory: Dict[str, int] = {
    "tshirts": 20,
    "pants": 15,
}

# --- Pydantic Models for Request and Response Bodies ---

class InventoryResponse(BaseModel):
    """
    Pydantic model for the GET /inventory response.
    Describes the structure of the inventory data returned.
    """
    tshirts: int = Field(..., description="Current count of tshirts in inventory.")
    pants: int = Field(..., description="Current count of pants in inventory.")

class InventoryUpdateRequest(BaseModel):
    """
    Pydantic model for the POST /inventory request.
    Describes the required fields for modifying an item's count.
    """
    item: str = Field(..., description="The name of the item to modify ('tshirts' or 'pants').")
    change: int = Field(..., description="The amount to change the item's count by. Can be positive (add) or negative (subtract).")

class InventoryUpdateResponse(BaseModel):
    """
    Pydantic model for the POST /inventory response.
    Returns the updated inventory counts after a modification.
    """
    tshirts: int = Field(..., description="Updated count of tshirts in inventory.")
    pants: int = Field(..., description="Updated count of pants in inventory.")

# --- API Endpoints ---

@app.get(
    "/inventory",
    response_model=InventoryResponse,
    summary="Get current inventory count",
    description="Retrieves the current stock levels for tshirts and pants.",
    status_code=status.HTTP_200_OK
)
async def get_inventory():
    """
    Returns the current inventory count for tshirts and pants.
    """
    return inventory

@app.post(
    "/inventory",
    response_model=InventoryUpdateResponse,
    summary="Modify item inventory count",
    description="Modifies the count of a specific item (tshirts or pants) in the inventory.",
    status_code=status.HTTP_200_OK
)
async def update_inventory(request: InventoryUpdateRequest):
    """
    Modifies the count of an item in the inventory.

    - **item**: The name of the item ('tshirts' or 'pants').
    - **change**: The amount to change the count by (positive to add, negative to subtract).

    Raises:
        HTTPException: If the item is invalid or if the change results in a negative stock.
    """
    item_name = request.item.lower() # Convert to lowercase for case-insensitivity
    change_amount = request.change

    # Validate the item name
    if item_name not in inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid item: '{request.item}'. Only 'tshirts' and 'pants' are supported."
        )

    # Calculate new stock and ensure it's not negative
    new_stock = inventory[item_name] + change_amount
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reduce '{item_name}' stock below zero. Current: {inventory[item_name]}, Attempted change: {change_amount}"
        )

    # Update the inventory
    inventory[item_name] = new_stock

    # Return the updated inventory
    return inventory

# To run this service:
# 1. Save the code as `main.py` inside an `inventory-service` directory.
# 2. Make sure you have FastAPI and Uvicorn installed:
#    `pip install fastapi uvicorn pydantic`
# 3. Run the service from the `inventory-service` directory using:
#    `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
# 4. Access the API documentation (OpenAPI UI) at `http://localhost:8000/docs`
#    or the raw OpenAPI JSON at `http://localhost:8000/openapi.json`
