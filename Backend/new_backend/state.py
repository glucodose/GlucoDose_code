from collections import deque
from typing import Deque, Dict, Any, Optional
import time

MAX_HISTORY = 180          
START_BG = 254.0   # CHANGED: Start High for Demo

BASE_BASAL = 1.0           
TARGET_MIN_BG = 90        
TARGET_MAX_BG = 120    

# Increased ISF to match strong physics
ISF = 200.0

# STATUS FLAGS
system_running: bool = False
simulation_spike: bool = False
spike_countdown: int = 0

# COOLER & TEMP STATE
cooler_state: str = "OFF"
insulin_temperature: float = 30.0 # Default starting temp

glucose_history: Deque[Dict[str, Any]] = deque(maxlen=MAX_HISTORY)
last_bg: float = START_BG
basal_history: Deque[Dict[str, Any]] = deque(maxlen=120)

current_iob: float = 0.0             
last_delivery_time: float = 0.0      
motor_state: str = "OFF"             
suggested_rate: float = BASE_BASAL   

# MECHANICAL STATS
last_plunger_mm: float = 0.0
last_motor_rotations: float = 0.0
last_encoder_pulses: int = 0
last_bolus_amount: float = 0.0

def get_state_snapshot() -> Dict[str, Any]:
    history = list(glucose_history)
    basal_hist = list(basal_history)
    current_glucose = history[-1] if history else None
    latest_basal = basal_hist[-1] if basal_hist else None
    
    return {
        "timestamp": int(time.time() * 1000),
        "isRunning": system_running,
        "currentBG": current_glucose["bg"] if current_glucose else None,
        "currentTrend": current_glucose["trend"] if current_glucose else None,
        "currentIOB": round(current_iob, 2),
        "motorState": motor_state,
        "coolerState": cooler_state,       # New
        "insulinTemp": round(insulin_temperature, 1), # New
        "glucoseHistory": history,
        "basalHistory": basal_hist,
        "latestRecommendation": latest_basal,
        "pumpStats": {
            "plunger_mm": round(last_plunger_mm, 5),
            "rotations": round(last_motor_rotations, 5),
            "pulses": last_encoder_pulses,
            "last_dose": last_bolus_amount
        },
        "profile": {
            "base_basal": BASE_BASAL,
            "min_bg": TARGET_MIN_BG,
            "max_bg": TARGET_MAX_BG,
            "isf": ISF 
        },
    }