import math
import cv2
import time


class Car: 
    """Representa un vehículo en el frame"""
    
    def __init__(self, car_id, x, y, frame_num):
        self.id = car_id
        self.position_history = [(x, y, frame_num)]  # (x, y, frame)
        self.last_seen = frame_num
    
    def get_current_position(self):
        """Retorna la posición actual (x, y)"""
        return self.position_history[-1][:2]
    
    def get_current_frame(self):
        """Retorna el frame actual"""
        return self.position_history[-1][2]
    
    def update_position(self, x, y, frame_num):
        """Actualiza la posición del vehículo"""
        self.position_history.append((x, y, frame_num))
        self.last_seen = frame_num
    
    def calculate_speed(self, fps):
        """Calcula la velocidad del vehículo en píxeles/segundo"""
        if len(self.position_history) < 2:
            return 0.0
        
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
        curr_x, curr_y = self.get_current_position()
        return math.hypot(x - curr_x, y - curr_y)



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
        self.cars = {}  # {car_id: Car}
        self.next_car_id = 0
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
            car_id for car_id, car in self.cars.items()
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
            "count": self.vehicle_count,
            "average_speed": self.get_average_speed(),
            "total_speeds_recorded": len(self.speeds)
        }
    

class VehicleDetector: 
    """Solo se encarga de detectar vehículos en el frame"""
    
    def __init__(self, min_area=500, max_width=420):
        self.min_area = min_area
        self.max_width = max_width
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=50, detectShadows=False
        )
    
    def detect(self, frame):
        """Retorna mask y lista de centroides detectados"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        
        
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            if w > self.max_width:
                continue
            
            centroid_x = x + w // 2
            centroid_y = y + h // 2
            detections.append((centroid_x, centroid_y))
        
        return mask, detections



class TrafficCounter:
    """Orquesta el conteo de tráfico - Solo coordina"""
    
    def __init__(self, lines_config, max_tracking=14, min_area=500, max_width=420):
        self.lines = {}
        for i, config in enumerate(lines_config):
            line = Line(
                line_id=i,
                x1=config["cx1"],
                y1=config["cy1"],
                x2=config["cx2"],
                y2=config["cy2"]
            )
            self.lines[i] = line
        
        self.detector = VehicleDetector(min_area, max_width)
        self.visualizer = TrafficVisualizer()
        self.max_tracking = max_tracking
        self.frames_counter = 0
    
    def process_frame(self, frame, fps):
        """Orquesta:  detecta → trackea → visualiza"""
        self.frames_counter += 1
        
        # 1. Detectar
        mask, detections = self.detector.detect(frame)
        
        # 2. Trackear
        self._update_tracks(detections, fps)
        self._cleanup_expired_tracks()
        
        # 3. Visualizar
        annotated = self.visualizer.draw(frame. copy(), self.lines)
        
        return mask, annotated
    
    def _update_tracks(self, detections, fps):
        """Actualiza tracking para cada detección"""
        for centroid_x, centroid_y in detections:
            for line in self.lines.values():
                if line.contains_point(centroid_x, centroid_y):
                    car = line.find_matching_car(centroid_x, centroid_y)
                    
                    if car is not None:
                        line. update_car(car, centroid_x, centroid_y, self.frames_counter, fps)
                    else:
                        line.add_car(centroid_x, centroid_y, self.frames_counter)
    
    def _cleanup_expired_tracks(self):
        """Limpia vehículos expirados"""
        for line in self.lines.values():
            line.cleanup_expired_cars(self.frames_counter, self.max_tracking)
    
    def print_results(self):
        """Imprime resultados finales"""
        print("\n========== Conteo de Vehículos por Carril ==========")
        total = 0
        
        for line in self.lines. values():
            stats = line.get_stats()
            total += stats["count"]
            
            print(
                f"Carril {stats['line_id'] + 1}: {stats['count']} vehículos, "
                f"velocidad media: {stats['average_speed']:.1f} px/s"
            )
        
        print(f"TOTAL vehículos: {total}")
        
        all_speeds = [s for line in self.lines.values() for s in line.speeds]
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            print(f"Velocidad media global: {avg_speed:.1f} px/s")
        
        print("====================================================")



class TrafficVisualizer: 
    """Solo se encarga de visualizar los datos"""
    
    LINE_COLOR = (255, 255, 0)
    TEXT_COLOR = (0, 255, 0)
    
    @staticmethod
    def draw(frame, lines):
        """Dibuja líneas y estadísticas"""
        font = cv2.FONT_HERSHEY_DUPLEX
        
        # Estadísticas globales
        total_vehicles = sum(line.vehicle_count for line in lines. values())
        all_speeds = [s for line in lines.values() for s in line.speeds]
        
        cv2.putText(
            frame,
            f"Total vehiculos: {total_vehicles}",
            (320, 40),
            font,
            1.0,
            TrafficVisualizer.TEXT_COLOR,
            2,
        )
        
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            cv2.putText(
                frame,
                f"Velocidad media global: {avg_speed:.1f} px/s",
                (320, 75),
                font,
                1.0,
                TrafficVisualizer.TEXT_COLOR,
                2,
            )
        
        # Dibujar líneas
        for line in lines.values():
            cv2.line(
                frame,
                (line.x1, line.y1),
                (line.x2, line.y2),
                TrafficVisualizer.LINE_COLOR,
                3,
            )
            
            cv2.putText(
                frame,
                f"Carril {line.id + 1}: {line.vehicle_count}",
                (line.x1, line.y1 - 15),
                font,
                0.7,
                TrafficVisualizer.TEXT_COLOR,
                2,
            )
        
        return frame