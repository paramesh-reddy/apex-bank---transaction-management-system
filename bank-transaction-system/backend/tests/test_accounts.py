import uuid
from starlette.testclient import TestClient


def test_create_account_success(client: TestClient):
    unique_name = f"Test Account {uuid.uuid4().hex[:8]}"
    response = client.post("/api/v1/accounts", json={"name": unique_name})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == unique_name
    assert float(data["balance"]) == 0.00
    assert "id" in data
    assert "created_at" in data


def test_create_account_reject_blank_or_whitespace_name(client: TestClient):
    response = client.post("/api/v1/accounts", json={"name": ""})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

    response2 = client.post("/api/v1/accounts", json={"name": "   "})
    assert response2.status_code == 422
    assert response2.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_account_success(client: TestClient):
    name = f"Savings {uuid.uuid4().hex[:6]}"
    res_create = client.post("/api/v1/accounts", json={"name": name})
    account_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/accounts/{account_id}")
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["id"] == account_id
    assert data["name"] == name
    assert float(data["balance"]) == 0.00


def test_get_account_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/accounts/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "ACCOUNT_NOT_FOUND"


def test_list_accounts(client: TestClient):
    response = client.get("/api/v1/accounts?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
