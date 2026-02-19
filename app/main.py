from fastapi import FastAPI

app = FastAPI(title="Firebuster API")

@app.get("/api/health")
def get_health():
    return {"status": "ok"}


# Added example path parameter handlers from FastAPI documentation https://fastapi.tiangolo.com/tutorial/path-params/

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.get("/items-types/{item_id}")
async def read_item_types(item_id: int):
    return {"item_id": item_id}

# Query parameter 
# can be tested with `curl "http://127.0.0.1:8000/items/?skip=0&limit=10"`
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item_query(skip: int = 0, limit: int =10):
    return fake_items_db[skip: skip+limit]

# For more complex handlers check out the tutorials in the FastAPI documentation: https://fastapi.tiangolo.com/tutorial/
