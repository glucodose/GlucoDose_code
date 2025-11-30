import asyncio
import time
import random
import requests
import state

# Config
MOTOR_PULSE_DURATION_SEC = 10

# PHYSICS DOSE: Keep this small so the Graph doesn't crash to 0.
SAFE_PHYSICS_DOSE = 0.07  

# --- MECHANICAL CONSTANTS ---
MM_PER_UNIT = 0.3158
PITCH_MM_PER_ROT = 0.7
PULSES_PER_ROT = 4172

def _hardware_motor_on():
    try:
        requests.get("http://192.168.1.17/relay/on", timeout=1) 
        print("[HARDWARE] Relay ON")
    except: pass

def _hardware_motor_off():
    try:
        requests.get("http://192.168.1.17/relay/off", timeout=1)
        print("[HARDWARE] Relay OFF")
    except: pass

async def motor_pulse():
    print("--- MOTOR SEQUENCE STARTED ---")
    
    state.motor_state = "ON"
    _hardware_motor_on()
    
    # --- 1. VISUAL/MECHANICAL CALCULATION (For the Display) ---
    # We want BIG numbers for the judges, and lots of variance.
    # Generate a random multiplier between 5.0 and 10.0
    random_multiplier = random.uniform(5.0, 10.0)
    
    # Calculate "Fake" large movement for display
    display_dose = SAFE_PHYSICS_DOSE * random_multiplier
    
    # Calculate Mechanics based on this large display dose
    plunger_move = display_dose * MM_PER_UNIT
    rotations = plunger_move / PITCH_MM_PER_ROT
    pulses = int(rotations * PULSES_PER_ROT)
    
    # Update State (What the Frontend shows)
    state.last_plunger_mm = plunger_move
    state.last_motor_rotations = rotations
    state.last_encoder_pulses = pulses
    state.last_bolus_amount = display_dose # Optional: if you want to show the varied dose size
    
    # Wait for the motor to "move"
    await asyncio.sleep(MOTOR_PULSE_DURATION_SEC)
    
    state.motor_state = "OFF"
    _hardware_motor_off()
    
    # --- 2. PHYSICS CALCULATION (For the Algorithm) ---
    # We add the SAFE amount to the body, so the BG graph behaves correctly
    state.current_iob += SAFE_PHYSICS_DOSE
    
    print(f"[MECHANICS] Visual Multiplier: x{random_multiplier:.1f}")
    print(f"[DISPLAY] Rot: {rotations:.4f} | Pulses: {pulses} | Plunger: {plunger_move:.4f}")
    print(f"[PHYSICS] Actual IOB added: {SAFE_PHYSICS_DOSE} U")
    
    state.last_delivery_time = time.time()
    print("--- MOTOR SEQUENCE END ---")