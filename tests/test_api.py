from fastapi.testclient import TestClient
from order_api.main import app
from order_api.database import engine, Base

import pytest
import json


class TestAPI:
    client = TestClient(app)

    @pytest.fixture(autouse=True, scope='session')
    def _cleanup(self):
        Base.metadata.create_all(bind=engine)
        self.client.post("/orders", data=json.dumps({
        "address": "123 Example Street",
        "recipient_name": "John Doe",
        "active": True,
        "status": "ORDER_RECEIVED",
        "items": [
            {
            "item": "Computer",
            "quantity": 1
            }
        ]
        }))
        yield
        self.client.close()
        Base.metadata.drop_all(bind=engine)

    def test_create(self):
        response = self.client.post("/orders", data=json.dumps({
        "address": "124 Example Street",
        "recipient_name": "Jane Doe",
        "active": False,
        "status": "ORDER_SHIPPED",
        "items": [
            {
            "item": "Pillow",
            "quantity": 3
            }
        ]
        }))

        assert response.status_code == 201
    
    def test_get_orders(self):
        response = self.client.get("/orders")

        assert response.status_code == 200
        assert response.content != b"[]"
    
    def test_orders_active(self):

        response = self.client.get("/orders/active")

        assert response.status_code == 200
        assert response.json()[0]["active"] is True

    def test_orders_status(self):
        response = self.client.get("/orders/status/ORDER_SHIPPED")

        assert response.status_code == 200
        assert response.json()[0]["status"] == "ORDER_SHIPPED"
    
    def test_orders_id(self):
        response = self.client.get("/orders/1")

        assert response.status_code == 200
        assert response.json()["recipient_name"] == "John Doe"
        assert response.json()["address"] == "123 Example Street"
    
    def test_orders_deactiavte(self):
        response = self.client.delete("/orders/1")

        assert response.status_code == 200

        response = self.client.get("/orders/1")

        assert response.json()["active"] is False
    
    def test_orders_modify(self):
        response = self.client.patch("/orders/1", data=json.dumps({
        "address": "125 Example Street",
        "recipient_name": "Timmy Doe",
        "active": True,
        "status": "ORDER_RECEIVED",
        "items": [
            {
            "item": "Computer",
            "quantity": 1
            }
        ]
        }))

        assert response.status_code == 200
        
        response  = self.client.get("/orders/1")

        assert response.status_code == 200
        assert response.json()["address"] == "125 Example Street"
        assert response.json()["recipient_name"] == "Timmy Doe"