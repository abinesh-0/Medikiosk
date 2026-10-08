import os
os.environ['DATABASE_URL']='sqlite:///:memory:'
os.environ['ALLOW_DEV_OTP']='true'
os.environ['TESTING']='true'
import pytest
from app import create_app

@pytest.fixture()
def client():
    app=create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c
