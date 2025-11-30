import asyncio
import time
from datetime import datetime
import state
from motor_control import motor_pulse

INTERVAL_SECONDS = 10 
MAX_ALLOWED_IOB = 0.40  

def _get_smooth_trend_per_minute():
    history = list(state.glucose_history)
    if len(history) < 6: return 0.0 
    latest = history[-1]['bg']
    past = history[-6]['bg'] 
    per_minute = (latest - past) * 2 
    return max(-2.0, min(2.0, per_minute))

async def run_fake_oref1():
    print("OpenAPS (oref1) Started.")
    smoothed_trend = 0.0
    
    while True:
        # --- 🛑 PAUSE CHECK 🛑 ---
        # If paused, stop making decisions.
        if not state.system_running:
            await asyncio.sleep(1)
            continue

        now = time.time()
        current_bg = state.last_bg
        
        # 1. Trend Smoothing
        raw_trend = _get_smooth_trend_per_minute()
        smoothed_trend = (smoothed_trend * 0.7) + (raw_trend * 0.3)
        
        # 2. Prediction
        future_rise = smoothed_trend * 20
        insulin_impact = state.current_iob * state.ISF
        eventual_bg = int(current_bg + future_rise - insulin_impact)
        eventual_bg = max(60, eventual_bg)
        
        # 3. Decision Logic
        time_since_delivery = now - state.last_delivery_time
        reason = ""
        suggested_action = "None"
        rate = state.BASE_BASAL
        
        if time_since_delivery < 60:
            reason = "Waiting for absorption."
            suggested_action = "WAIT"
        elif state.motor_state == "ON":
            reason = "Motor Moving."
            suggested_action = "WAIT"
        elif state.current_iob >= MAX_ALLOWED_IOB:
            reason = f"Max IOB ({state.current_iob:.2f}). Safety Hold."
            suggested_action = "WAIT"
        else:
            if eventual_bg > state.TARGET_MAX_BG:
                rate = 2.0
                reason = f"Pred {eventual_bg} > {state.TARGET_MAX_BG}. Need IOB."
                suggested_action = "DELIVER"
            elif eventual_bg < state.TARGET_MIN_BG:
                rate = 0.0
                reason = f"Pred {eventual_bg} < {state.TARGET_MIN_BG}. Suspending."
                suggested_action = "SUSPEND"
            else:
                rate = state.BASE_BASAL
                reason = f"Pred {eventual_bg} is safe."
                suggested_action = "NONE"

        # 4. Execute
        if suggested_action == "DELIVER":
            print(f"💉 [ACTION TRIGGERED] {reason}")
            asyncio.create_task(motor_pulse())
        
        rec = {
            "ts": int(now * 1000),
            "rate": rate,
            "duration": 30,
            "eventualBG": eventual_bg,
            "reason": reason
        }
        state.basal_history.append(rec)
        state.suggested_rate = rate

        local_time = datetime.fromtimestamp(now).strftime("%H:%M:%S")
        print(
            f"[OREF1] {local_time} | "
            f"BG:{int(current_bg)} | "
            f"Trend:{smoothed_trend:+.2f} | "
            f"IOB:{state.current_iob:.2f}U | "
            f"Pred:{eventual_bg} -> "
            f"[{suggested_action}]"
        )

        await asyncio.sleep(INTERVAL_SECONDS)