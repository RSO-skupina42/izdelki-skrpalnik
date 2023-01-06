from fastapi import FastAPI, Response, Request, Depends, Query
from fastapi_database import get_db, Database
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from typing import Union
from run_spider_process import execute

import sentry_sdk
from sentry_sdk import set_level
from config import *

# enable logging
sentry_sdk.init(
    dsn=conf_sentry_dsn,
    traces_sample_rate=conf_sentry_traces_sample_rate,
    debug=conf_sentry_debug,
    server_name=conf_sentry_server_name,
    release=conf_sentry_release,
    environment=conf_sentry_environment,
)
set_level("info")


class Product(BaseModel):
    id: str = None
    store_elem_id: Union[str, None] = None
    store_name: Union[str, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    category: Union[str, None] = None
    sales_unit: Union[str, None] = None
    item_size: Union[str, None] = None
    price: Union[float, None] = None
    url: Union[str, None] = None


class Descriptor(BaseModel):
    fields: str
    # table: str
    limit: int
    offset: int


class ResponseProducts(BaseModel):
    data: Union[List[Product], None]
    desc: Union[Descriptor, None]
    message: str


app = FastAPI(
    title="Skrpalnik izdelkov",
    description="Api za pridobivanje podatkov o izdelkih iz strani spletnih trgovin.",
    root_path="/scrapy",
    docs_url="/openapi",
)

origins = [
    ""
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/demo/fill-store-data", description="V bazo naloži sveže podatke o izdelkih iz trgovin.")
async def fill_store_database():
    return StreamingResponse(execute(["scrapy", "crawl", "myspider"]), media_type="text/plain")


@app.get("/products", response_model=ResponseProducts, description="Vrne iskane filtrirane izdelke iz trgovin.")
async def get_products(request: Request,
                     response: Response,
                     store_elem_id: Union[str, None]=None,
                     store_name: Union[str, None]=None,
                     title: Union[str, None]=None,
                     description: Union[str, None]=None,
                     category: Union[str, None]=None,
                     item_size: Union[str, None]=None,
                     price: Union[str, None]=None,
                     db: Database = Depends(get_db),
                     fields="id,store_elem_id,store_name,title,description,category,sales_unit,item_size,price,url",
                     # store_name="spar",
                     limit=10,
                     offset=0):

    # TODO: add filtering based on store_name
    # if store_elem_id is None: store_elem_id = "store_elem_id"

    query = f"SELECT {fields} FROM stores"
    columns = [(store_elem_id, "store_elem_id"),
               (store_name, "store_name"),
               (title, "title"),
               (description, "description"),
               (category, "category"),
               (item_size, "item_size"),
               (price, "price")]
    if any([c for c, n in columns]):
        query += f" WHERE"

    for column, name in columns:
        if column is not None:
            query += f" LOWER({name}) LIKE LOWER('%{column}%') AND"
    if query[-4:] == " AND":
        query = query[:-4]
    query += f" LIMIT {limit} OFFSET {offset}"
    print(query)

    test_table = db.get_table(query)
    data, desc = None, None
    if test_table:
        data = [Product(**{key: p[i] for i, key in enumerate(fields.split(","))}) for p in test_table]
        desc = {
                "fields": fields,
                # "table": table,
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
