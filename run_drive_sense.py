import time
import cv2
import threading
from rich.live import Live
from src.telemetry.can_parser import TelemetryParser
from src.ui.terminal_render import TerminalUI
from src.perception.yolo_detector import YOLODetector
from src.agent.vlm_client import VLMAgent

def main():
    parser = TelemetryParser("data/sample_can_bus.csv")
    parser.load_data()
    ui = TerminalUI()
    
    print("Initializing YOLOv11 Edge Model...")
    detector = YOLODetector("yolo11n.pt")
    
    print("Initializing VLM Agent Engine...")
    vlm_agent = VLMAgent()
    
    video_path = "data/sample_dashcam.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Warning: Could not open {video_path}. Falling back to webcam...")
        cap = cv2.VideoCapture(0)
    
    print("Initializing DriveSense Edge Node...")
    time.sleep(1)
    
    # We use a state dictionary so the background VLM thread can update the UI safely
    agent_state = {"log": "[OK] Scene normal. Monitoring active.", "is_reasoning": False}
    
    def trigger_vlm(frame, telemetry, vision_stats):
        """ This runs in a separate thread so it doesn't block the fast Perception loop! """
        agent_state["is_reasoning"] = True
        has_ped = any("person" in obj.lower() for obj in vision_stats)
        
        if has_ped:
            agent_state["log"] = "[ALERT] 🚨 PEDESTRIAN IN PATH! AEB Braking Engaged. VLM evaluating hazard..."
        else:
            agent_state["log"] = "[ALERT] 🚨 Heavy Braking Anomaly! VLM analyzing video frame..."
        
        # Heavy, non-blocking call to local Moondream VLM
        reasoning = vlm_agent.analyze_scene(frame, telemetry, vision_stats)
        
        agent_state["log"] = (
            f"[ALERT] 🚨 Critical Incident Assessed!\n"
            f"[VLM REASONING]: {reasoning.strip()}\n"
            f"[RECOMMENDED ACTION]: {'Maintain emergency brake pressure until pedestrian clears path.' if has_ped else 'Hold brake pressure and verify safe following distance.'}"
        )
        
        # Keep reasoning visible for 5 seconds before returning to standby
        time.sleep(5)
        agent_state["is_reasoning"] = False
        agent_state["log"] = "[OK] Scene normal. VLM in standby. Monitoring telemetry."
        
    with Live(ui.layout, refresh_per_second=10, screen=True) as live:
        for _ in range(1000): 
            telemetry = parser.get_next_reading()
            
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret: break

            vision_stats = detector.process_frame(frame)
            if not vision_stats:
                vision_stats = ["No objects detected"]
            
            has_pedestrian = any("person" in obj.lower() for obj in vision_stats)
            is_hard_braking = telemetry.get('brake', 0) > 50

            # Autonomous Emergency Braking (AEB) & Anomaly Trigger
            if (has_pedestrian or is_hard_braking) and not agent_state["is_reasoning"]:
                # If pedestrian detected, ensure braking is activated in telemetry view
                if has_pedestrian and telemetry.get('brake', 0) < 50:
                    telemetry['brake'] = 85.0
                    telemetry['can_id'] = '0x204 (AEB)'

                # Trigger VLM reasoning asynchronously in the background
                threading.Thread(
                    target=trigger_vlm, 
                    args=(frame.copy(), telemetry, vision_stats),
                    daemon=True
                ).start()
                
            live.update(ui.update(telemetry, vision_stats, agent_state["log"]))
            time.sleep(0.08) # ~12 FPS real-time playback

    cap.release()

if __name__ == "__main__":
    main()
