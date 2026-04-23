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
        "clientId": config("client_id", default="firebuster-api"),
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
    admin: bool = Depends(verify_admin_role),
    ttf_service: TTFService = Depends(get_ttf_service),
):
    return ttf_service.get(latitude, longitude)
