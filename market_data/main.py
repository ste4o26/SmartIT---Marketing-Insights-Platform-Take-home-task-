import dotenv
import fastapi

from market_data.constants import SERVICE_URI_PREFIX
from market_data.middlewares import register_middlewares
from market_data.routers import crypto

dotenv.load_dotenv()
app = fastapi.FastAPI()
register_middlewares(app)
app.include_router(crypto.router, prefix=f"/{SERVICE_URI_PREFIX}")
