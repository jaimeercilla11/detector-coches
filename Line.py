from Car import Car


class Line:
    """Representa una línea de conteo en una carretera"""
    
    def __init__(self, line_id, x1, y1, x2, y2, margin=10):
        self.id = line_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.margin = margin
        
        # Tracking de vehículos en esta línea
        self.vehicle_count = 0
        self. cars = {}  # {car_id: Car}
        self. next_car_id = 0
        self.speeds = []  # Velocidades registradas
    
    def contains_point(self, x, y):
        """Verifica si un punto cruza la línea"""
        return (
            self.x1 <= x <= self.x2
            and abs(y - self.y1) <= self.margin
        )
    
    def find_matching_car(self, x, y, distance_threshold=50):
        """Busca un car existente cerca de (x, y)"""
        for car_id, car in self.cars.items():
            if car.distance_to(x, y) < distance_threshold:
                return car
        return None
    
    def add_car(self, x, y, frame_num):
        """Añade un nuevo vehículo a esta línea"""
        new_car = Car(self.next_car_id, x, y, frame_num)
        self.cars[self.next_car_id] = new_car
        self.next_car_id += 1
        self.vehicle_count += 1
        return new_car
    
    def update_car(self, car, x, y, frame_num, fps):
        """Actualiza la posición de un vehículo"""
        car.update_position(x, y, frame_num)
        speed = car.calculate_speed(fps)
        if speed > 0:
            self.speeds.append(speed)
    
    def cleanup_expired_cars(self, current_frame, max_tracking):
        """Elimina vehículos que no se han visto en mucho tiempo"""
        expired_ids = [
            car_id for car_id, car in self.cars. items()
            if car.is_expired(current_frame, max_tracking)
        ]
        for car_id in expired_ids:
            del self.cars[car_id]
    
    def get_average_speed(self):
        """Obtiene la velocidad media en esta línea"""
        return sum(self.speeds) / len(self.speeds) if self.speeds else 0.0
    
    def get_stats(self):
        """Retorna estadísticas de la línea"""
        return {
            "line_id": self.id,
            "count": self. vehicle_count,
            "average_speed": self.get_average_speed(),
            "total_speeds_recorded": len(self. speeds)
        }