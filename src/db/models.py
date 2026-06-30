from datetime import datetime, timezone

from sqlalchemy import DateTime, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class BulletinModel(Base):
    __tablename__ = 'bulletins'

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_basis_name: Mapped[str]
    delivery_type_id: Mapped[str]
    volume: Mapped[int]
    total: Mapped[int]
    count: Mapped[int]
    date: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


Index("ix_bulletin_id", BulletinModel.id)
Index("ix_bulletins_exchange_product_name", BulletinModel.exchange_product_name)
Index("ix_bulletins_delivery_basis_name", BulletinModel.delivery_basis_name)
