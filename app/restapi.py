from app.factory import get_ttf_service
from app.services.ttf.ttf_service import TTFService
from decouple import config
from fastapi import FastAPI, Depends, status, Query, HTTPException
from app.kc.auth import (
    verify_admin_role,
    verify_user_role,
    verify_sadmin_role,
    verify_suser_role,
    verify_user_path,
    verify_user_locquery,
)

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight": False},
    swagger_ui_init_oauth={
        "clientId": config("client_id"),
        "usePkceWithAuthorizationCodeGrant": True,
    },
)


@app.get("/api/health", status_code=status.HTTP_200_OK)
def get_health():
    return {"status": "ok"}


@app.get("/api/v1/ttf/")
def protected_get_ttf_user(
    longitude: float = Query(ge=-180, le=180),
    latitude: float = Query(ge=-90, le=90),
    user: bool = Depends(verify_user_role),
    ttf_service: TTFService = Depends(get_ttf_service),
):
    return ttf_service.get(latitude, longitude)


@app.get("/api/v1/admin")
def protected_admin(admin: bool = Depends(verify_admin_role)):
    return {"message": "This is a protected resource for ADMIN role."}


@app.get("/api/v1/admin/service")
def protected_sadmin(admin: bool = Depends(verify_sadmin_role)):
    return {"message": "This is a protected resource for APP_ADMIN role."}


@app.get("/api/v1/protected")
def protected_user(user: bool = Depends(verify_user_role)):
    return {"message": "This is a protected resource for USER role."}


@app.get("/api/v1/protected/service")
def protected_suser(user: bool = Depends(verify_suser_role)):
    return {"message": "This is a protected resource for APP_USER role."}


@app.get("/api/v1/public", status_code=status.HTTP_200_OK)
def public_user():
    return {"message": "This is a public resource for everyone."}


@app.get("/api/v1/")
def protected_user_query(user: bool = Depends(verify_user_locquery)):
    return {
        "message": "This is a protected resource for any user that is registered on a location."
    }


@app.get("/api/v1/{location}")
def protected_user_loc(location: str, user: bool = Depends(verify_user_path)):
    return {
        "message": f"This is a protected resource for any user that is registered on location = {location}."
    }
