import unittest
from fastapi import HTTPException
from app.kc.auth import verify_role, verify_path, verify_parameters
import asyncio
from app.kc.auth import get_user_info


class TestVerifyRole(unittest.TestCase):
    def test_role_present_returns_true(self):
        self.assertTrue(verify_role(["ADMIN", "USER"], "ADMIN"))

    def test_role_missing_raises_401(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_role(["USER"], "ADMIN")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_empty_roles_raises_401(self):
        with self.assertRaises(HTTPException):
            verify_role([], "ADMIN")


class TestVerifyPath(unittest.TestCase):
    def test_path_allowed(self):
        verify_path(["/api/v1/bergen"], "/api/v1/bergen")

    def test_path_not_allowed_raises_401(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_path(["/api/v1/oslo"], "/api/v1/bergen")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_empty_paths_raises_401(self):
        with self.assertRaises(HTTPException):
            verify_path([], "/api/v1/bergen")


class TestVerifyParameters(unittest.TestCase):
    def test_all_params_allowed(self):
        verify_parameters(["bergen", "oslo"], ["bergen"])

    def test_multiple_params_all_allowed(self):
        verify_parameters(["bergen", "oslo"], ["bergen", "oslo"])

    def test_unauthorized_param_raises_401(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_parameters(["bergen"], ["stavanger"])
        self.assertEqual(ctx.exception.status_code, 401)

    def test_mixed_params_raises_401(self):
        with self.assertRaises(HTTPException):
            verify_parameters(["bergen"], ["bergen", "stavanger"])


class TestGetUserInfo(unittest.TestCase):
    def _make_payload(self, realm_roles=None, client_roles=None, locations=None):
        return {
            "sub": "abc-123",
            "preferred_username": "fireadmin",
            "given_name": "Fire",
            "family_name": "Admin",
            "azp": "firebuster-api",
            "realm_access": {"roles": realm_roles or []},
            "resource_access": {"firebuster-api": {"roles": client_roles or []}},
            "location": locations or [],
        }

    def test_user_fields_mapped_correctly(self):
        payload = self._make_payload(realm_roles=["ADMIN"], client_roles=["APP_ADMIN"])
        user = asyncio.run(get_user_info(payload))
        self.assertEqual(user.username, "fireadmin")
        self.assertEqual(user.id, "abc-123")
        self.assertIn("ADMIN", user.realm_roles)
        self.assertIn("APP_ADMIN", user.client_roles)

    def test_locations_extracted(self):
        payload = self._make_payload(locations=["/api/v1/bergen"])
        user = asyncio.run(get_user_info(payload))
        self.assertEqual(user.locations, ["/api/v1/bergen"])

    def test_missing_resource_access_gives_empty_client_roles(self):
        payload = self._make_payload()
        payload["resource_access"] = {}
        user = asyncio.run(get_user_info(payload))
        self.assertEqual(user.client_roles, [])
