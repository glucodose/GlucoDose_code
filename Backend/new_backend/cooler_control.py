import asyncio
import requests
import state

# Cooler runs for 5 seconds
COOLER_DURATION = 30

def _hardware_cooler_on():
    try:
        # Example URL for your relay
        requests.get("http://192.168.1.17/cooler/on", timeout=1) 
        print("[HARDWARE] Cooler ON")
    except: pass

def _hardware_cooler_off():
    try:
        requests.get("http://192.168.1.17/cooler/off", timeout=1)
        print("[HARDWARE] Cooler OFF")
    except: pass

async def trigger_cooler():
    print("❄️ COOLER SEQUENCE STARTED")
    state.cooler_state = "ON"
    _hardware_cooler_on()
    
    # While cooler is on, drop the temp in state for visual effect
    # Drop temp by 2 degrees over 5 seconds
    start_temp = state.insulin_temperature
    
    for _ in range(COOLER_DURATION):
        await asyncio.sleep(1)
        # Visually drop temp while cooling
        state.insulin_temperature -= 0.1
        
    state.cooler_state = "OFF"
    _hardware_cooler_off()
    print("❄️ COOLER SEQUENCE END")