# Sistema de Detección y Conteo de Vehículos
Sistema de visión por computador para detección, conteo y cálculo de velocidad de vehículos en vídeos de tráfico, utilizando técnicas de procesamiento de imágenes con OpenCV.

## Características

- Detección automática de vehículos mediante sustracción de fondo
- Conteo por carril con líneas de detección configurables
- Cálculo de velocidad en tiempo real (km/h)
- Tracking de vehículos con identificación única
- Estadísticas detalladas por carril y globales
- Visualización en tiempo real con rectángulos y contadores

---

## Estructura del Proyecto
proyecto/

│

├── prueba_detector_coches.ipynb     

├── trafico01.mp4                    

└── README.md                         

### Ejecutar las celdas en orden:

- Celda 1: Importar librerías
- Celda 2: Definir clase Vehiculo
- Celda 3: Funciones auxiliares
- Celda 4: Configuración de líneas y parámetros
- Celda 5: Inicialización y carga de vídeo
- Celda 6: Procesamiento principal
- Celda 7: Mostrar resultados

---

### Controles durante la ejecución:

- Presionar "q" para detener el procesamiento
- El vídeo se mostrará en una ventana de OpenCV

---

### Descripción de Funciones y Clases
**Clase Vehiculo**: Representa un vehículo detectado y rastreado en el vídeo. Guarda la historia reciente de posiciones (coordenadas x, y y el índice de frame) usando un deque para mantener un número limitado de posiciones recientes. Calcula la velocidad suavizada en km/h basada en la distancia recorrida en los últimos frames y la tasa de cuadros por segundo (fps) del vídeo. Proporciona métodos para actualizar la posición, obtener la velocidad actual, la posición más reciente, y el último frame registrado.

**Función encontrar_vehiculo(cx, cy, vehiculos, frame_idx, max_dist=50, max_frames=30)**: Busca entre los vehículos actualmente activos el que esté más cerca del punto (cx, cy) en pantalla, considerando solo aquellos que han sido actualizados dentro de un número máximo de frames (max_frames) y que estén dentro de una distancia máxima (max_dist). Esto permite asociar detecciones nuevas con vehículos ya rastreados para mantener el seguimiento.

**Función limpiar_vehiculos(vehiculos, velocidades, frame_idx, timeout=30, v_min=5)**: Elimina vehículos que no han sido actualizados en los últimos timeout frames, guardando sus velocidades si estas superan una velocidad mínima (v_min). Esto ayuda a liberar memoria y a mantener las estadísticas de velocidad acumuladas de vehículos que ya no están presentes en la escena.

#### Variables y parámetros de configuración:

**LINEAS**: Define líneas de detección por carril en coordenadas de píxeles.

**Umbrales** como UMBRAL para binarización, AREA_MIN y AREA_MAX para filtrar contornos por tamaño, y tolerancia espacial para considerar que un vehículo está sobre una línea.

TIMEOUT, MAX_DIST y otros parámetros ajustan la sensibilidad y comportamiento del sistema.

### Flujo del Sistema
1. Se carga el vídeo y se calcula un fondo promedio para la sustracción de fondo inicial.

2. Para cada frame, se resta el fondo, binariza la imagen, limpia con operaciones morfológicas y aplica una máscara para limitar la detección a la región de interés.

3. Se detectan contornos que se filtran por área y proporción para identificar posibles vehículos.

4. Se asocian estas detecciones con vehículos existentes o se crean nuevos objetos Vehiculo.

5. Se actualizan posiciones y velocidades, contabilizando vehículos que cruzan las líneas definidas.

6. Periódicamente se limpian vehículos inactivos.

7. Al final se muestran estadísticas de conteo y velocidades por carril.

### Resultados

El resultado que os tiene que aparecer por pantalla al ejecutar todo el script es asi:

https://github.com/user-attachments/assets/fd438348-9326-4cbd-8239-80b57837a341


```
============================================================
RESULTADOS FINALES
============================================================
Carril 1:   5 vehículos | Vel: 56.1 km/h (min: 47.2, max: 65.5)
Carril 2:   5 vehículos | Vel: 53.5 km/h (min: 50.2, max: 55.7)
Carril 3:  10 vehículos | Vel: 126.0 km/h (min: 104.3, max: 145.0)
Carril 4:  12 vehículos | Vel: 108.3 km/h (min: 38.2, max: 137.0)
Carril 5:   5 vehículos | Sin datos de velocidad
Carril 6:   9 vehículos | Sin datos de velocidad
Carril 7:   7 vehículos | Vel: 88.2 km/h (min: 88.2, max: 88.2)
------------------------------------------------------------
TOTAL: 53 vehículos
Velocidad Global: 84.1 km/h (min: 38.2, max: 145.0)
============================================================
```


## Autores
- Jaime Ercilla Martin
- Javier Bolívar García-Izquierdo




