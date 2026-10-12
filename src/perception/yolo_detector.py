import cv2
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path="yolo11n.pt"):
        # We use the nano (n) version for the fastest edge inference
        self.model = YOLO(model_path)
        
    def process_frame(self, frame):
        """
        Runs YOLOv11 on the given frame.
        Returns a list of detected objects with confidence strings.
        """
        if frame is None:
            return []
            
        # Run inference (verbose=False to avoid cluttering our terminal UI)
        results = self.model(frame, verbose=False)[0]
        
        detected_stats = []
        for box in results.boxes:
            # Extract class name and confidence
            cls_name = self.model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            if conf > 0.4:  # Only show confident detections
                detected_stats.append(f"{cls_name} ({conf:.2f})")
                
        # Return unique detections (e.g., if there are 5 cars, just show "car (0.90)", etc.)
        # We cap it at the top 5 to keep the terminal UI clean
        return list(set(detected_stats))[:5]
