from fastapi import FastAPI
from .routes import router
from .database import Base, engine
app = FastAPI()




Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tournament Platform API", version="1.0")


  

app.include_router(router)

app.include_router(router, prefix="/api", tags=["Users"])

app.include_router(router, prefix="/api", tags=["API Endpoints"])

app.include_router(router, prefix="/api", tags=["Teams"])



