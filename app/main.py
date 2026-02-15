from fastapi import FastAPI

app = FastAPI()


@app.get("/api/health")
def get_health():
    return {"Status": "ok"}
