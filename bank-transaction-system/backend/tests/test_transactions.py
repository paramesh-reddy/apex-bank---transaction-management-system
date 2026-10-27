import uuid
from decimal import Decimal
from starlette.testclient import TestClient


def create_test_account(client: TestClient, name_prefix: str = "TxTest") -> str:
    res = client.post("/api/v1/accounts", json={"name": f"{name_prefix} {uuid.uuid4().hex[:6]}"})
    assert res.status_code == 201
    return res.json()["id"]


def test_credit_increases_balance(client: TestClient):
    account_id = create_test_account(client)
    ref = f"REF-CREDIT-{uuid.uuid4().hex[:8]}"
    res = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "150.50", "description": "Deposit salary", "reference_id": ref},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["transaction"]["type"] == "credit"
    assert data["transaction"]["amount"] == "150.50"
    assert data["account_balance"] == "150.50"


def test_debit_decreases_balance(client: TestClient):
    account_id = create_test_account(client)
    # Credit 200.00
    client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "200.00", "reference_id": f"INIT-{uuid.uuid4().hex[:8]}"},
    )
    # Debit 75.25
    ref = f"REF-DEBIT-{uuid.uuid4().hex[:8]}"
    res = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "debit", "amount": "75.25", "reference_id": ref},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["account_balance"] == "124.75"


def test_multiple_credits_and_debits_balance_accuracy(client: TestClient):
    account_id = create_test_account(client)
    amounts = [
        ("credit", "100.00"),
        ("credit", "50.25"),
        ("debit", "30.10"),
        ("credit", "20.00"),
        ("debit", "40.15"),
    ]
    expected_balance = Decimal("100.00") + Decimal("50.25") - Decimal("30.10") + Decimal("20.00") - Decimal("40.15")

    for t_type, amt in amounts:
        res = client.post(
            f"/api/v1/accounts/{account_id}/transactions",
            json={"type": t_type, "amount": amt, "reference_id": f"SEQ-{uuid.uuid4().hex[:8]}"},
        )
        assert res.status_code == 201

    res_account = client.get(f"/api/v1/accounts/{account_id}")
    assert Decimal(res_account.json()["balance"]) == expected_balance


def test_reject_zero_and_negative_amounts(client: TestClient):
    account_id = create_test_account(client)
    res_zero = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "0.00", "reference_id": f"ZERO-{uuid.uuid4().hex[:6]}"},
    )
    assert res_zero.status_code == 422

    res_neg = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "-50.00", "reference_id": f"NEG-{uuid.uuid4().hex[:6]}"},
    )
    assert res_neg.status_code == 422


def test_reject_invalid_transaction_types(client: TestClient):
    account_id = create_test_account(client)
    res = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "invest", "amount": "100.00", "reference_id": f"TYPE-{uuid.uuid4().hex[:6]}"},
    )
    assert res.status_code == 422


def test_reject_missing_or_blank_reference_id(client: TestClient):
    account_id = create_test_account(client)
    res_blank = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "50.00", "reference_id": "   "},
    )
    assert res_blank.status_code == 422


def test_reject_duplicate_reference_id_same_account(client: TestClient):
    account_id = create_test_account(client)
    ref = f"DUP-{uuid.uuid4().hex[:8]}"
    res1 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "50.00", "reference_id": ref},
    )
    assert res1.status_code == 201

    res2 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "25.00", "reference_id": ref},
    )
    assert res2.status_code == 409
    assert res2.json()["error"]["code"] == "DUPLICATE_TRANSACTION_REFERENCE"


def test_allow_same_reference_id_different_accounts(client: TestClient):
    acc1 = create_test_account(client)
    acc2 = create_test_account(client)
    shared_ref = f"SHARED-{uuid.uuid4().hex[:8]}"

    res1 = client.post(
        f"/api/v1/accounts/{acc1}/transactions",
        json={"type": "credit", "amount": "50.00", "reference_id": shared_ref},
    )
    assert res1.status_code == 201

    res2 = client.post(
        f"/api/v1/accounts/{acc2}/transactions",
        json={"type": "credit", "amount": "50.00", "reference_id": shared_ref},
    )
    assert res2.status_code == 201


def test_reject_insufficient_balance_without_modifying_balance(client: TestClient):
    account_id = create_test_account(client)
    # Deposit 50.00
    client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "50.00", "reference_id": f"INIT-{uuid.uuid4().hex[:6]}"},
    )
    # Attempt debit of 100.00
    res_debit = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "debit", "amount": "100.00", "reference_id": f"OVER-{uuid.uuid4().hex[:6]}"},
    )
    assert res_debit.status_code == 400
    assert res_debit.json()["error"]["code"] == "INSUFFICIENT_BALANCE"

    # Verify balance is still strictly 50.00
    res_acc = client.get(f"/api/v1/accounts/{account_id}")
    assert Decimal(res_acc.json()["balance"]) == Decimal("50.00")


def test_transaction_pagination_and_descending_order(client: TestClient):
    account_id = create_test_account(client)
    for i in range(15):
        client.post(
            f"/api/v1/accounts/{account_id}/transactions",
            json={"type": "credit", "amount": f"{i+1}.00", "reference_id": f"PAG-{i}-{uuid.uuid4().hex[:6]}"},
        )

    res_p1 = client.get(f"/api/v1/accounts/{account_id}/transactions?page=1&limit=10")
    assert res_p1.status_code == 200
    d1 = res_p1.json()
    assert len(d1["items"]) == 10
    assert d1["current_page"] == 1
    assert d1["page_size"] == 10
    assert d1["total_records"] == 15
    assert d1["total_pages"] == 2

    # Latest record should have amount 15.00
    assert d1["items"][0]["amount"] == "15.00"

    res_p2 = client.get(f"/api/v1/accounts/{account_id}/transactions?page=2&limit=10")
    assert res_p2.status_code == 200
    d2 = res_p2.json()
    assert len(d2["items"]) == 5


def test_confirm_transactions_cannot_be_modified_or_deleted_via_api(client: TestClient):
    account_id = create_test_account(client)
    res_tx = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={"type": "credit", "amount": "100.00", "reference_id": f"IMMUTABLE-{uuid.uuid4().hex[:6]}"},
    )
    tx_id = res_tx.json()["transaction"]["id"]

    # Verify PUT/PATCH/DELETE endpoints do not exist
    put_res = client.put(f"/api/v1/accounts/{account_id}/transactions/{tx_id}", json={"amount": "200.00"})
    assert put_res.status_code in (404, 405)

    patch_res = client.patch(f"/api/v1/accounts/{account_id}/transactions/{tx_id}", json={"amount": "200.00"})
    assert patch_res.status_code in (404, 405)

    delete_res = client.delete(f"/api/v1/accounts/{account_id}/transactions/{tx_id}")
    assert delete_res.status_code in (404, 405)
