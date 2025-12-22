import math


class Car:
    """Represents an individual vehicle with its position, history and methods to calculate speed and distance."""
    
    def __init__(self, car_id, x, y, frame_number):
        """
        Initialize a Car instance.
        
        Args:
            car_id: Unique identifier for the car
            x: X coordinate of the centroid
            y: Y coordinate of the centroid
            frame_number: Frame number when the car was first detected
        """
        self.id = car_id
        self.x = x
        self.y = y
        self.frame_number = frame_number
        self.speeds = []
    
    def update_position(self, x, y, frame_number):
        """Update the car's position to a new frame."""
        self.x = x
        self.y = y
        self.frame_number = frame_number
    
    def calculate_speed(self, new_x, new_y, new_frame, fps):
        """
        Calculate speed between current position and new position.
        
        Args:
            new_x: New X coordinate
            new_y: New Y coordinate
            new_frame: New frame number
            fps: Frames per second of the video
            
        Returns:
            Speed in pixels per second
        """
        distance = math.hypot(new_x - self.x, new_y - self.y)
        time = (new_frame - self.frame_number) / fps
        
        speed = distance / time if time > 0 else 0.0
        if speed > 0:
            self.speeds.append(speed)
        return speed
    
    def get_average_speed(self):
        """Get average speed for this car."""
        if self.speeds:
            return sum(self.speeds) / len(self.speeds)
        return 0.0
    
    def is_near(self, x, y, threshold=50):
        """
        Check if a position is near this car's current position.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            threshold: Maximum distance to consider "near"
            
        Returns:
            True if the position is within threshold distance
        """
        return abs(x - self.x) < threshold and abs(y - self.y) < threshold
