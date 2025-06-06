from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class StockTransactionBase(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    quantity: int = Field(..., description="Number of shares")
    price: float = Field(..., description="Price per share")
    transaction_type: str = Field(..., description="Type of transaction (BUY/SELL)")
    transaction_date: datetime = Field(..., description="Date of the transaction")
    portfolio_id: int = Field(..., description="ID of the portfolio")

class StockTransactionCreate(StockTransactionBase):
    pass

class StockTransaction(StockTransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 