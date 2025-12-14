import cv2
import math


def line_crossed(centroid_x, centroid_y, line, margin=10):
    """
    Comprueba si un centroide ha cruzado una línea horizontal.
    
    Args:
        centroid_x, centroid_y: coordenadas del centroide del objeto
        line: diccionario con {"cx1", "cy1", "cx2", "cy2"}
        margin: tolerancia vertical en píxeles (default: 10)
    
    Returns:
        bool: True si el centroide cruza la línea
    """
    return (
        line["cx1"] <= centroid_x <= line["cx2"]
        and abs(centroid_y - line["cy1"]) <= margin
    )


def speed_calc(prev_obj, actual_obj, fps):
    """
    Calcula la velocidad de un objeto entre dos posiciones.
    
    Args:
        prev_obj: tupla (x_prev, y_prev, frame_prev)
        actual_obj: tupla (x_actual, y_actual, frame_actual)
        fps: frames por segundo del vídeo
    
    Returns:
        float: velocidad en píxeles/segundo
    """
    x_prev, y_prev, prev_frame = prev_obj
    x_actual, y_actual, actual_frame = actual_obj

    distance = math.hypot(x_actual - x_prev, y_actual - y_prev)
    time = (actual_frame - prev_frame) / fps

    return distance / time if time > 0 else 0.0


class TrafficCounter:
    """
    Lógica de visión:
    - Segmentación de fondo
    - Detección de blobs
    - Tracking por carril
    - Conteo y velocidades
    - Dibujar overlays
    """

    # Colores en BGR
    LINE_COLOR = (255, 255, 0)      # cian para líneas
    TEXT_COLOR = (0, 255, 0)        # verde radioactivo para texto

    def __init__(self, lines_config, max_tracking=14, min_area=500, max_width=420):
        """
        Inicializa el contador de tráfico.
        
        Args:
            lines_config: lista de diccionarios con líneas de conteo
            max_tracking: frames máximo para mantener un track
            min_area: área mínima de contorno (píxeles)
            max_width: ancho máximo de vehículo (píxeles)
        """
        self.lines = lines_config
        self.max_tracking = max_tracking
        self.min_area = min_area
        self.max_width = max_width

        self.counter = [0 for _ in self.lines]
        self.object_ids = [0 for _ in self.lines]
        self.track_obj = [{} for _ in self.lines]

        # velocidades por carril (para estadísticas, no se dibujan)
        self.lane_speeds = [[] for _ in self.lines]

        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=50, detectShadows=False
        )
        self.frames_counter = 0

    def process_frame(self, frame, fps):
        """
        Procesa un frame completo: detecta, trackea, cuenta y dibuja.
        
        Args:
            frame: imagen BGR del frame actual
            fps: frames por segundo del vídeo
        
        Returns:
            tuple: (mask_binarizada, frame_anotado)
        """
        self.frames_counter += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            if w > self.max_width:
                continue

            centroid_x = x + w // 2
            centroid_y = y + h // 2

            for i, line in enumerate(self.lines):
                if line_crossed(centroid_x, centroid_y, line):
                    self._update_track_for_lane(
                        lane_index=i,
                        centroid_x=centroid_x,
                        centroid_y=centroid_y,
                        fps=fps,
                    )

        self._cleanup_expired_tracks()
        annotated = self._draw_lanes_and_counts(frame.copy())
        return mask, annotated

    def _update_track_for_lane(self, lane_index, centroid_x, centroid_y, fps):
        """
        Actualiza/crea track de un vehículo en un carril específico.
        Calcula velocidad si hay track previo.
        """
        lane_tracks = self.track_obj[lane_index]

        matching_id = next(
            (
                obj_id
                for obj_id, (old_x, old_y, last_seen) in lane_tracks.items()
                if abs(centroid_x - old_x) < 50
                and abs(centroid_y - old_y) < 50
            ),
            None,
        )

        if matching_id is not None:
            prev_obj = lane_tracks[matching_id]
            lane_tracks[matching_id] = (
                centroid_x,
                centroid_y,
                self.frames_counter,
            )
            speed = speed_calc(prev_obj, lane_tracks[matching_id], fps)
            if speed > 0:
                self.lane_speeds[lane_index].append(speed)
                print(
                    f"Velocidad de carril {lane_index + 1}: "
                    f"{speed:.2f} píxeles/seg"
                )
        else:
            lane_tracks[self.object_ids[lane_index]] = (
                centroid_x,
                centroid_y,
                self.frames_counter,
            )
            self.counter[lane_index] += 1
            self.object_ids[lane_index] += 1

    def _cleanup_expired_tracks(self):
        """
        Elimina tracks de vehículos que no se han visto en max_tracking frames.
        """
        for i, lane_tracks in enumerate(self.track_obj):
            expired_ids = [
                obj_id
                for obj_id, (_, _, last_seen) in lane_tracks.items()
                if self.frames_counter - last_seen > self.max_tracking
            ]
            for obj_id in expired_ids:
                del lane_tracks[obj_id]

    def _draw_lanes_and_counts(self, frame):
        """
        Dibuja líneas de carriles, contadores y estadísticas globales.
        """
        font = cv2.FONT_HERSHEY_DUPLEX

        # Total de vehículos (texto grande, más a la derecha)
        total_vehiculos = sum(self.counter)
        stats_y = 40
        total_text = f"Total vehiculos: {total_vehiculos}"
        cv2.putText(
            frame,
            total_text,
            (320, stats_y),
            font,
            1.0,
            self.TEXT_COLOR,
            2,
        )

        # Velocidad media global (texto grande, más a la derecha)
        all_speeds = [s for lane in self.lane_speeds for s in lane]
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            avg_text = f"Velocidad media global: {avg_speed:.1f} px/s"
            cv2.putText(
                frame,
                avg_text,
                (320, stats_y + 35),
                font,
                1.0,
                self.TEXT_COLOR,
                2,
            )

        # Por carril: línea + contador
        for i, line in enumerate(self.lines):
            base_y = line["cy1"] - 15
            count_text = f"Carril {i + 1}: {self.counter[i]}"

            cv2.putText(
                frame,
                count_text,
                (line["cx1"], base_y),
                font,
                0.7,
                self.TEXT_COLOR,
                2,
            )

            cv2.line(
                frame,
                (line["cx1"], line["cy1"]),
                (line["cx2"], line["cy2"]),
                self.LINE_COLOR,
                3,
            )

        return frame

    def print_results(self):
        """
        Imprime estadísticas finales por consola:
        - Conteo y velocidad media por carril
        - Total vehículos
        - Velocidad media global
        """
        print("\n========== Conteo de Vehículos por Carril ==========")
        total = 0
        for i, count in enumerate(self.counter):
            total += count
            lane_speeds = self.lane_speeds[i]
            if lane_speeds:
                lane_avg = sum(lane_speeds) / len(lane_speeds)
                print(
                    f"Carril {i + 1}: {count} vehículos, "
                    f"velocidad media: {lane_avg:.1f} px/s"
                )
            else:
                print(f"Carril {i + 1}: {count} vehículos, sin datos de velocidad")

        print(f"TOTAL vehículos: {total}")
        all_speeds = [s for lane in self.lane_speeds for s in lane]
        if all_speeds:
            avg_speed = sum(all_speeds) / len(all_speeds)
            print(f"Velocidad media global: {avg_speed:.1f} px/s")
        print("====================================================")
