from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_landing_page():
    response = client.get("/landing-page")
    assert response.status_code == 200

def test_post_contact_form():
    response = client.post("/contact-form", data={"name": "John Doe", "email": "john@example.com", "message": "Hello World"})
    assert response.status_code == 200
    assert response.json() == {"message": "Form submitted successfully"}

def test_post_contact_form_error():
    response = client.post("/contact-form", data={"name": "", "email": "", "message": ""})
    assert response.status_code == 200
    assert response.json() == {"error": "Form submission failed"}
