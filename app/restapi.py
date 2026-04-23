import logging

from app.factory import get_ttf_service
from app.services.ttf.ttf_service import TTFService
from decouple import config
from fastapi import FastAPI, Depends, status, Query, HTTPException
from app.kc.auth import (
    verify_admin_role,
)

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight": False},
    swagger_ui_init_oauth={
        "clientId": config("client_id", default="firebuster-api"),
        "usePkceWithAuthorizationCodeGrant": True,
    },
)

logger = logging.getLogger(__name__)


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
    # Logging to register activity
    logger.info("Incoming TTF request lat=%s lon=%s", latitude, longitude)

    ## try except block for getting results and logging number of points
    try:
        result = ttf_service.get(latitude, longitude)
        logger.info(
            "TTF request succeeded lat=%s lon=%s points=%s",
            latitude,
            longitude,
            len(result.ttf_points),
        )
        return result
    # There are multiple possible exceptions that can happen throughout the service call. These we handle depending on exception type
    except HTTPException as e:
        logger.warning(
            "TTF request failed lat=%s lon=%s status=%s detail=%s",
            latitude,
            longitude,
            e.status_code,
            e.detail,
        )
        raise
    except ConnectionError as e:
        logger.warning(
            "TTF weather unavailable lat=%s lon=%s detail=%s",
            latitude,
            longitude,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except ValueError as e:
        logger.warning(
            "TTF upstream data issue lat=%s lon=%s detail=%s",
            latitude,
            longitude,
            str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except RuntimeError as e:
        logger.error(
            "TTF internal failure lat=%s lon=%s detail=%s",
            latitude,
            longitude,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception:
        logger.exception(
            "Unhandled TTF request failure lat=%s lon=%s", latitude, longitude
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error while handling TTF request",
        )


@app.get("/")
def read_root():
    return {"message": "Hello Firebuster API!"}
