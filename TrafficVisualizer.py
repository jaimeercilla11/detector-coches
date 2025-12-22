import cv2


class TrafficVisualizer:
    """Handles all visualization logic for traffic detection."""
    
    LINE_COLOR = (255, 255, 0)  # Cyan
    TEXT_COLOR = (0, 255, 0)    # Green
    
    def __init__(self):
        """Initialize the TrafficVisualizer."""
        self.font = cv2.FONT_HERSHEY_DUPLEX
    
    def draw_statistics(self, frame, lines):
        """
        Draw global statistics on the frame.
        
        Args:
            frame: Frame to draw on (will be modified in place)
            lines: List of Line objects
        """
        # Calculate total vehicles and average speed
        total_vehicles = sum(line.counter for line in lines)
        all_speeds = [speed for line in lines for speed in line.speeds]
        
        # Draw total vehicles
        stats_y = 40
        total_text = f"Total vehiculos: {total_vehicles}"
        cv2.putText(
            frame,
            total_text,
            (320, stats_y),
            self.font,
            1.0,
            self.TEXT_COLOR,
            2,
        )
        
        # Draw average speed if available
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            avg_text = f"Velocidad media global: {avg_speed:.1f} px/s"
            cv2.putText(
                frame,
                avg_text,
                (320, stats_y + 35),
                self.font,
                1.0,
                self.TEXT_COLOR,
                2,
            )
    
    def draw_line(self, frame, line):
        """
        Draw a counting line and its statistics on the frame.
        
        Args:
            frame: Frame to draw on (will be modified in place)
            line: Line object to draw
        """
        # Draw count text above the line
        base_y = line.cy1 - 15
        count_text = f"Carril {line.id + 1}: {line.counter}"
        
        cv2.putText(
            frame,
            count_text,
            (line.cx1, base_y),
            self.font,
            0.7,
            self.TEXT_COLOR,
            2,
        )
        
        # Draw the line itself
        cv2.line(
            frame,
            (line.cx1, line.cy1),
            (line.cx2, line.cy2),
            self.LINE_COLOR,
            3,
        )
    
    def draw_all(self, frame, lines):
        """
        Draw all lines and statistics on the frame.
        
        Args:
            frame: Frame to draw on
            lines: List of Line objects
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw global statistics
        self.draw_statistics(annotated, lines)
        
        # Draw each line
        for line in lines:
            self.draw_line(annotated, line)
        
        return annotated
