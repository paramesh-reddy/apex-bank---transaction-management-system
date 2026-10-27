import uuid
from decimal import Decimal
import threading
from starlette.testclient import TestClient
from main import app

def test_concurrent_debits_prevent_overdraft():
    client = TestClient(app)
    res_acc = client.post('/api/v1/accounts', json={'name': f'ConcurrentTest {uuid.uuid4().hex[:6]}'})
    acc_id = res_acc.json()['id']

    client.post(
        f'/api/v1/accounts/{acc_id}/transactions',
        json={'type': 'credit', 'amount': '100.00', 'reference_id': f'INIT-{uuid.uuid4().hex[:8]}'},
    )

    num_threads = 10
    success_count = 0
    fail_count = 0
    lock = threading.Lock()

    def do_debit(idx: int):
        nonlocal success_count, fail_count
        thread_client = TestClient(app)
        res = thread_client.post(
            f'/api/v1/accounts/{acc_id}/transactions',
            json={
                'type': 'debit',
                'amount': '20.00',
                'reference_id': f'CONC-DEBIT-{idx}-{uuid.uuid4().hex[:6]}',
            },
        )
        with lock:
            if res.status_code == 201:
                success_count += 1
            elif res.status_code == 400 and res.json()['error']['code'] == 'INSUFFICIENT_BALANCE':
                fail_count += 1

    threads = [threading.Thread(target=do_debit, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert success_count == 5, f'Expected 5 successful debits, got {success_count}'
    assert fail_count == 5, f'Expected 5 failed debits, got {fail_count}'

    final_res = client.get(f'/api/v1/accounts/{acc_id}')
    assert Decimal(final_res.json()['balance']) == Decimal('0.00')

def test_database_trigger_immutability(db):
    from sqlalchemy import text
    import pytest

    row = db.execute(text('SELECT id FROM transactions LIMIT 1;')).fetchone()
    if row:
        tx_id = row[0]
        with pytest.raises(Exception) as exc_info:
            db.execute(text('UPDATE transactions SET amount = 999.00 WHERE id = :id'), {'id': tx_id})
            db.commit()
        db.rollback()
        assert 'Transactions are strictly immutable' in str(exc_info.value)
