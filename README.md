# Portfolio & PnL Tracker – FastAPI

A simple backend service to track trades, portfolio positions, and Profit & Loss (PnL).

Built using FastAPI and Python.

---

## 🚀 Overview

This service allows:

* Recording trades (Buy/Sell)
* Viewing current portfolio holdings
* Viewing Realized and Unrealized PnL
* Viewing symbol-wise PnL breakdown

The system maintains portfolio state incrementally (O(1) reads), similar to real trading systems.

---

## 🧠 Approach

Instead of recalculating portfolio and PnL from trade history on every request, this implementation uses an incremental state update model:

* Trades are stored for audit purposes.
* A `PortfolioManager` maintains positions in memory.
* On every trade:

  * Position quantity and average cost are updated.
  * Realized PnL is updated immediately.
* Portfolio and PnL reads are O(1).

This design mirrors how real trading systems maintain live portfolio state.

---

## 📐 Accounting Method

This implementation uses the Average Cost Method:

* Average entry price updates only on BUY.
* SELL does not change average entry price.
* Realized PnL = (Sell Price − Avg Entry Price) × Quantity Sold.
* Unrealized PnL = (Market Price − Avg Entry Price) × Current Quantity.

---

## 📌 Assumptions

* Single user system.
* In-memory storage (no database).
* Hardcoded market prices:

  * BTC → 44,000
  * ETH → 2,000
* No authentication.
* No concurrency handling (single-process design).

---

## 🏗 Project Structure

```
app/
│
├── main.py                  # FastAPI routes
├── models/
│   ├── trade.py
│   └── enums.py
├── serices/
│   └── portfolio_manager.py # Business logic
│
tests/
└── test_api.py              # API test cases
```

---

## ⚙️ Installation & Running

### 1️⃣ Clone the repository

```
git clone <your-repo-url>
cd <repo-folder>
```

### 2️⃣ Create virtual environment

```
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows
```

### 3️⃣ Install dependencies

If requirements.txt is provided:

```
pip install -r requirements.txt
```

Otherwise:

```
pip install fastapi uvicorn pytest
```

### 4️⃣ Run the server

```
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

Interactive docs available at:

```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

### ➕ Add Trade

`POST /trades`

Example:

```json
{
  "id": 1,
  "symbol": "BTC",
  "side": "buy",
  "price": "40000",
  "quantity": "1",
  "timestamp": 1234567890
}
```

---

### 📊 Get Portfolio

`GET /portfolio`

Returns current open positions:

```json
{
  "BTC": {
    "quantity": "1",
    "average_entry_price": "41000",
    "realized_pnl": "2000"
  }
}
```

Returns `404` if no open positions.

---

### 💰 Get PnL

`GET /pnl`

Returns:

```json
{
  "realized_pnl": "2000",
  "unrealized_pnl": "3000",
  "by_symbol": {
    "BTC": {
      "realized_pnl": "2000",
      "unrealized_pnl": "3000",
      "quantity": "1",
      "average_entry_price": "41000"
    }
  }
}
```

---

## 🧪 Running Tests

```
pytest -v
```

Tests cover:

* Trade validation
* Oversell protection
* Portfolio correctness
* Realized PnL
* Unrealized PnL
* Multi-symbol handling
* Empty portfolio behavior

---

## 💡 Design Highlights

* Uses `Decimal` for financial precision (no floating-point errors).
* Clean separation of:

  * API layer
  * Domain logic
  * Data models
* Incremental portfolio state updates (efficient & scalable).
* Test coverage for critical flows.

---

## 🔚 Future Improvements (Optional)

* FIFO lot accounting
* Persistent database storage
* Concurrency-safe updates
* Market price API integration
* Authentication layer
