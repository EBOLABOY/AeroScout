import logging
from fastapi import FastAPI, APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import database connection functions
from app.database.connection import connect_db, disconnect_db
# Import settings if needed, e.g., for app metadata
from app.core.config import settings
from app.core import dynamic_fetcher # Added for initial cookie loading
from app.core.token_scheduler import start_token_scheduler, stop_token_scheduler  # 添加 token 调度器
from app.core.redis_manager import redis_manager  # 添加 Redis 管理器
from app.core.search_session_manager import search_session_manager  # 添加搜索会话管理器

# Import API endpoint routers
from app.apis.v1.endpoints import auth, users, admin, poi, tasks, legal # Added legal for legal content endpoints
from app.apis.v2.endpoints import flights as flights_v2  # Added V2 flights endpoints
from app.apis.v2.endpoints import simplified_flights  # Added simplified flights endpoints

# --- Logging Configuration ---
# Configure basic logging. In a real application, you might use a more robust setup (e.g., file logging, structured logging).
# 从配置文件读取日志级别
from app.core.config import settings
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.WARNING)
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info(f"日志级别设置为: {settings.LOG_LEVEL}")
# --- End Logging Configuration ---


# --- Lifespan Management ---
# Define lifespan context manager for startup/shutdown events (FastAPI >= 0.90)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    Connects to the database on startup and disconnects on shutdown.
    """
    print("Application startup: Connecting to database...")
    await connect_db()

    print("Application startup: Initializing Redis connection...")
    try:
        await redis_manager.initialize()
        print("Redis connection initialized successfully")
    except Exception as e:
        print(f"Redis initialization failed: {e}")
        print("Application will continue with memory-based session storage")

    print("Application startup: Initializing search session manager...")
    await search_session_manager.initialize()

    print("Application startup: Loading initial Trip.com cookies...")
    await dynamic_fetcher.load_initial_trip_cookies() # Load cookies after DB connection
    print("Application startup: Starting Token Scheduler (Kiwi auto-refresh)...")
    await start_token_scheduler()  # 启动 token 调度器，替换单次加载
    try:
        yield # Application runs here
    finally:
        print("Application shutdown: Stopping Token Scheduler...")
        await stop_token_scheduler()  # 停止 token 调度器
        print("Application shutdown: Closing Redis connection...")
        await redis_manager.close()
        print("Application shutdown: Disconnecting from database...")
        await disconnect_db()

# Create FastAPI application instance with lifespan manager
app = FastAPI(
    title="AeroScout API",
    description="API for AeroScout flight and airport information services.",
    version="0.1.0", # Example version
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# Root endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint providing a welcome message.
    """
    return {"message": "Welcome to AeroScout API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Global health check endpoint
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "message": "AeroScout API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

# --- API Routers ---
# Create a main router for V1 APIs
api_router_v1 = APIRouter(prefix="/api/v1")

# Include endpoint routers into the V1 router
api_router_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router_v1.include_router(users.router, prefix="/users", tags=["Users"])
api_router_v1.include_router(admin.router, prefix="/admin", tags=["Admin"]) # Includes admin endpoints
api_router_v1.include_router(poi.router, prefix="/poi", tags=["POI"]) # Added POI endpoints
api_router_v1.include_router(tasks.router, prefix="/tasks", tags=["Tasks"]) # Added tasks endpoints
api_router_v1.include_router(legal.router, prefix="/legal", tags=["Legal"]) # Added legal endpoints

# Create a main router for V2 APIs
api_router_v2 = APIRouter(prefix="/api/v2")

# Include V2 endpoint routers
api_router_v2.include_router(flights_v2.router, tags=["Flights V2"])
api_router_v2.include_router(simplified_flights.router, prefix="/flights", tags=["Simplified Flights"])

# Include both V1 and V2 routers into the main application
app.include_router(api_router_v1)
app.include_router(api_router_v2)

# --- End API Routers ---


# --- Global Exception Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles FastAPI's built-in HTTPException.
    Logs the error and returns a JSON response matching the exception's details.
    """
    logger.error(f"HTTPException caught: Status Code={exc.status_code}, Detail='{exc.detail}'")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None), # Include headers if they exist
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic validation errors that occur during request processing.
    Logs the specific validation errors and returns a 422 Unprocessable Entity response.
    """
    # Log the detailed validation errors
    error_details = exc.errors()
    logger.error(f"Request Validation Error: Path='{request.url.path}', Errors={error_details}")
    # Return a structured error response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": error_details},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any other unhandled exceptions that occur during request processing.
    Logs the exception with traceback and returns a generic 500 Internal Server Error response.
    """
    # Use logger.exception to include the full traceback
    logger.exception(f"Unhandled Exception caught: Path='{request.url.path}', Error='{exc}'")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

# --- End Global Exception Handlers ---


# Example of how to run the app using uvicorn (for local development)
# if __name__ == "__main__":
#     import uvicorn
#     # Note: Running directly like this might bypass some environment loading mechanisms.
#     # It's generally better to run via `uvicorn aeroscouthq_backend.app.main:app --reload`
#     uvicorn.run(app, host="0.0.0.0", port=8000)