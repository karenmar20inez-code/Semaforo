# Semaforo
¡Claro que sí! Aquí tienes una propuesta de `README.md` estructurada, clara y lista para agregar a tu repositorio. He unificado la funcionalidad de tu script de Pygame con el formato de tus archivos de registro.

---

# 🚦 Metropolis Traffic Control

## 📝 Descripción
**Metropolis Traffic Control** es un simulador de tráfico bidimensional desarrollado en Python utilizando la biblioteca Pygame. El sistema modela una intersección urbana con semáforos automatizados, inteligencia básica de frenado/detección de colisiones frontales y un radar de velocidad. Además, incluye una consola interactiva en tiempo real para que el operador audite y gestione las infracciones vehiculares.

## ✨ Características Principales
* **Simulación de Tráfico:** Generación aleatoria de vehículos con velocidades dinámicas (incluyendo un porcentaje de conductores infractores).
* **Control por Semáforos (AFD):** Autómata Finito Determinista que alterna el flujo vehicular de manera automática mediante deltas de tiempo.
* **Radar y Fotomultas:** Sistema que detecta vehículos que superan el límite de velocidad (80 km/h), activando un flash visual en pantalla y capturando los datos del auto.
* **Consola de Gestión en Vivo:** Interfaz lateral ('TRÁNSITO: PENDIENTES') para auditar infracciones, permitiendo emitir o descartar multas en tiempo real.
* **Sistema de Reportes:** Estructura de logs (`reporte_trafico.txt`) para el control estadístico de la intersección.

## 🛠️ Requisitos
* **Python 3.x**
* **Pygame**

Puedes instalar la dependencia principal ejecutando:
```bash
pip install pygame
```

## 🚀 Instalación y Ejecución
1. Clona o descarga el repositorio.
2. Asegúrate de contar con la carpeta `assets/` en el mismo directorio que el script. Esta carpeta debe contener:
   * El mapa/fondo: `image_15.png`
   * Los *sprites* de los vehículos: `image_0.png`, `image_2.png`, `image_3.png`, `image_4.png`, `image_5.png`
3. Ejecuta el simulador desde la terminal:
```bash
python semaforo_pro.py
```

## 🎮 Controles del Operador
El panel lateral derecho muestra las infracciones pendientes. Utiliza tu teclado para administrar la intersección:

* **`[ESPACIO]`**: Cambiar manualmente el estado de los semáforos.
* **`[FLECHA ARRIBA]` / `[FLECHA ABAJO]`**: Navegar por la lista de infracciones pendientes.
* **`[M]`**: Confirmar y emitir multa al vehículo seleccionado.
* **`[D]`**: Descartar la advertencia seleccionada.

## 📄 Estructura de Reportes (`reporte_trafico.txt`)
El simulador genera o alimenta registros de tráfico que los auditores pueden revisar posteriormente. [cite_start]El formato de salida incluye un encabezado con la fecha, el recuento total de vehículos procesados y el total de multas aplicadas[cite: 1]. 

A continuación, se detalla una lista de infractores donde cada entrada refleja:
* [cite_start]**ID** del vehículo[cite: 1].
* [cite_start]**Velocidad** registrada al momento del flash[cite: 2].
* [cite_start]**Hora** exacta de cruce[cite: 2, 3].

---

¿Te gustaría que agreguemos alguna sección extra a este documento, como una guía para modificar las constantes físicas (como el límite de velocidad o los tiempos del semáforo)?
