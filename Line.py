from Car import Car


class Line:
    """Represents a counting line with its vehicles, counter and statistics."""
    
    def __init__(self, cx1, cy1, cx2, cy2, line_id, max_tracking=14):
        """
        Initialize a Line instance.
        
        Args:
            cx1: X coordinate of line start
            cy1: Y coordinate of line start
            cx2: X coordinate of line end
            cy2: Y coordinate of line end
            line_id: Unique identifier for the line
            max_tracking: Maximum frames to track a car without update
        """
        self.cx1 = cx1
        self.cy1 = cy1
        self.cx2 = cx2
        self.cy2 = cy2
        self.id = line_id
        self.max_tracking = max_tracking
        
        # Use dictionary instead of parallel lists (SOLID feedback)
        self.cars = {}  # Dictionary of Car objects keyed by car_id
        self.next_car_id = 0
        self.counter = 0
        self.speeds = []
    
    def is_crossed(self, centroid_x, centroid_y, margin=10):
        """
        Check if a centroid has crossed this line.
        
        Args:
            centroid_x: X coordinate of centroid
            centroid_y: Y coordinate of centroid
            margin: Vertical tolerance in pixels
            
        Returns:
            True if the centroid is on the line within margin
        """
        return (
            self.cx1 <= centroid_x <= self.cx2
            and abs(centroid_y - self.cy1) <= margin
        )
    
    def update_or_create_car(self, centroid_x, centroid_y, frame_number, fps):
        """
        Update existing car or create new one.
        
        Args:
            centroid_x: X coordinate of detected centroid
            centroid_y: Y coordinate of detected centroid
            frame_number: Current frame number
            fps: Frames per second of the video
            
        Returns:
            Tuple of (car_id, speed, is_new_car)
        """
        # Try to find matching car
        matching_car = None
        for car in self.cars.values():
            if car.is_near(centroid_x, centroid_y):
                matching_car = car
                break
        
        if matching_car:
            # Update existing car
            speed = matching_car.calculate_speed(
                centroid_x, centroid_y, frame_number, fps
            )
            matching_car.update_position(centroid_x, centroid_y, frame_number)
            
            if speed > 0:
                self.speeds.append(speed)
            
            return matching_car.id, speed, False
        else:
            # Create new car
            car_id = self.next_car_id
            self.next_car_id += 1
            
            new_car = Car(car_id, centroid_x, centroid_y, frame_number)
            self.cars[car_id] = new_car
            self.counter += 1
            
            return car_id, 0.0, True
    
    def cleanup_expired_cars(self, current_frame):
        """
        Remove cars that haven't been updated recently.
        
        Args:
            current_frame: Current frame number
        """
        expired_ids = [
            car_id
            for car_id, car in self.cars.items()
            if current_frame - car.frame_number > self.max_tracking
        ]
        for car_id in expired_ids:
            del self.cars[car_id]
    
    def get_average_speed(self):
        """Get average speed for all vehicles on this line."""
        if self.speeds:
            return sum(self.speeds) / len(self.speeds)
        return 0.0
    
    def get_stats(self):
        """
        Get statistics for this line.
        
        Returns:
            Dictionary with count and average speed
        """
        return {
            "count": self.counter,
            "avg_speed": self.get_average_speed(),
            "total_speeds": len(self.speeds)
        }
