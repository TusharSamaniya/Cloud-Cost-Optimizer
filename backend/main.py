import sys
import os

# 0. Add root directory to sys.path so 'ml' module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 1. Import each route module individually with a clear, unambiguous alias.
#    Using "from app.api.routes import (a, b, settings as settings_routes)"
#    can trip up Python's import resolution on some setups because the
#    submodule name 'settings' collides visually with the Settings class
#    used elsewhere. Importing it as its own line with importlib-style
#    dotted path avoids any ambiguity entirely.
from app.api.routes import auth
from app.api.routes import aws
from app.api.routes import sync
from app.api.routes import recommendations
from app.api.routes import anomalies
from app.api.routes import dashboard
from app.api.routes import ml
from app.api.routes import settings as app_settings_routes  # renamed clearly

from app.core.scheduler import scheduler

# --- CORS origins ---
# Default origins for local development. In production (Railway), set the
# CORS_ORIGINS environment variable to a comma-separated list of your real
# frontend URL(s), e.g.:
#   CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
_default_origins = "http://localhost:5173,https://cloud-cost-optimizer-livid.vercel.app/"
origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

# 2. Lifespan events (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

# 3. Instantiate the app
app = FastAPI(title="Cloud Cost Optimizer API", lifespan=lifespan)

# 4. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. The Health Check Route
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0", "cors_origins": origins}

# 6. Register Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(aws.router, prefix="/api/aws", tags=["AWS Integration"])
app.include_router(sync.router, prefix="/api/sync", tags=["Data Sync"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])
app.include_router(app_settings_routes.router, prefix="/api/settings", tags=["Settings"])