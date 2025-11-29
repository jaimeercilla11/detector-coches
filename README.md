# Sistema de Detección y Conteo de Vehículos
Sistema de visión por computador para detección, conteo y cálculo de velocidad de vehículos en vídeos de tráfico, utilizando técnicas de procesamiento de imágenes con OpenCV.
## Características

- Detección automática de vehículos mediante sustracción de fondo
- Conteo por carril con líneas de detección configurables
- Cálculo de velocidad en tiempo real (km/h)
- Tracking de vehículos con identificación única
- Estadísticas detalladas por carril y globales
- Visualización en tiempo real con rectángulos y contadores


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

### Controles durante la ejecución:

- Presionar "q" para detener el procesamiento
- El vídeo se mostrará en una ventana de OpenCV

### Resultado


https://github.com/user-attachments/assets/fd438348-9326-4cbd-8239-80b57837a341


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

## Autores
- Jaime Ercilla Martin
- Javier Bolivar Garcia-Izquierdo




