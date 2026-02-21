from decimal import Decimal
from typing import Dict, List
from app.models.trade import Trade
from app.models.enums import Side


class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.total_quantity: Decimal = Decimal("0")
        self.avg_entry_price: Decimal = Decimal("0")
        self.realized_pnl: Decimal = Decimal("0")


class PortfolioManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.market_prices: Dict[str, Decimal] = {
            "BTC": Decimal("44000"),
            "ETH": Decimal("2000")
        }

    def add_trade(self, trade: Trade): #function to add and update the portfolio then and there
        pos = self.positions.setdefault(trade.symbol, Position(trade.symbol))

        if trade.side == Side.BUY:
            new_total_qty = pos.total_quantity + trade.quantity
            new_total_cost = (
                pos.total_quantity * pos.avg_entry_price
                + trade.quantity * trade.price
            )

            pos.total_quantity = new_total_qty
            pos.avg_entry_price = new_total_cost / new_total_qty

        else:  
            if trade.quantity > pos.total_quantity:
                raise ValueError(f"Insufficient quantity to sell {trade.symbol}")

            realized = (trade.price - pos.avg_entry_price) * trade.quantity
            pos.realized_pnl += realized
            pos.total_quantity -= trade.quantity

            if pos.total_quantity == 0:
                pos.avg_entry_price = Decimal("0")

        self.trades.append(trade)

    def get_portfolio(self): #get current state of the portfolio
        result = {}

        for symbol, pos in self.positions.items():
            if pos.total_quantity > 0:
                result[symbol] = {
                    "quantity": pos.total_quantity,
                    "average_entry_price": pos.avg_entry_price,
                    "realized_pnl": pos.realized_pnl
                }

        return result

    def get_pnl(self): #get current pnl details
        total_realized = Decimal("0")
        total_unrealized = Decimal("0")

        by_symbol = {}

        for symbol, pos in self.positions.items():
            realized = pos.realized_pnl
            unrealized = Decimal("0")

            if pos.total_quantity > 0:
                if symbol not in self.market_prices:
                    raise ValueError(f"Missing market price for {symbol}")

                market_price = self.market_prices[symbol]
                unrealized = (
                    (market_price - pos.avg_entry_price)
                    * pos.total_quantity
                )

            total_realized += realized
            total_unrealized += unrealized

            by_symbol[symbol] = {
                "realized_pnl": realized,
                "unrealized_pnl": unrealized,
                "quantity": pos.total_quantity,
                "average_entry_price": pos.avg_entry_price
            }

        return {
            "realized_pnl": total_realized,
            "unrealized_pnl": total_unrealized,
            "pnl_split": by_symbol
        }