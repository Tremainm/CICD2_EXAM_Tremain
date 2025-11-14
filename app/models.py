from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    pass

class CustomerDB(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    customer_since: Mapped[int] = mapped_column(Integer, nullable=False)
    orders: Mapped[list["OrderDB"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[int] = mapped_column(unique=True, nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_id", ondelete="CASCADE"), nullable=False)
    owner: Mapped["CustomerDB"] = relationship(back_populates="orders")


