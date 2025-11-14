# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionLocal
from app.models import Base, CustomerDB, OrderDB
from app.schemas import CustomerCreate, CustomerRead, CustomerPatch, OrderCreate, OrderRead, OrderReadWithOwner

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)

# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def add_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = CustomerDB(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
        db.refresh(customer)
    except:
        db.rollback()
        raise HTTPException(status_code=409, detail="Customer already exists")
    return customer

@app.get("/api/customers", response_model=list[CustomerRead], status_code=status.HTTP_200_OK)
def list_customers(db: Session = Depends(get_db)):
    stmt = select(CustomerDB).order_by(CustomerDB.id)
    return db.execute(stmt),scalars().all()

@app.get("/api/customers/{customer_id}", response_model=CustomerRead, status_code=status.HTTP_200_OK)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/api/customer/{customer_id}", response_model=CustomerRead, status_code=status.HTTP_202_ACCEPTED)
def update_customer(customer_id: int, payload=CustomerCreate, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in payload.model_dump().items():
        setattr(customer, key, value)

    commit_or_rollback(db, "Failed to update user")
    db.refresh(customer)
    return customer

@app.patch("/api/customer/{customer_id}", response_model=CustomerRead, status_code=status.HTTP_202_ACCEPTED)
def update_customer(customer_id: int, payload=CustomerPatch, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)

    commit_or_rollback(db, "Failed to update user")
    db.refresh(customer)
    return customer

@app.delete("/api/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> Response:
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/api/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    order = OrderDB(
        order_number=order.order_number,
        total_cents = order.total_cents,
        owner_id = order.owner_id
    )

    db.add(order)
    commit_or_rollback(db, "Order create failed")
    db.refresh(order)
    return order

@app.get("/api/orders", response_model=list[OrderRead], status_code=status.HTTP_200_OK)
def list_orders(db: Session = Depends(get_db)):
    stmt = select(OrderDB).order_by(OrderDB.id)
    return db.execute(stmt).scalars().all()

@app.get("/api/orders/{order_id}", response_model=OrderReadWithOwner)
def get_order_with_customer(order_id: int, db: Session = Depends(get_db)):
    stmt = select(OrderDB).where(OrderDB.id == order_id).options(selectinload(OrderDB.owner))
    order = db.execute(stmt).scalars().all()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
