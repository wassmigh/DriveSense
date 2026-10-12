from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

class TerminalUI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="upper", ratio=1),
            Layout(name="lower", ratio=1)
        )
        self.layout["upper"].split_row(
            Layout(name="telemetry", ratio=1),
            Layout(name="vision", ratio=2)
        )
        
    def update(self, telemetry_data, vision_stats, agent_log):
        # Create Telemetry Table
        t_table = Table(title="Live Telemetry (CAN Bus)")
        t_table.add_column("Signal", style="cyan")
        t_table.add_column("Value", style="magenta")
        can_id = telemetry_data.get('can_id', '0x180')
        t_table.add_row("CAN Msg ID", str(can_id), style="bold yellow" if can_id == "0x204" else "cyan")
        t_table.add_row("Speed", f"{telemetry_data.get('speed', 0):.1f} km/h")
        t_table.add_row("Engine RPM", f"{int(telemetry_data.get('rpm', 0))} RPM")
        t_table.add_row("Throttle", f"{telemetry_data.get('throttle', 0):.1f}%")
        t_table.add_row("Steering", f"{telemetry_data.get('steering', 0):.2f}°")
        
        brake = telemetry_data.get('brake', 0)
        t_table.add_row("Brake", f"{brake}%", style="bold red" if brake > 50 else "green")
        
        # Create Vision Stats
        v_table = Table(title="Vision (YOLOv11 Edge)")
        v_table.add_column("Detected Objects", style="green")
        for obj in vision_stats:
            v_table.add_row(obj)
            
        self.layout["upper"]["telemetry"].update(Panel(t_table, title="[bold blue]Telemetry Node"))
        self.layout["upper"]["vision"].update(Panel(v_table, title="[bold green]Perception Node"))
        
        alert_style = "bold red" if "[ALERT]" in agent_log else "bold yellow"
        self.layout["lower"].update(Panel(agent_log, title="[bold magenta]VLM Reasoning Agent", style=alert_style))
        
        return self.layout
