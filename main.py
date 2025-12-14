import cv2

from utils import TrafficCounter


VIDEO_PATH = "trafico01.mp4"

LINES_CONFIG = [
    {"cx1": 480, "cy1": 850, "cx2": 580, "cy2": 850},
    {"cx1": 610, "cy1": 850, "cx2": 720, "cy2": 850},
    {"cx1": 990, "cy1": 750, "cx2": 1090, "cy2": 750},
    {"cx1": 1320, "cy1": 900, "cx2": 1470, "cy2": 900},
    {"cx1": 1180, "cy1": 640, "cx2": 1210, "cy2": 640},
    {"cx1": 1420, "cy1": 730, "cx2": 1500, "cy2": 730},
    {"cx1": 1630, "cy1": 770, "cx2": 1770, "cy2": 770},
]


def create_windows():
    """
    Crea ventanas redimensionables para asegurar que se vea todo el frame.
    """
    cv2.namedWindow("Máscara", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Detección de Vehículos", cv2.WINDOW_NORMAL)
    # Ajusta tamaño a tu pantalla si hace falta
    cv2.resizeWindow("Detección de Vehículos", 1280, 720)


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Error: No se pudo abrir el archivo de video.")
        return

    create_windows()
    traffic_counter = TrafficCounter(LINES_CONFIG, max_tracking=14)

    go = True
    while go:
        ret, frame = cap.read()
        if not ret:
            break

        fps = cap.get(cv2.CAP_PROP_FPS)
        mask, annotated = traffic_counter.process_frame(frame, fps)

        # Mostrar SIEMPRE las dos ventanas
        cv2.imshow("Máscara", mask)
        cv2.imshow("Detección de Vehículos", annotated)

        key = cv2.waitKey(27) & 0xFF
        # Pulsar 'c' o Esc para salir
        if key == ord("c") or key == 27:
            go = False

    cap.release()
    cv2.destroyAllWindows()
    traffic_counter.print_results()


if __name__ == "__main__":
    main()
