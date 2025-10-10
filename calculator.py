# run_loop.py
import json
import time
import subprocess
import os

# --- Configuration ---
# THIS IS YOUR SAFETY TOGGLE SWITCH!
# False = Open Loop (only shows recommendations)
# True = Closed Loop (would attempt to send commands to a pump)
LOOP_IS_CLOSED = False

OREF1_PATH = 'E:/oref1/oref0-master'
LOOP_INTERVAL_SECONDS = 300 # 5 minutes

# In run_loop.py

def run_oref1_calculation():
    """Runs the main determine-basal script and returns the recommendation."""
    
    # The command should now use SIMPLE, RELATIVE paths
    command = [
        'node',
        'bin/oref0-determine-basal.js',
        'data/iob.json',
        'data/temp_basal.json',
        'data/glucose.json',
        'data/profile.json'
    ]
    
    # Let's print the command for debugging
    print(f"Executing command: {' '.join(command)}")

    try:
        # The magic is here: cwd=OREF1_PATH tells subprocess to 'cd' into
        # that directory before running the command.
        process = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            cwd=OREF1_PATH  # <-- THIS IS THE CRUCIAL FIX
        )
        
        if not process.stdout:
            print("!!! ORCHESTRATOR: Error - oref1 script produced no output. !!!")
            if process.stderr:
                print("--- Error Message from script ---")
                print(process.stderr)
            return None

        recommendation = json.loads(process.stdout)
        return recommendation

    except subprocess.CalledProcessError as e:
        print("!!! ORCHESTRATOR: Error - oref1 script returned a non-zero exit code. !!!")
        print("--- Error Message from script ---")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("!!! ORCHESTRATOR: Error - 'node' command not found or path is wrong. !!!")
        print("Please ensure Node.js is installed and in your system's PATH.")
        return None
    except json.JSONDecodeError:
        print("!!! ORCHESTRATOR: Error parsing JSON output from oref1 script !!!")
        print("Raw output was:", process.stdout)
        return None
    

if __name__ == '__main__':
    print("--- Starting Oref1 Orchestrator Loop ---")
    print(f"SAFETY SWITCH: Loop is {'CLOSED' if LOOP_IS_CLOSED else 'OPEN'}")
    
    while True:
        recommendation = run_oref1_calculation()
        
        if recommendation:
            rate = recommendation.get('rate')
            duration = recommendation.get('duration')
            reason = recommendation.get('reason')
            
            print("\n--- Oref1 Recommendation Received ---")
            print(f"Reason: {reason}")
            print(f"Recommended Temp Basal: {rate} U/hr for {duration} mins")
            
            # This is where your safety toggle works!
            if LOOP_IS_CLOSED:
                print("ACTION: LOOP IS CLOSED. Sending command to pump controller...")
                # In a real system, you would call your pump control function here:
                # pump_controller.set_temp_basal(rate, duration)
            else:
                print("ACTION: LOOP IS OPEN. No action will be taken automatically.")
        
        print(f"\n--- Waiting for {LOOP_INTERVAL_SECONDS // 60} minutes until next cycle ---")
        time.sleep(LOOP_INTERVAL_SECONDS)