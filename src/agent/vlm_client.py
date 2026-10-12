import base64
import requests
import cv2

class VLMAgent:
    def __init__(self, model_name="moondream"):
        # Default local endpoint for Ollama
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = model_name

    def analyze_scene(self, frame, telemetry_data, yolo_objects):
        """
        Sends the current frame and telemetry data to the local VLM.
        """
        # Encode OpenCV frame to base64 string for the API
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')

        # Multi-modal prompt engineering
        prompt = f"""You are DriveSense, an autonomous driving AI agent.
Current Vehicle Telemetry:
- Speed: {telemetry_data.get('speed', 0):.1f} km/h
- Steering: {telemetry_data.get('steering', 0):.2f} degrees
- Brake Pressure: {telemetry_data.get('brake', 0)}%

The Edge CV model detected these objects: {', '.join(yolo_objects) if yolo_objects else 'None'}

An anomaly (hard braking) was just detected. Analyze the provided dashboard camera frame.
Provide a very brief, 1-2 sentence explanation of the hazard and a recommended action.
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [img_str],
            "stream": False
        }

        try:
            # Attempt to reach local Ollama instance
            response = requests.post(self.api_url, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json().get("response", "No response.")
            elif response.status_code == 404:
                return (
                    f"[MODEL NOT DOWNLOADED] Ollama is active, but '{self.model_name}' has not been pulled.\n"
                    f"-> Run 'ollama pull {self.model_name}' in your terminal.\n"
                    f"[SIMULATED REASONING]: Emergency braking at {telemetry_data.get('speed', 0):.1f} km/h. "
                    f"Hazard detected: {', '.join(yolo_objects) if yolo_objects else 'Path obstruction'}. "
                    "Action: Maintain brake pressure."
                )
            else:
                return f"[API Error]: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException:
            # Graceful fallback if Ollama is not installed or running
            return (
                "[OLLAMA OFFLINE] Simulated VLM Response: "
                f"Emergency braking engaged at {telemetry_data.get('speed', 0):.1f} km/h. "
                f"Visual hazard likely related to: {', '.join(yolo_objects) if yolo_objects else 'Unknown'}. "
                "Action: Maintain brake pressure."
            )
