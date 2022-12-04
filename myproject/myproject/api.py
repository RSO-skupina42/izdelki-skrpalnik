from fastapi import FastAPI, Response, Request, Depends, Query
from fastapi_database import get_db, Database
from pydantic import BaseModel
from typing import List
from typing import Union


class Product(BaseModel):
    title: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[str, None] = None
    # description: Union[str, None] = None
    # description: Union[str, None] = None


class Descriptor(BaseModel):
    fields: str
    table: str
    limit: int
    offset: int


class ResponseProducts(BaseModel):
    data: Union[List[Product], None]
    desc: Union[Descriptor, None]
    message: str


app = FastAPI(title="Izdelki skrpalnik", description="Api za pridobivanje podatkov o izdelkih iz strani spletnih trgovin.")


@app.on_event("shutdown")
def shutdown_event(db: Database = Depends(get_db)):
    db.disconnect_db()


@app.get("/products", response_model=ResponseProducts, description="Vrne izdelke iz trgovine.")
async def predict_eh(request: Request,
                     response: Response,
                     db: Database = Depends(get_db),
                     fields="title,description,price",
                     table="spar",
                     limit=10,
                     offset=0):

    query = f"SELECT {fields} FROM {table} LIMIT {limit} OFFSET {offset}"
    print(query)

    test_table = db.get_table(query)
    data, desc = None, None
    if test_table:
        data = [Product(**{key: p[i] for i, key in enumerate(fields.split(","))}) for p in test_table]
        desc = {
                "fields": fields,
                "table": table,
                "limit": limit,
                "offset": offset,
            }
        msg = "OK"
    else:
        msg = "Not ok."

    return {
        "data": data,
        "desc": desc,
        "message": msg,
    }
