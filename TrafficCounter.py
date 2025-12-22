# TrafficCounter.py - REFACTORIZADO
import cv2
from Line import Line
from VehicleDetector import VehicleDetector
from TrafficVisualizer import TrafficVisualizer


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
        mask, detections = self. detector.detect(frame)
        
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