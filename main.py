from fastapi import FastAPI, Query
import asyncio
import time
import random

app = FastAPI(title="Downstream Service (Slow)")

@app.get("/")
async def root():
    return {"service": "downstream", "status": "operational"}

@app.get("/slow")
async def slow_response(
    delay: int = Query(default=5, ge=1, le=30)
):
    """Responds after specified delay"""
    start = time.time()
    await asyncio.sleep(delay)
    duration = time.time() - start
    
    return {
        "status": "success",
        "requested_delay": delay,
        "actual_duration": duration,
        "message": f"Response delayed by {delay} seconds"
    }

@app.get("/random")
async def random_delay():
    """Random delay between 1-10 seconds"""
    delay = random.uniform(1, 10)
    await asyncio.sleep(delay)
    
    return {
        "status": "success",
        "delay": delay
    }

@app.get("/sometimes-fail")
async def sometimes_fail(
    failure_rate: float = Query(default=0.3, ge=0.0, le=1.0)
):
    """Fails randomly based on failure_rate"""
    if random.random() < failure_rate:
        raise Exception("Random failure occurred")
    
    await asyncio.sleep(2)
    return {"status": "success"}

@app.get("/timeout-trap")
async def timeout_trap():
    """Takes very long time - designed to cause timeouts"""
    await asyncio.sleep(60)
    return {"status": "completed", "message": "You waited 60 seconds!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
