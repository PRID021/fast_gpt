from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from http import HTTPStatus
from typing import Any, Generic, TypeVar,Optional
from fastapi.responses import StreamingResponse
import asyncio
import json


T = TypeVar("T")

app = FastAPI()

# class Item(BaseModel):
#     name:str
#     price:float
#     is_offer: Union[bool,None] = None



# @app.get("/",tags=["Test"])
# def read_root():
#     return {"Hello":"World"}

# @app.get("/items/{item_id}",tags=["Item"])
# def read_item(item_id: int, q:Union[str,None] = None):
#     return {'item_id':item_id,'q':q}

# class ItemResponse(BaseModel):
#     id: int
#     name:str
#     create_at: datetime

# @app.put("/items/{item_id}",tags=['Item'],status_code= HTTPStatus.CREATED, response_model= ItemResponse)
# def update_item(item_id:int,item:Item):
#     return  ItemResponse(id=item_id,name=item.name,create_at=datetime.now)

class Order(BaseModel):
    product: str
    units: int

class Product(BaseModel):
    name: str
    notes: str

class Response(BaseModel,Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None


@app.get('/ok',tags=['TEST'],status_code=HTTPStatus.OK,response_model=Response[None])
async def ok_endpoint():
    return Response[None](status_code=HTTPStatus.OK,message="Wellcome!",data=None)

@app.get('/hello')
async def hello_endpoint(name: str = 'World'):
    return {"message": f"Hello, {name}!"}

@app.post('/orders')
async def place_order(product: str, units: int):
    return {'message':f'Order for {units} units of {product} placed successfully'}




@app.post('/oders_pydantic', tags=["Orders"], response_model=Response[Order])
async def place_order(order: Order):
    return Response[Order](status_code=HTTPStatus.ACCEPTED,
                    message= f"Order for {order.units} units of {order.product} placed successfully",
                    data= order)

class MessageResponse(BaseModel):
    event_id: int
    data: str
    is_last_event: bool
    def toJson(self):
        return json.dumps({"event_id": self.event_id,"data": self.data,"is_last_event":self.is_last_event})

@app.get("/chat",tags=["CHAT"])
async def chat_stream():
    async def fake_video_streamer():
        for i in range(10):
            yield MessageResponse(event_id=i,data="some random data",is_last_event=(i==9)).toJson() + "\n"
            await asyncio.sleep(0.5)
           

    return StreamingResponse(fake_video_streamer(),media_type="application/x-ndjson")