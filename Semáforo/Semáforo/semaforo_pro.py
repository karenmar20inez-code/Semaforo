import pygame
import sys
import time
import random
import os

# --- 1. CONFIGURACIÓN DE ENTORNO Y CONSTANTES DE FÍSICA ---
ANCHO_JUEGO, ALTO_JUEGO = 900, 750 
ANCHO_CONSOLA = 250
ANCHO_TOTAL = ANCHO_JUEGO + ANCHO_CONSOLA

LIMITE_VELOCIDAD_KMH = 80
TIEMPO_FLASH_FRAMES = 10
DISTANCIA_FRENADO_FRONTAL = 85
TOLERANCIA_ALINEACION = 15

ZONA_RADAR_X = (390, 510)
ZONA_RADAR_Y = (380, 470)
ZONA_CRUCE_X = (385, 515)
ZONA_CRUCE_Y = (375, 475)

LINEA_FRENO_H_ESTE = (300, 355)
LINEA_FRENO_H_OESTE = (540, 595)
LINEA_FRENO_V_NORTE = (280, 335)
LINEA_FRENO_V_SUR = (465, 520)

# os.path.abspath(__file__) obtiene la ruta absoluta del archivo en ejecución.
# os.path.dirname extrae el directorio padre. Esto garantiza que el programa 
# encuentre la carpeta 'assets' sin importar desde qué ruta o editor se ejecute.
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_TOTAL, ALTO_JUEGO))
pygame.display.set_caption("Metropolis Traffic Control")
reloj = pygame.time.Clock()

# --- 2. GESTIÓN DE RECURSOS ---
def cargar_recurso_grafico(nombre_archivo, dimensiones=None):
    """
    Carga imágenes en memoria. Utiliza convert_alpha() para que Pygame renderice 
    por hardware el canal de transparencia (los bordes invisibles del PNG), 
    optimizando el rendimiento de fotogramas por segundo (FPS).
    """
    ruta_absoluta = os.path.join(DIRECTORIO_BASE, "assets", nombre_archivo)
    try:
        imagen = pygame.image.load(ruta_absoluta).convert_alpha()
        return pygame.transform.scale(imagen, dimensiones) if dimensiones else imagen
    except FileNotFoundError:
        print(f"[CRITICAL] Recurso no encontrado: {ruta_absoluta}")
        superficie_error = pygame.Surface(dimensiones if dimensiones else (50, 50))
        superficie_error.fill((200, 0, 0))
        return superficie_error

IMG_FONDO = cargar_recurso_grafico("image_15.png", (ANCHO_JUEGO, ALTO_JUEGO))

# Comprensión de listas (List Comprehension): Construye la lista iterando directamente 
# sobre el arreglo [0, 2, 3, 4, 5]. Es más eficiente en memoria que un bucle for tradicional.
AUTOS_DISPONIBLES = [cargar_recurso_grafico(f"image_{i}.png", (58, 26)) for i in [0, 2, 3, 4, 5]]

# --- 3. CLASES DE DOMINIO ---
class Vehiculo:
    def __init__(self, x, y, eje_movimiento, sentido_vectorial, semaforo_referencia):
        self.id_vehiculo = random.randint(1000, 9999)
        self.x = x
        self.y = y
        self.eje_movimiento = eje_movimiento 
        self.sentido_vectorial = sentido_vectorial
        self.semaforo = semaforo_referencia
        
        self.superficie_grafica = self._generar_sprite()
        self.ancho, self.alto = self.superficie_grafica.get_size()
        
        es_infractor = random.random() < 0.20
        self.velocidad_base = random.uniform(4.6, 6.4) if es_infractor else random.uniform(2.8, 4.4)
        self.velocidad_actual = self.velocidad_base
        self.velocidad_kmh = int(self.velocidad_base * 18)
        
        self.ha_cruzado_interseccion = False
        self.infraccion_registrada = False
        self.frames_restantes_flash = 0

    def _generar_sprite(self):
        imagen_base = random.choice(AUTOS_DISPONIBLES)
        if self.eje_movimiento == "H":
            return imagen_base if self.sentido_vectorial == 1 else pygame.transform.flip(imagen_base, True, False)
        return pygame.transform.rotate(imagen_base, 270 if self.sentido_vectorial == 1 else 90)

    def mover(self, flujo_vehicular, registro_multas):
        esta_bloqueado = self._detectar_colision_frontal(flujo_vehicular)
        
        if not self.ha_cruzado_interseccion and not esta_bloqueado:
            esta_bloqueado = self._evaluar_frenado_semaforo()
            self._auditar_velocidad(registro_multas)
            self._actualizar_estado_cruce()

        self.velocidad_actual = 0 if esta_bloqueado else self.velocidad_base
        
        if self.eje_movimiento == "H":
            self.x += self.velocidad_actual * self.sentido_vectorial
        else:
            self.y += self.velocidad_actual * self.sentido_vectorial

    def _detectar_colision_frontal(self, flujo_vehicular):
        """
        Evalúa colisiones inyectando la lista de todos los vehículos activos. 
        Se utiliza cálculo de distancia Euclidiana simplificada por eje para minimizar el costo del CPU.
        """
        for otro in flujo_vehicular:
            if otro == self: 
                continue
            
            if self.eje_movimiento == "H":
                distancia = otro.x - (self.x + self.ancho) if self.sentido_vectorial == 1 else self.x - (otro.x + otro.ancho)
                desalineacion = abs(self.y - otro.y)
            else:
                distancia = otro.y - (self.y + self.alto) if self.sentido_vectorial == 1 else self.y - (otro.y + otro.alto)
                desalineacion = abs(self.x - otro.x)
                
            if 0 < distancia < DISTANCIA_FRENADO_FRONTAL and desalineacion < TOLERANCIA_ALINEACION:
                return True
        return False

    def _evaluar_frenado_semaforo(self):
        if self.semaforo.estado == "verde":
            return False
            
        if self.eje_movimiento == "H":
            frente = self.x + self.ancho if self.sentido_vectorial == 1 else self.x
            rango = LINEA_FRENO_H_ESTE if self.sentido_vectorial == 1 else LINEA_FRENO_H_OESTE
        else:
            frente = self.y + self.alto if self.sentido_vectorial == 1 else self.y
            rango = LINEA_FRENO_V_NORTE if self.sentido_vectorial == 1 else LINEA_FRENO_V_SUR

        return rango[0] < frente < rango[1]

    def _auditar_velocidad(self, registro_multas):
        # Transductor concurrente: Evalúa la posición geométrica contra la matriz central
        en_zona_radar = (ZONA_RADAR_X[0] < self.x < ZONA_RADAR_X[1]) or (ZONA_RADAR_Y[0] < self.y < ZONA_RADAR_Y[1])
        if en_zona_radar and self.velocidad_kmh > LIMITE_VELOCIDAD_KMH and not self.infraccion_registrada:
            self.infraccion_registrada = True
            self.frames_restantes_flash = TIEMPO_FLASH_FRAMES
            # Añade un diccionario a la lista compartida de registros
            registro_multas.append({
                "id": self.id_vehiculo, 
                "vel": self.velocidad_kmh, 
                "hora": time.strftime("%H:%M")
            })

    def _actualizar_estado_cruce(self):
        if (self.eje_movimiento == "H" and ZONA_CRUCE_X[0] < self.x < ZONA_CRUCE_X[1]) or \
           (self.eje_movimiento == "V" and ZONA_CRUCE_Y[0] < self.y < ZONA_CRUCE_Y[1]):
            self.ha_cruzado_interseccion = True

    def dibujar(self, superficie_destino):
        superficie_destino.blit(self.superficie_grafica, (self.x, self.y))
        if self.frames_restantes_flash > 0:
            centro = (int(self.x + self.ancho / 2), int(self.y + self.alto / 2))
            pygame.draw.circle(superficie_destino, (255, 255, 255), centro, 40)
            self.frames_restantes_flash -= 1

class Semaforo:
    def __init__(self, x, y, inicial):
        self.x = x
        self.y = y
        self.estado = inicial
        # time.time() almacena el momento de creación en segundos absolutos (UNIX Time)
        # Esto permite medir deltas de tiempo sin detener el hilo principal (non-blocking)
        self.timer = time.time()

    def dibujar(self, superficie_destino):
        pygame.draw.rect(superficie_destino, (25, 25, 25), (self.x, self.y, 30, 90), border_radius=5)
        posiciones = {"rojo": 15, "amarillo": 45, "verde": 75}
        
        for color, pos_y in posiciones.items():
            color_rgb = {"rojo": (255, 0, 0), "amarillo": (255, 200, 0), "verde": (0, 255, 0)}[color] if self.estado == color else (50, 50, 50)
            pygame.draw.circle(superficie_destino, color_rgb, (self.x + 15, self.y + pos_y), 10)

# --- 4. ORQUESTACIÓN Y CONTROL ---
def alternar_luces(sem_h, sem_v):
    """
    Motor del Autómata Finito Determinista (AFD).
    Modifica la variable de estado y restablece el cronómetro a time.time() actual
    para comenzar a medir el siguiente ciclo en la máquina de estados.
    """
    ahora = time.time()
    if sem_h.estado == "verde": 
        sem_h.estado = "amarillo"
    elif sem_h.estado == "amarillo": 
        sem_h.estado = "rojo"
        sem_v.estado = "verde"
        sem_v.timer = ahora
    elif sem_v.estado == "verde": 
        sem_v.estado = "amarillo"
    elif sem_v.estado == "amarillo": 
        sem_v.estado = "rojo"
        sem_h.estado = "verde"
        sem_h.timer = ahora
    sem_h.timer = ahora

# --- 5. BUCLE DE EJECUCIÓN PRINCIPAL ---
# Se ajustan las coordenadas 'Y' y 'X' para colocar las cajas en las esquinas de las aceras
semaforo_horizontal = Semaforo(350, 420, "verde")
semaforo_vertical = Semaforo(510, 220, "rojo")
lista_vehiculos = []
registro_multas = []
multa_seleccionada = 0

while True:
    ahora = time.time()
    
    # Condición de transición del AFD: si el delta de tiempo supera el límite estático
    if (semaforo_horizontal.estado == "verde" and ahora - semaforo_horizontal.timer > 8) or \
       (semaforo_horizontal.estado == "amarillo" and ahora - semaforo_horizontal.timer > 2) or \
       (semaforo_vertical.estado == "verde" and ahora - semaforo_vertical.timer > 8) or \
       (semaforo_vertical.estado == "amarillo" and ahora - semaforo_vertical.timer > 2):
        alternar_luces(semaforo_horizontal, semaforo_vertical)

    pantalla.blit(IMG_FONDO, (0, 0))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE: 
                alternar_luces(semaforo_horizontal, semaforo_vertical)
            
            if registro_multas: 
                if evento.key == pygame.K_UP: 
                    multa_seleccionada = max(0, multa_seleccionada - 1)
                if evento.key == pygame.K_DOWN: 
                    multa_seleccionada = min(len(registro_multas) - 1, multa_seleccionada + 1)
                if evento.key in [pygame.K_m, pygame.K_d]:
                    registro_multas.pop(multa_seleccionada)
                    multa_seleccionada = 0

    if random.random() < 0.03 and len(lista_vehiculos) < 14:
        origen = random.randint(1, 4)
        nodos_generacion = {
            1: (-100, 373, "H", 1, semaforo_horizontal), 
            2: (1000, 333, "H", -1, semaforo_horizontal),
            3: (465, -100, "V", 1, semaforo_vertical), 
            4: (412, 850, "V", -1, semaforo_vertical)
        }
        # Desempaquetado de argumentos (*): El asterisco extrae los 5 elementos de la tupla 
        # seleccionada en el diccionario y los inyecta como parámetros individuales en __init__
        lista_vehiculos.append(Vehiculo(*nodos_generacion[origen]))

    # Se usa [:] para iterar sobre una copia de la lista. Esto previene errores de 
    # desplazamiento de índices al eliminar elementos (v) dentro del mismo bucle.
    for vehiculo in lista_vehiculos[:]:
        vehiculo.mover(lista_vehiculos, registro_multas)
        vehiculo.dibujar(pantalla)
        # Garbage Collection (Liberación de memoria): Si el vehículo sale de los límites
        # matemáticos de la pantalla, se destruye su instancia para no sobrecargar la RAM.
        if vehiculo.x > 1100 or vehiculo.x < -200 or vehiculo.y > 950 or vehiculo.y < -200: 
            lista_vehiculos.remove(vehiculo)

    semaforo_horizontal.dibujar(pantalla)
    semaforo_vertical.dibujar(pantalla)

    # --- RENDERIZADO DE INTERFAZ ---
    pygame.draw.rect(pantalla, (15, 15, 20), (ANCHO_JUEGO, 0, ANCHO_CONSOLA, ALTO_JUEGO))
    fuente_titulo = pygame.font.SysFont("Impact", 22)
    fuente_info = pygame.font.SysFont("Arial", 14)
    
    pantalla.blit(fuente_titulo.render("TRÁNSITO: PENDIENTES", True, (255, 200, 0)), (ANCHO_JUEGO + 10, 30))
    
    if not registro_multas:
        pantalla.blit(fuente_info.render("Sin infracciones", True, (100, 100, 100)), (ANCHO_JUEGO + 10, 70))
    else:
        # enumerate() permite obtener simultáneamente el índice (0, 1, 2...) y el valor
        # del elemento iterado, útil para multiplicar y generar espaciado en la interfaz.
        for indice, multa in enumerate(registro_multas[:15]):
            color_texto = (0, 255, 255) if indice == multa_seleccionada else (255, 255, 255)
            cursor = ">" if indice == multa_seleccionada else " "
            texto = f"{cursor} ID:{multa['id']} | {multa['vel']} km/h"
            pantalla.blit(fuente_info.render(texto, True, color_texto), (ANCHO_JUEGO + 10, 70 + indice * 22))

    instrucciones = ["[ESPACIO] Cambio Manual", "[ARRIBA/ABAJO] Navegar", "[M] Multar  [D] Descartar"]
    for idx, texto in enumerate(instrucciones):
        pantalla.blit(fuente_info.render(texto, True, (180, 180, 180)), (ANCHO_JUEGO + 10, 620 + idx * 25))
    
    pygame.display.flip()
    reloj.tick(60)