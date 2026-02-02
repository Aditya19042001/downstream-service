"""
Downstream Slow Service
A mock external API service that responds slowly to simulate real-world dependencies.
Used for testing cascade failures, timeouts, and downstream latency impacts.

Author: Your Name
Repository: https://github.com/yourusername/downstream-slow-service
Related: backend-load-testing (main service)
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
import random
import os
import logging
from datetime import datetime

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application configuration
DEFAULT_DELAY = int(os.getenv("DEFAULT_DELAY", "3"))
MAX_DELAY = int(os.getenv("MAX_DELAY", "30"))
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.0"))

app = FastAPI(
    title="Downstream Slow Service",
    description="Mock external API for testing backend resilience",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request counter
request_count = 0

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "downstream-slow-service",
        "version": "1.0.0",
        "status": "operational",
        "purpose": "Simulates slow external API dependencies",
        "endpoints": {
            "/health": "Health check",
            "/slow": "Configurable delay response",
            "/random": "Random delay response",
            "/sometimes-fail": "Randomly fails based on failure rate",
            "/timeout-trap": "Very long response (60s)",
            "/stats": "Service statistics"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "operational"
    }

@app.get("/slow")
async def slow_response(
    delay: int = Query(
        default=DEFAULT_DELAY,
        ge=1,
        le=MAX_DELAY,
        description="Delay in seconds"
    )
):
    """
    Responds after specified delay
    Use this to test timeout handling and downstream latency impact
    """
    global request_count
    request_count += 1
    
    logger.info(f"Slow request received - delay: {delay}s")
    start = time.time()
    
    await asyncio.sleep(delay)
    
    duration = time.time() - start
    
    return {
        "status": "success",
        "requested_delay": delay,
        "actual_duration": round(duration, 3),
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"Responded after {delay} seconds"
    }

@app.get("/random")
async def random_delay(
    min_delay: int = Query(default=1, ge=0, le=10),
    max_delay: int = Query(default=10, ge=1, le=30)
):
    """
    Responds after random delay between min and max
    Simulates unpredictable external API behavior
    """
    delay = random.uniform(min_delay, max_delay)
    logger.info(f"Random delay request - {delay:.2f}s")
    
    start = time.time()
    await asyncio.sleep(delay)
    duration = time.time() - start
    
    return {
        "status": "success",
        "delay_seconds": round(delay, 3),
        "actual_duration": round(duration, 3),
        "range": {"min": min_delay, "max": max_delay}
    }

@app.get("/sometimes-fail")
async def sometimes_fail(
    failure_rate: float = Query(
        default=FAILURE_RATE,
        ge=0.0,
        le=1.0,
        description="Probability of failure (0.0 to 1.0)"
    ),
    delay: int = Query(default=2, ge=0, le=10)
):
    """
    Randomly fails based on failure_rate
    Use this to test error handling and retry logic
    """
    logger.info(f"Sometimes-fail request - failure_rate: {failure_rate}")
    
    # Simulate processing time
    await asyncio.sleep(delay)
    
    # Randomly fail
    if random.random() < failure_rate:
        logger.warning("Request failed (simulated)")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Random failure occurred",
                "failure_rate": failure_rate,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return {
        "status": "success",
        "message": "Request succeeded",
        "failure_rate": failure_rate,
        "delay_seconds": delay
    }

@app.get("/timeout-trap")
async def timeout_trap():
    """
    Takes 60 seconds to respond
    Designed to cause timeouts in calling services
    Use this to test timeout configuration
    """
    logger.warning("Timeout trap triggered - will take 60 seconds")
    await asyncio.sleep(60)
    
    return {
        "status": "completed",
        "message": "You actually waited 60 seconds!",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/burst-error")
async def burst_error(
    error_duration: int = Query(default=30, ge=1, le=300)
):
    """
    Returns errors for specified duration
    Simulates temporary service degradation
    """
    # This is a simple implementation - in real scenario you'd use Redis/cache
    logger.warning(f"Burst error mode - all requests will fail for {error_duration}s")
    
    raise HTTPException(
        status_code=503,
        detail={
            "error": "Service Unavailable",
            "message": "Service is temporarily degraded",
            "retry_after": error_duration
        }
    )

@app.get("/stats")
async def stats():
    """Service statistics"""
    return {
        "total_requests": request_count,
        "service": "downstream-slow-service",
        "config": {
            "default_delay": DEFAULT_DELAY,
            "max_delay": MAX_DELAY,
            "failure_rate": FAILURE_RATE
        }
    }

@app.get("/cascade")
async def cascade_endpoint(
    levels: int = Query(default=3, ge=1, le=5)
):
    """
    Simulates cascade of slow operations
    Each level adds delay
    """
    total_delay = 0
    results = []
    
    for level in range(levels):
        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)
        total_delay += delay
        
        results.append({
            "level": level + 1,
            "delay": round(delay, 3)
        })
    
    return {
        "status": "success",
        "total_levels": levels,
        "total_delay": round(total_delay, 3),
        "cascade_results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
        log_level="info"
    )