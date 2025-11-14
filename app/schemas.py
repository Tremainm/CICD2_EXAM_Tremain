from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict
from annotated_types import Ge, Le

NameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
CustomerSinceInt = Annotated[int, Ge(2000), Le(2100)]

OrderNumStr = Annotated[str, StringConstraints(min_length=3, max_length=20)]
TotalCentsInt = Annotated[int, Ge(1), Le(1000000)]

class CustomerCreate(BaseModel):
    name: NameStr
    email: EmailStr
    customer_since: CustomerSinceInt

class CustomerPatch(BaseModel):
    name: Optional[NameStr] = None
    email: Optional[EmailStr] = None
    customer_since: Optional[CustomerSinceInt] = None

class CustomerRead(BaseModel):
    id: int
    name: NameStr
    email: EmailStr
    customer_since: CustomerSinceInt

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    order_number: OrderNumStr
    total_cents: TotalCentsInt
    owner_id: int

class OrderRead(BaseModel):
    id: int 
    order_number: OrderNumStr
    total_cents: TotalCentsInt
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class OrderReadWithOwner(OrderRead):
    owner: Optional["CustomerRead"] = None