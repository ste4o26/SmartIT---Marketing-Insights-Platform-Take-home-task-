import fastapi
from market_data.constants import SERVICE_URI_PREFIX
from market_data.routers import crypto

app = fastapi.FastAPI()
app.include_router(crypto.router, prefix=f"/{SERVICE_URI_PREFIX}")