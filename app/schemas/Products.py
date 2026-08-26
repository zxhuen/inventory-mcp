from unicodedata import numeric

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: numeric
    stock: int
