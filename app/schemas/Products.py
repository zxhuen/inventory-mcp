from decimal import Decimal
from unicodedata import numeric

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal
    stock: int
