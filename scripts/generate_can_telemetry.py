"""
DriveSense Telemetry Generator
Generates realistic automotive CAN bus telemetry synchronized with sample_dashcam.mp4 (587 frames @ 30 FPS ~ 19.57s).
Signals follow SAE J1939 / OBD-II automotive standards.
"""
import math
import os
import pandas as pd

def generate_telemetry(total_frames=587, fps=30.0, output_path="data/sample_can_bus.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    dt_ms = 1000.0 / fps  # ~33.33 ms per frame

    records = []
    
    speed = 72.0
    rpm = 2150
    steering = 0.2
    
    for i in range(total_frames):
        t_ms = round(i * dt_ms, 2)
        
        # Phase 1: Cruising (0.0s to 12.5s -> frames 0 to 375)
        if i <= 375:
            can_id = "0x180"  # Powertrain / Vehicle Speed
            throttle = 34.0 + 2.0 * math.sin(i / 15.0)
            brake = 0.0
            speed = 72.0 + 0.5 * math.sin(i / 12.0)
            rpm = int(speed * 30.5 + 5.0 * math.sin(i / 8.0))
            steering = round(0.4 * math.sin(i / 20.0) + 0.1 * math.cos(i / 5.0), 2)
            
        # Phase 2: Pedestrian Spotted / Rapid AEB Brake Ramp-up (12.5s to 13.0s -> frames 376 to 390)
        elif 376 <= i <= 390:
            can_id = "0x204"  # Brake ECU / Autonomous Emergency Braking (AEB)
            progress = (i - 376) / 14.0
            throttle = max(0.0, 34.0 * (1.0 - progress))
            brake = round(20.0 + progress * 68.0, 1)  # Sharp rise to ~88% brake pressure
            speed = max(64.0, speed - 0.55)
            rpm = int(speed * 28.0)
            steering = round(0.3 + 2.5 * progress, 2)  # Initial steering response
            
        # Phase 3: Full Emergency Braking while Pedestrian in Scene (13.0s to 15.5s -> frames 391 to 465)
        elif 391 <= i <= 465:
            can_id = "0x204"  # Full ABS/AEB Emergency Braking
            throttle = 0.0
            # Sustained high brake pressure (82% to 94%)
            brake_intensity = 88.0 + 5.0 * math.sin((i - 391) / 12.0)
            brake = round(min(95.0, max(80.0, brake_intensity)), 1)
            # Deceleration down to 18 km/h safe crawl
            speed = max(18.0, speed - 0.65)
            rpm = max(1000, int(speed * 25.0))
            # Evasive steering deflection then stabilization
            steering = round(3.8 * math.sin((i - 391) / 16.0), 2)
            
        # Phase 4: Path Clear / Recovery & Safe Acceleration (15.5s to 19.57s -> frames 466 to 586)
        else:
            can_id = "0x180"  # Powertrain resume
            progress = (i - 466) / (total_frames - 466)
            brake = 0.0
            throttle = min(28.0, 10.0 + progress * 18.0)
            speed = min(48.0, speed + 0.22)
            rpm = int(speed * 32.0 + 8.0 * math.sin(i / 10.0))
            steering = round(0.2 * math.sin(i / 15.0), 2)
            
        records.append({
            "timestamp_ms": t_ms,
            "frame_idx": i,
            "can_id": can_id,
            "speed": round(speed, 1),
            "steering": steering,
            "brake": brake,
            "rpm": rpm,
            "throttle": round(throttle, 1)
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} synchronized CAN frames to {output_path}")

if __name__ == "__main__":
    generate_telemetry()
