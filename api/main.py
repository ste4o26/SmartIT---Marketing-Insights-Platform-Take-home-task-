import fastapi
from api.constants import SERVICE_URI_PREFIX
from api.routers import auth

app = fastapi.FastAPI()
app.include_router(auth.router, prefix=f"/{SERVICE_URI_PREFIX}")
