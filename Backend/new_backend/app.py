import asyncio
import random
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os

import state
from glucose_simulator import run_glucose_simulator
from fake_oref1 import run_fake_oref1
import cooler_control

# --- TEMPERATURE / HEAT SIMULATION ---
async def run_temperature_simulation():
    """
    Simulates the device heating up slowly over time.
    This forces the user to use the 'COOL' button.
    """
    print("🔥 Device Heating Simulation Started")
    
    # Start at a realistic ambient temp
    state.insulin_temperature = 26.9
    
    while True:
        # Check Pause
        if not state.system_running:
            await asyncio.sleep(1)
            continue

        # Only heat up if the cooler is OFF
        if state.cooler_state == "OFF":
            # Add small incremental heat (Simulating motor heat/battery heat)
            # 0.005 to 0.02 degrees per second
            # This causes the display (rounded to 0.1) to tick up every ~10 seconds.
            heat_creep = random.uniform(0.005, 0.002)
            state.insulin_temperature += heat_creep
            
        # If Cooler is ON, cooler_control.py handles the rapid drop.
        
        await asyncio.sleep(1.0) # Run every second

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch background tasks
    asyncio.create_task(run_glucose_simulator())
    asyncio.create_task(run_fake_oref1())
    asyncio.create_task(run_temperature_simulation()) # New heating logic
    print("🚀 System Started: API + Logic + Heat Sim")
    yield
    # Shutdown
    print("🛑 System Shutting Down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(): return {"status": "ok"}

@app.get("/state")
async def get_state_http(): return state.get_state_snapshot()

@app.websocket("/ws/glucose")
async def ws_glucose(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            snapshot = state.get_state_snapshot()
            await ws.send_json(snapshot)
            await asyncio.sleep(1.0) 
    except WebSocketDisconnect: print("🔌 Client disconnected")

@app.post("/spike")
async def trigger_spike():
    state.simulation_spike = True
    state.spike_countdown = 3
    print("⚠️ MANUAL SPIKE TRIGGERED")
    return {"status": "ok"}

@app.post("/start")
async def start_system():
    state.system_running = True
    return {"status": "started"}

@app.post("/stop")
async def stop_system():
    state.system_running = False
    return {"status": "stopped"}

@app.post("/cooler")
async def manual_cooler():
    if state.cooler_state == "OFF":
        asyncio.create_task(cooler_control.trigger_cooler())
        return {"status": "cooling started"}
    return {"status": "already cooling"}

# Serve Frontend
if os.path.isdir("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)