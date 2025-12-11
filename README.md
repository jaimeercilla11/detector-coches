# Sistema de Detección y Conteo de Vehículos
Sistema de visión por computador para detección, conteo y cálculo de velocidad de vehículos en vídeos de tráfico, utilizando técnicas de procesamiento de imágenes con OpenCV.

## Características

- Detección automática de vehículos mediante sustracción de fondo
- Conteo por carril con líneas de detección configurables
- Cálculo de velocidad en tiempo real (px/s)
- Tracking de vehículos con identificación única
- Estadísticas detalladas por carril y globales
- Visualización en tiempo real con rectángulos y contadores

---

## Estructura del Proyecto
proyecto/
├── main.py
├── utils.py  
├── trafico01.mp4
└── README.md                     

### Archivos principales:

- **main.py**: Script principal que carga vídeo y procesa frames​

- **utils.py**: Clase TrafficCounter y funciones auxiliares​

---

### Instalación y Ejecución

`pip install opencv-python
python main.py`

---

### Controles:
- Presiona "c" o Esc para detener

- Ventanas: Máscara + Detección de Vehículos

--- 

#### Descripción de Funciones y Clases

- Clase `TrafficCounter`: Gestiona detección, tracking, conteo y velocidades por carril.​

- Función `line_crossed()`: Detecta si un centroide cruza línea de carril.​

- Función `speed_calc()`: Calcula velocidad entre posiciones previas/actuales.​

Parámetros clave:
- **LINES_CONFIG**: Líneas de detección por carril​

- **min_area=500, max_width=420**: Filtros de contornos​

- **max_tracking=14**: Timeout para tracks
---

### Flujo del Sistema
1. Carga vídeo y crea sustractor de fondo MOG2​

2. Por frame: grises → máscara → morfología → contornos​

3. Filtra contornos válidos y calcula centroides​

4. Asocia detecciones con tracks existentes o crea nuevos​

5. Actualiza contadores y velocidades al cruzar líneas​

6. Dibuja overlays y estadísticas en tiempo real
---

### Resultados

El resultado que os tiene que aparecer por pantalla al ejecutar todo el script es asi:
![Detector de coches](https://github.com/user-attachments/assets/48680dec-9c8e-4b2b-99e0-ef5a5e8ad5a6)

---

## Autores
- Jaime Ercilla Martin
- Javier Bolívar García-Izquierdo



