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


![Descripción opcional](https://i.imgur.com/SW43aGF.gif)






