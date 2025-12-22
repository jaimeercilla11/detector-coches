from Line import Line
from VehicleDetector import VehicleDetector
from TrafficVisualizer import TrafficVisualizer


class TrafficCounter:
    """
    Orchestrator class that coordinates vehicle detection, tracking and visualization.
    Follows Single Responsibility Principle by delegating to specialized classes.
    """
    
    def __init__(self, lines_config, max_tracking=14, min_area=500, max_width=420):
        """
        Initialize the TrafficCounter orchestrator.
        
        Args:
            lines_config: List of dictionaries with line coordinates
            max_tracking: Maximum frames to track a car without update
            min_area: Minimum contour area to consider as vehicle
            max_width: Maximum width to consider as vehicle
        """
        # Create Line objects from configuration
        self.lines = [
            Line(
                config["cx1"], 
                config["cy1"], 
                config["cx2"], 
                config["cy2"],
                line_id=i,
                max_tracking=max_tracking
            )
            for i, config in enumerate(lines_config)
        ]
        
        # Initialize detector and visualizer
        self.detector = VehicleDetector(min_area=min_area, max_width=max_width)
        self.visualizer = TrafficVisualizer()
        
        self.frames_counter = 0
    
    def process_frame(self, frame, fps):
        """
        Process a single frame: detect vehicles, update tracking, and visualize.
        
        Args:
            frame: Input frame (BGR image)
            fps: Frames per second of the video
            
        Returns:
            Tuple of (mask, annotated_frame)
        """
        self.frames_counter += 1
        
        # Detect vehicles
        mask, centroids = self.detector.detect_vehicles(frame)
        
        # Process each detected centroid
        for centroid_x, centroid_y in centroids:
            # Check which lines are crossed
            for line in self.lines:
                if line.is_crossed(centroid_x, centroid_y):
                    # Update or create car tracking
                    car_id, speed, is_new = line.update_or_create_car(
                        centroid_x, centroid_y, self.frames_counter, fps
                    )
                    
                    # Print speed for tracking (original behavior)
                    if speed > 0:
                        print(
                            f"Velocidad de carril {line.id + 1}: "
                            f"{speed:.2f} píxeles/seg"
                        )
        
        # Cleanup expired tracks
        for line in self.lines:
            line.cleanup_expired_cars(self.frames_counter)
        
        # Visualize results
        annotated = self.visualizer.draw_all(frame, self.lines)
        
        return mask, annotated
    
    def print_results(self):
        """Print final statistics for all lines."""
        print("\n========== Conteo de Vehículos por Carril ==========")
        total = 0
        all_speeds = []
        
        for line in self.lines:
            stats = line.get_stats()
            total += stats["count"]
            
            if stats["total_speeds"] > 0:
                print(
                    f"Carril {line.id + 1}: {stats['count']} vehículos, "
                    f"velocidad media: {stats['avg_speed']:.1f} px/s"
                )
            else:
                print(f"Carril {line.id + 1}: {stats['count']} vehículos, sin datos de velocidad")
            
            all_speeds.extend(line.speeds)
        
        print(f"TOTAL vehículos: {total}")
        
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            print(f"Velocidad media global: {avg_speed:.1f} px/s")
        
        print("====================================================")
