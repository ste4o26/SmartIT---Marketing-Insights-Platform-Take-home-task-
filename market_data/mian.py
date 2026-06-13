import fastapi
from market_data.routers import crypto

app = fastapi.FastAPI()
app.include_router(crypto.router)