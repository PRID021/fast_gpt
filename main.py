from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data import models
from data.database import engine

# routers
from routers import authenticate, chat, profile

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# import other routers

app.include_router(authenticate.router)
app.include_router(chat.router)
# app.include_router(profile.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=14433)
