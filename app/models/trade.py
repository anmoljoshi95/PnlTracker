from app.models.enums import Side
from pydantic import BaseModel, Field, field_validator
import json 
from datetime import datetime
from decimal import Decimal

class Trade(BaseModel):
    id:int 
    symbol:str 
    side:Side  
    price:Decimal 
    quantity:Decimal   #keeping it flexible for fractional quantities
    timestamp:int 

    @field_validator("price", "quantity")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Must be greater than 0")
        return v

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        return v.upper()

    def to_json(self) -> dict:
        return self.model_dump(mode="json")
    

    def timestamp_to_human_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

   
    
