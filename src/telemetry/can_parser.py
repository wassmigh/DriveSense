import pandas as pd
import time

class TelemetryParser:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        # In a real scenario, this reads from python-can or a raw CAN dump
        # For now, we simulate by reading a CSV or creating dummy data
        self.data = pd.DataFrame()
        self.current_idx = 0
        
    def load_data(self):
        try:
            self.data = pd.read_csv(self.csv_path)
        except Exception as e:
            # Create dummy data if file doesn't exist yet
            self.data = pd.DataFrame({
                'timestamp': range(100),
                'speed': [60 + (i%10) for i in range(100)],
                'steering': [0.0 for _ in range(100)],
                'brake': [0 if i < 50 else 80 for i in range(100)]
            })

    def get_next_reading(self):
        if self.current_idx >= len(self.data):
            self.current_idx = 0 # loop for simulation
        
        row = self.data.iloc[self.current_idx]
        self.current_idx += 1
        return row.to_dict()
