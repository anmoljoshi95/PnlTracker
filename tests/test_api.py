import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.main import app, portfolio_manager

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_portfolio():
    portfolio_manager.positions.clear()
    portfolio_manager.trades.clear()
    yield


def test_portfolio_empty():
    response = client.get("/portfolio")
    assert response.status_code == 404


def test_add_buy_trade():
    response = client.post("/trades", json={
        "id": 1,
        "symbol": "BTC",
        "side": "buy",
        "price": "40000",
        "quantity": "1",
        "timestamp": 123456
    })
    assert response.status_code == 201


def test_add_sell_without_position():
    response = client.post("/trades", json={
        "id": 1,
        "symbol": "BTC",
        "side": "sell",
        "price": "40000",
        "quantity": "1",
        "timestamp": 123456
    })
    assert response.status_code == 400


def test_portfolio_after_buys():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "40000", "quantity": "1", "timestamp": 1
    })
    client.post("/trades", json={
        "id": 2, "symbol": "BTC", "side": "buy",
        "price": "42000", "quantity": "1", "timestamp": 2
    })

    response = client.get("/portfolio")
    data = response.json()

    assert response.status_code == 200
    assert Decimal(data["BTC"]["quantity"]) == Decimal("2")
    assert Decimal(data["BTC"]["average_entry_price"]) == Decimal("41000")


def test_realized_pnl_after_sell():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "40000", "quantity": "1", "timestamp": 1
    })
    client.post("/trades", json={
        "id": 2, "symbol": "BTC", "side": "buy",
        "price": "42000", "quantity": "1", "timestamp": 2
    })
    client.post("/trades", json={
        "id": 3, "symbol": "BTC", "side": "sell",
        "price": "43000", "quantity": "1", "timestamp": 3
    })

    response = client.get("/pnl")
    data = response.json()

    assert Decimal(data["realized_pnl"]) == Decimal("2000")


def test_unrealized_pnl():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "41000", "quantity": "1", "timestamp": 1
    })

    response = client.get("/pnl")
    data = response.json()

    assert Decimal(data["unrealized_pnl"]) == Decimal("3000")


def test_oversell_error():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "40000", "quantity": "1", "timestamp": 1
    })

    response = client.post("/trades", json={
        "id": 2, "symbol": "BTC", "side": "sell",
        "price": "42000", "quantity": "2", "timestamp": 2
    })

    assert response.status_code == 400


def test_multi_symbol():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "40000", "quantity": "1", "timestamp": 1
    })
    client.post("/trades", json={
        "id": 2, "symbol": "ETH", "side": "buy",
        "price": "1500", "quantity": "2", "timestamp": 2
    })

    response = client.get("/portfolio")
    data = response.json()

    assert "BTC" in data
    assert "ETH" in data


def test_position_closed():
    client.post("/trades", json={
        "id": 1, "symbol": "BTC", "side": "buy",
        "price": "40000", "quantity": "1", "timestamp": 1
    })
    client.post("/trades", json={
        "id": 2, "symbol": "BTC", "side": "sell",
        "price": "41000", "quantity": "1", "timestamp": 2
    })

    response = client.get("/portfolio")
    assert response.status_code == 404  