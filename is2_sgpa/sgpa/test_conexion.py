import pytest
from django.test import Client


@pytest.mark.django_db
def test_example():
    client = Client()
    response = client.get("http://127.0.0.1:8000/login")
    assert response.status_code == 200

