from app.services.weather.weather_get import (
    process_weather_data,
    get_weather_data_for_coordinates,
)
from app.services.ttf_calculator import TTFCalculator
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


@app.get("/api/v1/ttf/")
def protected_get_ttf_user(
    longitude: float = Query(ge=-180, le=180),
    latitude: float = Query(ge=-90, le=90),
    user: bool = Depends(verify_user_role),
):
    try:
        weather_data_json = get_weather_data_for_coordinates(
            longitude=longitude, latitude=latitude
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to fetch weather data")
    weather_data_csv = process_weather_data(weather_data_json)
    ttf_points = TTFCalculator.calculate_from_csv(weather_data_csv)

    if not ttf_points:
        raise HTTPException(
            status_code=404, detail="No TTF data available for the given coordinates"
        )
    res = []
    for point in ttf_points:
        res.append(
            {
                "ttf": point.ttf,
                "weather_point": point.weather_point.model_dump(mode="json"),
            }
        )
    return res
