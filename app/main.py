from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.api import api_router
from .services.visit_counter import VisitCounterService
import asyncio
from contextlib import asynccontextmanager

# Global service instance
visit_counter_service = VisitCounterService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background flusher task that runs every 30 seconds
    visit_counter_service.background_task = asyncio.create_task(visit_counter_service.batchFlusher())
    print("Started background buffer flusher task")
    yield
    # Stop the task on shutdown and ensure a final flush
    if visit_counter_service.background_task:
        visit_counter_service.running = False
        visit_counter_service.background_task.cancel()
        try:
            await visit_counter_service.background_task
        except asyncio.CancelledError:
            pass
        # Final flush of any remaining buffered data to Redis on shutdown
        print("Performing final flush before shutdown")
        await visit_counter_service.flush_buffer()

app = FastAPI(title="Visit Counter Service", lifespan=lifespan)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "healthy"}

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX) 