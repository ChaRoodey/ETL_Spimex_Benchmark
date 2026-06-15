from datetime import datetime

from pydantic import BaseModel


class BulletinAddSchema(BaseModel):
    exchange_product_id: int
    exchange_product_name: int
    oil_id: int
    delivery_basis_id: int
    delivery_basis_name: str
    delivery_type_id: int
    volume: int
    total: int
    count: int
    date: datetime
