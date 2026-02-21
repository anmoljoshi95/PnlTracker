# from fastapi import FastAPI
# import uvicorn
# from typing import List
# from app.models.trade import Trade
# from collections import defaultdict
# from app.Services.services import PortFolioManager

# app = FastAPI()


# ALLTRADES = []

# #To Save Trades incomming
# @app.post("/trades", status_code=201)
# async def add_trade(trade: Trade):
#     ALLTRADES.append(trade)
#     return {
#         "message": "Trade recorded successfully",
#     }


# #to get the portfolio details
# @app.get("/portfolio")
# async def get_portfolio():
#     if not ALLTRADES:
#         raise HTTPException(
#             status_code=404,
#             detail="No trades found. Portfolio is empty."
#         )
#     try:
#         return PortFolioManager.calculate_portfolio(trades)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception:
#         raise HTTPException(status_code=500, detail="Internal server error")



from fastapi import FastAPI, HTTPException
from app.models.trade import Trade
from app.services.portfolio_manager import PortfolioManager

app = FastAPI()

portfolio_manager = PortfolioManager()


@app.post("/trades", status_code=201)
async def add_trade(trade: Trade):
    try:
        portfolio_manager.add_trade(trade)
        return {
            "message": "Trade recorded successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/portfolio")
async def get_portfolio():
    portfolio = portfolio_manager.get_portfolio()

    if not portfolio:
        raise HTTPException(status_code=404, detail="No open positions.")

    return portfolio


@app.get("/pnl")
async def get_pnl():
    try:
        return portfolio_manager.get_pnl()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




if __name__ == "__main__":
    uvicorn.run(
        "main:app",    
        host="0.0.0.0",
        port=8000,
        reload=True
    )