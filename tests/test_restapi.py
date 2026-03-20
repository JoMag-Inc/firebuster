import os
import unittest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from app.restapi import app

client = TestClient(app)


class TestRestapi(unittest.TestCase):
    def test_public_api(self):
        response = client.get('/api/v1/public')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "This is a public resource for everyone."})


    def test_protected_admin_endpoint(self):
        load_dotenv()
        acc_token = os.environ.get('token_user1')
        _headers = {"Authorization": f"Bearer {acc_token}"}
        response = client.get('api/v1/admin', headers=_headers)
        print(response.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{"message": "This is a protected resource for ADMIN role."})

    def test_protected_resource_path(self):
        load_dotenv()
        acc_token = os.environ.get('token_user1')
        location: str = "bergen"
        headers = {"Authorization": f'Bearer {acc_token}'}
        response = client.get(f'/api/v1/{location}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": f'This is a protected resource for any user that is registered on a location = {location}.'})



