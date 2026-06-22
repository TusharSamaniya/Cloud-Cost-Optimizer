from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 1. Lifespan events (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting up... Ready to optimize costs!")
    # Later, we will add database connection logic here
    yield
    print("Server is shutting down...")

# 2. Instantiate the FastAPI application
app = FastAPI(title="Cloud Cost Optimizer API", lifespan=lifespan)

# 3. Add CORS Middleware (Allows your future React frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, we restrict this. For now, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. The Health Check Route
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}