from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 1. Cleaned up imports (no duplicates!)
from app.api.routes import auth, aws, sync
from app.core.scheduler import scheduler
from app.api.routes import auth, aws, sync, recommendations, anomalies, dashboard

# 2. Lifespan events (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server STARTS
    scheduler.start()
    yield
    # This runs when the server STOPS
    scheduler.shutdown()

# 3. Instantiate the app EXACTLY ONCE
app = FastAPI(title="Cloud Cost Optimizer API", lifespan=lifespan)

# 4. Add CORS Middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. The Health Check Route
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

# 6. Register Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(aws.router, prefix="/api/aws", tags=["AWS Integration"])
app.include_router(sync.router, prefix="/api/sync", tags=["Data Sync"])

app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])