
import math

class Car:
    """Representa un vehículo en el frame"""
    
    def __init__(self, car_id, x, y, frame_num):
        self.id = car_id
        self. position_history = [(x, y, frame_num)]  # (x, y, frame)
        self.last_seen = frame_num
        self.vehicle_type = None  # Puede ser:  "car", "motorcycle", "truck", etc.
    
    @property
    def current_position(self):
        """Retorna la posición actual (x, y)"""
        return self.position_history[-1][: 2]
    
    @property
    def current_frame(self):
        """Retorna el frame actual"""
        return self.position_history[-1][2]
    
    def update_position(self, x, y, frame_num):
        """Actualiza la posición del vehículo"""
        self. position_history.append((x, y, frame_num))
        self.last_seen = frame_num
    
    def calculate_speed(self, fps):
        """Calcula la velocidad del vehículo en píxeles/segundo"""
        if len(self.position_history) < 2:
            return 0. 
        
        x_prev, y_prev, frame_prev = self.position_history[-2]
        x_curr, y_curr, frame_curr = self.position_history[-1]
        
        distance = math.hypot(x_curr - x_prev, y_curr - y_prev)
        time_elapsed = (frame_curr - frame_prev) / fps
        
        return distance / time_elapsed if time_elapsed > 0 else 0.0
    
    def is_expired(self, current_frame, max_tracking):
        """Verifica si el vehículo debe ser descartado"""
        return current_frame - self.last_seen > max_tracking
    
    def distance_to(self, x, y):
        """Calcula la distancia a un punto (x, y)"""
        curr_x, curr_y = self.current_position
        return math.hypot(x - curr_x, y - curr_y)