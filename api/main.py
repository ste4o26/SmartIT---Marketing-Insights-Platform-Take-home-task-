import dotenv
import fastapi

from api.constants import SERVICE_URI_PREFIX
from api.middlewares import register_middlewares
from api.routers import auth
from api.routers import crypto

dotenv.load_dotenv()

app = fastapi.FastAPI()
register_middlewares(app)
app.include_router(auth.router, prefix=f"/{SERVICE_URI_PREFIX}")
app.include_router(crypto.router, prefix=f"/{SERVICE_URI_PREFIX}")
