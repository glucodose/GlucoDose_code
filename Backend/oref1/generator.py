# data_simulator.py
import json
import time
import random
from collections import deque
import os

# --- Configuration ---
OREF1_DATA_PATH = 'E:/oref1/oref0-master/data'
HISTORY_MINUTES = 60
READING_INTERVAL_SECONDS = 10 # We'll generate a reading every minute for realism

# --- Initial State ---
current_bg = 130
# A deque will automatically manage our 60-minute history
glucose_history = deque(maxlen=HISTORY_MINUTES) 

def setup_static_files():
    """Create the other required files so the main loop doesn't fail."""
    # This is a valid, simple profile
    profile_data = {
        "current_basal": 1.0, "max_iob": 5, "min_bg": 100, "max_bg": 110,
        "sens": [{"i": 0, "start": "00:00", "value": 50, "offset": 0}],
        "basal": [{"i": 0, "start": "00:00", "value": 1.0, "minutes": 0}],
        "carb_ratio": [{"i": 0, "start": "00:00", "value": 10, "offset": 0}],
        "timezone": "UTC"
    }
    with open(os.path.join(OREF1_DATA_PATH, 'profile.json'), 'w') as f:
        json.dump(profile_data, f)
        
    # For testing, we'll assume IOB is always zero
    iob_data = {"iob": 0, "activity": 0, "basaliob": 0, "bolusiob": 0}
    with open(os.path.join(OREF1_DATA_PATH, 'iob.json'), 'w') as f:
        json.dump(iob_data, f)

    # An empty placeholder for temp_basal
    with open(os.path.join(OREF1_DATA_PATH, 'temp_basal.json'), 'w') as f:
        json.dump({}, f)

    print("Static files (profile.json, iob.json, temp_basal.json) are set up.")


def generate_new_reading_and_update_file():
    """Simulates a new BG reading, adds to history, and overwrites the JSON file."""
    global current_bg
    
    # Introduce a small, random drift to the BG
    drift = random.uniform(-2, 2)
    current_bg += drift
    
    # Create the new reading object
    new_reading = {
        # Using unix timestamp in milliseconds
        "date": int(time.time() * 1000),
        "dateString": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "sgv": int(current_bg),
        "direction": "Flat" # Keeping it simple for the simulator
    }
    
    # Add to our history queue (the oldest reading is automatically dropped if full)
    glucose_history.append(new_reading)
    
    # Overwrite the glucose.json file with the complete, updated history
    # The oref1 script needs a simple list, so we convert the deque
    with open(os.path.join(OREF1_DATA_PATH, 'glucose.json'), 'w') as f:
        json.dump(list(glucose_history), f)
        
    print(f"SIMULATOR: New reading generated. BG: {int(current_bg)}. History size: {len(glucose_history)}")


if __name__ == '__main__':
   #  setup_static_files()
    print("--- Starting Data Simulator Loop ---")
    while True:
        generate_new_reading_and_update_file()
        # For testing, you can speed this up (e.g., time.sleep(5) for every 5 seconds)
        time.sleep(READING_INTERVAL_SECONDS)
