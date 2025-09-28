from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_crud_operations():
    # Create
    response = client.post("/items/", json={"name":"Item1","description":"First item","price":10})
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Read by ID
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Item1"

    # Update
    response = client.put(f"/items/{item_id}", json={"name":"Updated","description":"Updated item","price":20})
    assert response.status_code == 200
    assert response.json()["price"] == 20

    # Read all
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Delete
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
