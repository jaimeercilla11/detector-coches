# Práctica 2: Conteo de Vehículos en Vías de Tráfico

**Fundamentos de Sistemas Inteligentes**  
**Grado en Ciencias e Ingeniería de Datos**  
**Autores:** Jaime Ercilla Martín, Javier Bolívar García-Izquierdo  
**Fecha:** Diciembre 2024

---

## 1. Introducción

Esta práctica aborda el problema del conteo automático de vehículos en vías de tráfico mediante técnicas de visión por computador. El objetivo es desarrollar un sistema capaz de detectar, rastrear y contabilizar vehículos que transitan por múltiples carriles, calculando además sus velocidades de desplazamiento.

### 1.1 Objetivos del Proyecto

- Implementar un contador de vehículos para múltiples carriles
- Desarrollar un sistema de tracking robusto con identificación única de vehículos
- Calcular velocidades de circulación en tiempo real
- Proporcionar estadísticas detalladas por carril y globales

### 1.2 Tecnologías Utilizadas

El desarrollo se ha realizado íntegramente con **OpenCV** (cv2) en Python, siguiendo los requisitos del enunciado. Se han utilizado técnicas clásicas de procesamiento de imagen sin recurrir a deep learning, específicamente:

- **Background Subtraction** con algoritmo MOG2
- **Procesamiento morfológico** para limpieza de máscaras
- **Detección de contornos** para segmentación de vehículos
- **Tracking simple** basado en proximidad espacial

---

## 2. Metodología

### 2.1 Arquitectura del Sistema

El sistema está dividido en dos módulos principales con responsabilidades bien definidas:

- **main.py**: Gestión del flujo de video, ventanas de visualización y bucle principal
- **utils.py**: Lógica de procesamiento, tracking, conteo y cálculo de velocidades

```
[Frame de Video] → [Segmentación de Fondo] → [Detección de Contornos] 
    → [Tracking por Carril] → [Conteo + Velocidad] → [Visualización]
```

### 2.2 Técnicas de Procesamiento

#### 2.2.1 Segmentación de Fondo (Background Subtraction)

Se emplea el algoritmo **MOG2 (Mixture of Gaussians)** implementado en OpenCV por sus ventajas:

- **Adaptación dinámica** a cambios graduales de iluminación
- **Tolerancia** a pequeños movimientos de cámara y vibraciones
- **Buen balance** entre precisión y rendimiento computacional
- **No requiere entrenamiento** previo

**Configuración utilizada:**
```python
cv2.createBackgroundSubtractorMOG2(
    history=300,           # 300 frames de histórico
    varThreshold=50,       # Umbral de varianza para foreground
    detectShadows=False    # Desactivado para simplificar
)
```

#### 2.2.2 Procesamiento Morfológico

Tras obtener la máscara binaria se aplican operaciones morfológicas para mejorar la calidad:

1. **Operación de cierre morfológico** (kernel 5×5):
   - Elimina huecos pequeños dentro de los objetos detectados
   - Conecta componentes cercanos del mismo vehículo
   - Reduce fragmentación de siluetas

2. **Umbralización binaria** (threshold=254):
   - Binarización final estricta para obtener siluetas limpias
   - Elimina píxeles grises residuales

Esto reduce significativamente el ruido y mejora la continuidad de los blobs detectados, facilitando el conteo preciso.

#### 2.2.3 Detección y Filtrado de Contornos

Se extraen contornos externos con `cv2.findContours()` y se aplican dos filtros críticos:

| Filtro | Valor | Justificación |
|--------|-------|---------------|
| **Área mínima** | 500 px² | Descarta ruido, sombras y objetos muy pequeños |
| **Ancho máximo** | 420 px | Evita detecciones erróneas de regiones grandes (fondos, edificios) |

Estos umbrales se ajustaron experimentalmente para el video proporcionado, equilibrando detección de motocicletas (pequeñas) y eliminación de falsos positivos.

### 2.3 Sistema de Tracking por Carril

#### 2.3.1 Líneas de Conteo Virtuales

Se definen **7 líneas virtuales horizontales** distribuidas estratégicamente en los carriles de interés. Cada línea se representa mediante un diccionario con coordenadas:

```python
{"cx1": x_inicio, "cy1": y, "cx2": x_fin, "cy2": y}
```

Un vehículo se considera **detectado** cuando su centroide cruza la línea con un margen de tolerancia de **±10 píxeles verticales**, permitiendo cierta flexibilidad ante vibraciones o imprecisiones de detección.

#### 2.3.2 Algoritmo de Asociación de Objetos

Para cada carril se mantiene un **diccionario independiente** de objetos rastreados. El algoritmo de asociación funciona así:

1. **Cálculo del centroide**: Se obtiene el centro (cx, cy) del bounding box del contorno
2. **Búsqueda de match**: Se busca en el diccionario del carril si existe un objeto previo a menos de 50 píxeles
3. **Si existe match**:
   - Se actualiza la posición del track
   - Se calcula la velocidad entre posiciones
   - Se registra el frame actual
4. **Si NO existe match**:
   - Se crea un nuevo track con ID único
   - Se incrementa el contador de vehículos del carril
5. **Limpieza periódica**: Se eliminan tracks inactivos tras 14 frames sin detección

**Ventajas:**
- Tracking independiente por carril evita confusiones entre vías
- Sistema de IDs únicos permite estadísticas individuales por vehículo

**Limitaciones conocidas:**
- Asignación por "primer match" en vez de óptimo global (no usa Hungarian algorithm)
- Puede fallar con múltiples vehículos muy cercanos (< 50px)
- No distingue dirección de movimiento (útil para vías de doble sentido)

### 2.4 Cálculo de Velocidad

La velocidad instantánea se calcula mediante **distancia euclidiana** entre posiciones sucesivas:

```python
distancia = √((x₂-x₁)² + (y₂-y₁)²)
tiempo = (frame_actual - frame_previo) / fps
velocidad = distancia / tiempo  # píxeles/segundo
```

Se almacenan **todas las velocidades detectadas** para calcular:
- Velocidad media por carril
- Velocidad media global del sistema

**Nota importante:** Las velocidades están expresadas en **píxeles/segundo**. Para convertir a km/h se requeriría:
1. Calibración espacial conociendo dimensiones reales de la vía (ej: ancho de carril = 3.5m)
2. Factor de conversión píxeles → metros
3. Conversión m/s → km/h (×3.6)

---

## 3. Implementación

### 3.1 Estructura del Proyecto

```
proyecto/
├── main.py           # Script principal
├── utils.py          # Lógica de detección y tracking
├── trafico01.mp4     # Video de entrada
└── README.md         # Documentación
```

### 3.2 Configuración de Parámetros

Los parámetros clave del sistema y su justificación:

| Parámetro | Valor | Ubicación | Justificación |
|-----------|-------|-----------|---------------|
| `min_area` | 500 px² | TrafficCounter | Filtrar ruido y objetos pequeños no vehiculares |
| `max_width` | 420 px | TrafficCounter | Evitar detecciones de regiones grandes (fondos) |
| `max_tracking` | 14 frames | TrafficCounter | Balance entre persistencia y limpieza de memoria |
| `margin` (línea) | 10 px | line_crossed() | Tolerancia vertical para cruces de línea |
| `margin` (tracking) | 50 px | _update_track_for_lane() | Distancia máxima para asociación espacial |
| `history` | 300 | MOG2 | Frames de histórico para modelar fondo estable |
| `varThreshold` | 50 | MOG2 | Sensibilidad de detección de movimiento |

### 3.3 Componentes Principales

#### Clase `TrafficCounter`
Gestiona toda la lógica de visión por computador:
- **Atributos**: Contadores, tracks activos, velocidades acumuladas, subtractor de fondo
- **Métodos públicos**:
  - `process_frame()`: Procesa un frame completo y retorna máscaras anotadas
  - `print_results()`: Imprime estadísticas finales por consola
- **Métodos privados**:
  - `_update_track_for_lane()`: Actualiza/crea tracks y calcula velocidades
  - `_cleanup_expired_tracks()`: Elimina objetos inactivos
  - `_draw_lanes_and_counts()`: Renderiza overlays visuales

#### Función `line_crossed()`
Detecta si un centroide ha cruzado una línea de conteo con tolerancia configurable.

#### Función `speed_calc()`
Calcula velocidad instantánea entre dos posiciones temporales usando distancia euclidiana.

### 3.4 Visualización en Tiempo Real

El sistema muestra **dos ventanas simultáneas** redimensionables:

1. **"Máscara"**: Visualización de la segmentación binaria (útil para debug y ajuste de parámetros)
2. **"Detección de Vehículos"**: Frame anotado mostrando:
   - **Líneas de conteo** en color cian (cyan)
   - **Contadores por carril** en texto verde sobre cada línea
   - **Estadísticas globales** en la esquina superior:
     - Total de vehículos detectados
     - Velocidad media global (px/s)

**Controles de usuario:**
- Presionar **'c'** o **Esc**: Detiene el procesamiento y muestra estadísticas finales
- Ventanas redimensionables para adaptarse a diferentes pantallas

### 3.5 Salida de Resultados

Al finalizar el procesamiento (o al presionar 'c'), se imprimen estadísticas detalladas por consola:

```
========== Conteo de Vehículos por Carril ==========
Carril 1: X vehículos, velocidad media: Y.Y px/s
Carril 2: X vehículos, velocidad media: Y.Y px/s
...
TOTAL vehículos: XX
Velocidad media global: YY.Y px/s
====================================================
```

Adicionalmente, durante la ejecución se imprimen velocidades instantáneas para cada detección (útil para debugging).

---

## 4. Resultados

### 4.1 Video Oficial (trafico01.mp4)

**Configuración del sistema:**
- **7 carriles** monitorizados simultáneamente
- Procesamiento en tiempo real con visualización dual
- Tracking independiente por carril

### 4.2 Demostración Visual

El sistema en funcionamiento muestra:

- **Ventana izquierda (Máscara)**: Segmentación binaria donde se aprecia claramente la silueta de cada vehículo detectado en blanco sobre fondo negro
- **Ventana derecha (Detección)**: Frame original con overlays que incluyen:
  - Líneas de conteo en cian marcando cada carril
  - Contadores individuales por carril en tiempo real
  - Estadísticas globales actualizadas continuamente

**Video de demostración:**  
Ver funcionamiento completo en: https://github.com/user-attachments/assets/9e9d5870-043f-4fa9-baf6-ebbd36eb6f3d

El video muestra el sistema procesando tráfico real con múltiples vehículos simultáneos en diferentes carriles, demostrando:
- Detección robusta de vehículos de diferentes tamaños
- Conteo preciso al cruzar líneas virtuales
- Tracking estable sin pérdidas significativas
- Cálculo de velocidades en tiempo real

### 4.3 Análisis Cualitativo

**Fortalezas observadas:**
- ✅ Detección consistente de vehículos en buenas condiciones de iluminación
- ✅ Separación correcta de carriles evita conteos cruzados
- ✅ Sistema de tracking mantiene identidad de vehículos a lo largo de varios frames
- ✅ Respuesta en tiempo real permite aplicaciones prácticas

**Casos problemáticos identificados:**
- ⚠️ Oclusiones parciales cuando vehículos se superponen visualmente
- ⚠️ Vehículos muy lentos o detenidos pueden "fundirse" con el fondo tras varios segundos
- ⚠️ Sombras pronunciadas ocasionalmente generan detecciones duplicadas
- ⚠️ Cambios bruscos de iluminación requieren tiempo de adaptación del MOG2

### 4.4 Observaciones Técnicas

El algoritmo de background subtraction MOG2 demuestra buena adaptabilidad a:
- Diferentes velocidades de vehículos (lentos y rápidos)
- Distintos tamaños (motocicletas, coches, furgonetas)
- Cambios graduales de iluminación durante el día

La configuración de parámetros elegida (`min_area=500`, `max_width=420`) proporciona un equilibrio adecuado entre sensibilidad (detectar vehículos pequeños) y especificidad (evitar falsos positivos por ruido).

---

## 5. Requisitos Cumplidos

### Requisitos Obligatorios

✅ **1. Contador básico de vehículos (MÍNIMO 5.0)**  
Implementado correctamente con líneas de conteo virtuales y sistema de tracking.

✅ **2. Múltiples vías y carriles**  
Sistema configurado para **7 carriles independientes** con conteo diferenciado por carril y estadísticas individuales.

### Requisitos Opcionales Implementados

✅ **5. Diferentes velocidades de vehículos**  
El algoritmo MOG2 se adapta automáticamente a vehículos rápidos y lentos sin necesidad de ajustes manuales.

✅ **6. Robustez a diferentes tipos de vehículos**  
Los filtros por área mínima (500px²) y ancho máximo (420px) permiten detectar desde motocicletas hasta camiones y furgonetas.

✅ **8. Cálculo de velocidad**  
Sistema completo de tracking con cálculo de velocidad instantánea mediante distancia euclidiana entre frames consecutivos. Se proporcionan estadísticas de velocidad media por carril y global.

✅ **10. Aporte adicional**  
- **Estadísticas agregadas**: Velocidad media global y por carril
- **Visualización dual**: Máscara binaria + frame anotado en paralelo
- **Sistema de tracking robusto**: Identificación única de vehículos con limpieza automática de objetos inactivos
- **Interfaz interactiva**: Ventanas redimensionables y controles de teclado

### Requisitos Opcionales NO Implementados

❌ **3. Aplicación a otros vídeos similares**  
No se ha probado exhaustivamente con videos adicionales por limitaciones de tiempo en la práctica.

❌ **4. Vías de doble sentido**  
El sistema actual no distingue dirección de movimiento (arriba↔abajo). Sería necesario implementar análisis de historial de posiciones para detectar trayectorias.

❌ **7. Contadores independientes por tipo de vehículo**  
La clasificación automática requeriría técnicas más avanzadas:
- Deep learning (YOLO, Faster R-CNN) - fuera del alcance con OpenCV puro
- O clasificadores por características manuales (relación aspecto, área) con entrenamiento supervisado

❌ **9. Escenarios de retención/atascos**  
El background subtraction tiene limitaciones inherentes con objetos estáticos prolongados:
- Vehículos detenidos > 10 segundos se integran en el modelo de fondo
- Posible solución: combinar con detección basada en bordes o características

---

## 6. Limitaciones y Trabajo Futuro

### 6.1 Limitaciones Identificadas

1. **Oclusiones totales o parciales**  
   Vehículos solapados visualmente pueden:
   - Contarse como uno solo
   - Perder tracking temporalmente
   - Generar IDs duplicados tras separarse

2. **Condiciones de iluminación variables**  
   - Cambios bruscos (nubes, túneles) afectan la segmentación
   - MOG2 requiere tiempo de adaptación (~5-10 segundos)
   - Sombras pronunciadas pueden generar falsos positivos

3. **Algoritmo de tracking simple**  
   - Asociación por "primer match" no es óptima
   - Puede fallar con alta densidad de vehículos (>3 por carril)
   - No utiliza predictores de movimiento (Kalman filter)

4. **Ausencia de calibración espacial**  
   - Velocidades reportadas en píxeles/segundo
   - No hay conversión automática a km/h
   - Requiere medición manual de referencias espaciales

5. **Dirección única**  
   - No distingue vehículos entrando vs saliendo
   - Imposible detectar infracciones de sentido contrario
   - Limitado a análisis de flujo unidireccional

6. **Sensibilidad a parámetros**  
   - Umbrales (`min_area`, `max_width`) ajustados para video específico
   - Puede requerir reconfiguración para diferentes escenas
   - No hay ajuste automático adaptativo

### 6.2 Mejoras Propuestas

**A corto plazo (extensiones directas):**

1. **Detección de dirección**  
   Implementar análisis de historial de posiciones (últimos N frames) para determinar vector de movimiento dominante.

2. **Clasificación simple por tamaño**  
   Categorizar vehículos según área y relación aspecto:
   - Motos: área < 1000px²
   - Coches: 1000-3000px²
   - Camiones: > 3000px² o ancho > 250px

3. **Exportación de datos estructurados**  
   Guardar resultados en CSV/JSON para análisis posterior:
   ```csv
   timestamp,carril,id_vehiculo,velocidad_px_s,tipo_estimado
   ```

4. **Calibración espacial opcional**  
   Permitir definir referencias espaciales (ej: "este carril mide 3.5m") para convertir px/s → km/h.

**A medio plazo (mejoras sustanciales):**

5. **Filtro de Kalman para tracking**  
   Predecir posiciones futuras basándose en trayectoria, mejorando robustez ante oclusiones temporales.

6. **Hungarian algorithm para asociación**  
   Optimizar asignación global de detecciones a tracks existentes.

7. **Detección de eventos**  
   - Alertas de velocidad excesiva (configurable por carril)
   - Detección de atascos (velocidad media < umbral)
   - Conteo de infracciones (sentido contrario)

8. **Interfaz gráfica**  
   Panel de control para ajustar parámetros en tiempo real sin editar código.

**A largo plazo (investigación avanzada):**

9. **Integración con deep learning**  
   - Detectores estado del arte (YOLOv8, Faster R-CNN)
   - Clasificación automática de tipos de vehículo
   - Tracking multi-objeto robusto (DeepSORT, ByteTrack)

10. **Sistema multi-cámara**  
    - Tracking global de vehículos entre múltiples vistas
    - Re-identificación de vehículos por características visuales
    - Análisis de flujo de tráfico a nivel de red vial

11. **Condiciones meteorológicas adversas**  
    - Adaptación a lluvia, nieve, niebla
    - Corrección de iluminación nocturna
    - Preprocesamiento especializado por condición

---

## 7. Conclusiones

Se ha desarrollado con éxito un **sistema funcional de conteo de vehículos** basado en técnicas clásicas de visión por computador utilizando exclusivamente OpenCV, cumpliendo estrictamente los requisitos del enunciado.

### Logros principales:

✅ **Arquitectura modular y extensible**: Separación clara entre captura/visualización (main.py) y lógica de procesamiento (utils.py)

✅ **Monitorización multi-carril**: Capacidad de procesar hasta 7 carriles simultáneamente con conteo independiente

✅ **Sistema de tracking robusto**: Identificación única de vehículos con persistencia temporal y limpieza automática

✅ **Análisis de velocidad**: Cálculo en tiempo real con estadísticas agregadas por carril y globales

✅ **Visualización informativa**: Interfaz dual que facilita tanto el análisis técnico (máscara) como la interpretación visual (anotaciones)

### Reflexión técnica:

El enfoque basado en **background subtraction con MOG2** ha demostrado ser efectivo y eficiente para el escenario planteado, especialmente considerando las restricciones de usar únicamente OpenCV clásico sin deep learning. Esta técnica ofrece:

- **Simplicidad computacional**: No requiere GPU ni grandes recursos
- **Interpretabilidad**: Resultados fáciles de analizar y depurar
- **Flexibilidad**: Adaptable a diferentes escenas mediante ajuste de parámetros

Sin embargo, también se han identificado **limitaciones inherentes** del enfoque clásico, especialmente en situaciones de alta densidad, oclusiones prolongadas y vehículos estáticos. Estas limitaciones son conocidas en la literatura y justifican la evolución hacia técnicas basadas en aprendizaje profundo en aplicaciones industriales reales.

### Aporte académico:

La práctica ha permitido:
- Aplicar conceptos fundamentales de procesamiento de imagen (seg
