import uuid
from decimal import Decimal
from starlette.testclient import TestClient

def create_account_with_funds(client: TestClient, initial_balance: str) -> str:
    res = client.post('/api/v1/accounts', json={'name': f'TransferAcct {uuid.uuid4().hex[:6]}'})
    assert res.status_code == 201
    acc_id = res.json()['id']
    if Decimal(initial_balance) > 0:
        res_credit = client.post(
            f'/api/v1/accounts/{acc_id}/transactions',
            json={
                'type': 'credit',
                'amount': initial_balance,
                'description': 'Funding account',
                'reference_id': f'FUND-{uuid.uuid4().hex[:8]}',
            },
        )
        assert res_credit.status_code == 201
    return acc_id

def test_transfer_between_two_accounts_successfully(client: TestClient):
    acc_a = create_account_with_funds(client, '100.00')
    acc_b = create_account_with_funds(client, '50.00')
    ref = f'TRF-{uuid.uuid4().hex[:8]}'

    res = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc_a,
            'destination_account_id': acc_b,
            'amount': '30.00',
            'reference_id': ref,
            'description': 'Payment for services',
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert Decimal(data['source_balance']) == Decimal('70.00')
    assert Decimal(data['destination_balance']) == Decimal('80.00')
    assert data['transfer']['reference_id'] == ref

    tx_a = client.get(f'/api/v1/accounts/{acc_a}/transactions')
    assert tx_a.status_code == 200
    debit_tx = tx_a.json()['items'][0]
    assert debit_tx['type'] == 'debit'
    assert debit_tx['amount'] == '30.00'

    tx_b = client.get(f'/api/v1/accounts/{acc_b}/transactions')
    assert tx_b.status_code == 200
    credit_tx = tx_b.json()['items'][0]
    assert credit_tx['type'] == 'credit'
    assert credit_tx['amount'] == '30.00'

def test_transfer_reject_same_account(client: TestClient):
    acc = create_account_with_funds(client, '100.00')
    res = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc,
            'destination_account_id': acc,
            'amount': '20.00',
            'reference_id': f'SAME-{uuid.uuid4().hex[:6]}',
        },
    )
    assert res.status_code == 400
    assert res.json()['error']['code'] == 'SAME_ACCOUNT_TRANSFER'

def test_transfer_reject_nonexistent_account(client: TestClient):
    acc_a = create_account_with_funds(client, '100.00')
    fake_id = str(uuid.uuid4())
    res = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc_a,
            'destination_account_id': fake_id,
            'amount': '20.00',
            'reference_id': f'NOACC-{uuid.uuid4().hex[:6]}',
        },
    )
    assert res.status_code == 404
    assert res.json()['error']['code'] == 'ACCOUNT_NOT_FOUND'

def test_transfer_reject_insufficient_funds(client: TestClient):
    acc_a = create_account_with_funds(client, '25.00')
    acc_b = create_account_with_funds(client, '50.00')
    res = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc_a,
            'destination_account_id': acc_b,
            'amount': '100.00',
            'reference_id': f'LOW-{uuid.uuid4().hex[:6]}',
        },
    )
    assert res.status_code == 400
    assert res.json()['error']['code'] == 'INSUFFICIENT_BALANCE'

    res_a = client.get(f'/api/v1/accounts/{acc_a}')
    res_b = client.get(f'/api/v1/accounts/{acc_b}')
    assert Decimal(res_a.json()['balance']) == Decimal('25.00')
    assert Decimal(res_b.json()['balance']) == Decimal('50.00')

def test_transfer_reject_duplicate_reference(client: TestClient):
    acc_a = create_account_with_funds(client, '100.00')
    acc_b = create_account_with_funds(client, '50.00')
    ref = f'DUP-TRF-{uuid.uuid4().hex[:8]}'
    res1 = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc_a,
            'destination_account_id': acc_b,
            'amount': '10.00',
            'reference_id': ref,
        },
    )
    assert res1.status_code == 201

    res2 = client.post(
        '/api/v1/transfers',
        json={
            'source_account_id': acc_a,
            'destination_account_id': acc_b,
            'amount': '10.00',
            'reference_id': ref,
        },
    )
    assert res2.status_code == 409
    assert res2.json()['error']['code'] == 'DUPLICATE_TRANSFER_REFERENCE'
