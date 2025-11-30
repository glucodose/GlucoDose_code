import asyncio
import time
import random
import state

# --- CONFIGURATION ---
INTERVAL_SECONDS = 5  

# CHANGED: Increased to 25.0 to handle the high start (295) effectively
INSULIN_POWER_FACTOR = 23.0

IOB_DECAY_RATE = 0.004 
_trend_drift = 0.4 

def _step_bg_physics(prev_bg: float) -> float:
    global _trend_drift
    
    # 1. SPIKE HANDLING
    if state.spike_countdown > 0:
        print(f"🍬 SUPER SPIKE ACTIVE! Ticks left: {state.spike_countdown}")
        _trend_drift = 6.0 
        state.spike_countdown -= 1
    else:
        # 2. NORMAL PHYSICS
        change = random.uniform(-0.05, 0.1) 
        _trend_drift += change
        
        # Brake: If IOB exists, kill upward momentum
        if state.current_iob > 0.05:
            _trend_drift -= (state.current_iob * 0.5) 
            
        _trend_drift = max(-2.0, min(2.0, _trend_drift)) 

    # 3. INSULIN DROP (Stronger now with Factor 25.0)
    insulin_drop = 0
    if state.current_iob > 0:
        insulin_drop = -(state.current_iob * INSULIN_POWER_FACTOR)

    # 4. SAFETY FLOOR
    liver_resistance = 0
    if prev_bg < 110: 
        dist = (110 - prev_bg)
        liver_resistance = dist * 0.5 

    noise = random.uniform(-0.05, 0.05)
    new_bg = prev_bg + _trend_drift + insulin_drop + liver_resistance + noise
    
    # Absolute Limits
    new_bg = max(80.0, min(400.0, new_bg))
    
    # 5. METABOLISM
    if state.current_iob > 0:
        state.current_iob -= IOB_DECAY_RATE
        if state.current_iob < 0: state.current_iob = 0

    return new_bg

def seed_glucose_history():
    if state.glucose_history: return
    now = time.time()
    # Seed with the High Start Value
    sim_bg = state.START_BG 
    for i in range(state.MAX_HISTORY):
        # Create a history that was flat/high
        t = now - ((state.MAX_HISTORY - i) * INTERVAL_SECONDS)
        state.glucose_history.append({
            "ts": int(t * 1000), "bg": int(sim_bg), "trend": "Flat"
        })
    state.last_bg = sim_bg 
    print(f"✅ Physics Engine Ready. Starting BG: {state.START_BG}")

async def run_glucose_simulator():
    if not state.glucose_history: seed_glucose_history()
    print("✅ Physics Task Started.")
    while True:
        if not state.system_running:
            await asyncio.sleep(1)
            continue
            
        prev_bg = state.last_bg
        new_bg = _step_bg_physics(prev_bg)
        state.last_bg = new_bg
        
        delta = new_bg - prev_bg
        if delta > 1.0: t = "Rising"
        elif delta > 0.3: t = "Slight Up"
        elif delta < -1.0: t = "Falling"
        elif delta < -0.3: t = "Slight Down"
        else: t = "Flat"
        
        state.glucose_history.append({
            "ts": int(time.time() * 1000), "bg": int(new_bg), "trend": t
        })
        
        await asyncio.sleep(INTERVAL_SECONDS)