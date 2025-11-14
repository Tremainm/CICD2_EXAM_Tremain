import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.models import Base

TEST_DB_URL = "sqlite+pysqlite:///:memory"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread":False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

Base.metadata.create_all(bind=engine)

@pytes.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_create_customer(client):
    r = client.post("/api/customers", json={"name":"John", "email":"john@mail.com", "customer_since": 2025})
    assert r.status_code == 201

def test_update_customer(client):
    r = client.post("/api/customers", json={"name":"Jane", "email":"jane@mail.com", "customer_since": 2015})
    assert r.status_code == 201
    customer_id = r.json()["id"]

    payload = {"name":"Mary", "email":"mary@mail.com", "customer_since": 2035}
    r2 = client.put(f"/api/customer/{customer_id}", json=payload)

    assert r2.status_code == 202
    data = r2.json()
    
    assert data["name"] == "Mary"
    assert data["email"] == "mary@mail.com"
    assert data["customer_since"] == 2035

def test_patch_customer(client):
    r = client.post("/api/customers", json={"name":"Jim", "email":"jim@mail.com", "customer_since": 2010})
    assert r.status_code == 201
    customer_id = r.json()["id"]

    r2 = client.put(f"/api/customer/{customer_id}", json={"email":"jimNew@mail.com"})

    assert r2.status_code == 202
    data = r2.json()
    
    assert data["email"] == "jimNew@mail.com"

def test_delete_customer(client):
    r = client.post("/api/customers", json={"name":"Jimmy", "email":"jimmy@mail.com", "customer_since": 2011})
    assert r.status_code == 201
    customer_id = r.json()["id"]

    r2 = client.delete(f"/api/customers/{customer_id}")
    assert = r2.status_code == 204

    r3 = client.get(f"/api/customers/{customer_id}")
    assert r3.status_code == 404

def test_get_customer(client):
    r = client.post("/api/customers", json={"name":"Tremain", "email":"tremain@mail.com", "customer_since": 2021})
    assert r.status_code == 201
    customer_id = r.json()["id"]

    r2 = client.get(f"/api/customers/{customer_id}")
    assert r2.status_code == 200
    data = r2.json()
    
    assert data["name"] == "Tremain"

def test_get_customer_not_found(client):
    r = client.get("/api/customers/999")
    assert r.status_code == 404