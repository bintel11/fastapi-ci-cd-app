from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import json
import os

app = FastAPI(title="CRUD App with Input/Output Files")

# Input file (simulates DB)
INPUT_FILE = "data.json"
# Output file (parsed data written here after each change)
OUTPUT_FILE = "parsed_output.json"

# Ensure files exist
for file in [INPUT_FILE, OUTPUT_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)

# Helpers
def read_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def write_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def sync_output():
    """Copy current input file to output file"""
    data = read_data(INPUT_FILE)
    write_data(OUTPUT_FILE, data)

# CRUD Operations

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    data = read_data(INPUT_FILE)
    item_dict = item.dict()
    item_dict["id"] = max([d.get("id",0) for d in data], default=0) + 1
    data.append(item_dict)
    write_data(INPUT_FILE, data)
    sync_output()  # write parsed output
    return item_dict

@app.get("/items/", response_model=List[Item])
def read_items():
    return read_data(INPUT_FILE)

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    data = read_data(INPUT_FILE)
    for item in data:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    data = read_data(INPUT_FILE)
    for idx, existing_item in enumerate(data):
        if existing_item["id"] == item_id:
            updated_item = item.dict()
            updated_item["id"] = item_id
            data[idx] = updated_item
            write_data(INPUT_FILE, data)
            sync_output()
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    data = read_data(INPUT_FILE)
    for idx, existing_item in enumerate(data):
        if existing_item["id"] == item_id:
            data.pop(idx)
            write_data(INPUT_FILE, data)
            sync_output()
            return {"message": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
