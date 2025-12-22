import cv2

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
        for line in lines. values():
            cv2.line(
                frame,
                (line.x1, line.y1),
                (line.x2, line. y2),
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