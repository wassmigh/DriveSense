# DriveSense

DriveSense is a terminal-based Multimodal AI Agent for Predictive Automotive Diagnostics and Scene Understanding. 
It acts as a simulated intelligent edge device that fuses synchronized video streams and CAN bus telemetry data.

## Architecture
- **Perception:** YOLOv11 for real-time object detection.
- **Telemetry:** Virtual CAN bus parsing for vehicle state (speed, brake, steering).
- **Reasoning (VLM):** Local Vision-Language Model triggered by telemetry anomalies to explain driving scenes.
- **UI:** Terminal-based rich interface.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

## Run
Run the simulation dashboard:
`python run_drive_sense.py`
