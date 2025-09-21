import pygame, math

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cañón con proyectiles parabólicos")

BLANCO = (255,255,255)
NEGRO  = (0,0,0)
AZUL   = (40,120,220)
ROJO   = (220,40,40)

# Cargar imagen del proyectil
PROJECTILE_IMG = None
PROJECTILE_PATH = "Spaceship/img_downsized/ball.png"  # Ajusta la ruta según tu estructura

try:
    PROJECTILE_IMG = pygame.image.load(PROJECTILE_PATH).convert_alpha()
except Exception as e:
    print(f"No se pudo cargar la imagen del proyectil: {e}")
    PROJECTILE_IMG = None

class Plataforma:
    def __init__(self, x, y, w, h, speed=1800, min_x=500, max_x=700, auto=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed        # px/seg
        self.dir = 1              # 1 derecha, -1 izquierda
        self.min_x = min_x
        self.max_x = max_x
        self.auto = auto          # True: oscilante, False: teclado

    def update(self, dt, keys=None):
        if self.auto:
            # movimiento oscilante entre min_x y max_x
            self.rect.x += int(self.dir * self.speed * dt)
            if self.rect.right >= self.max_x:
                self.rect.right = self.max_x
                self.dir = -1
            elif self.rect.left <= self.min_x:
                self.rect.left = self.min_x
                self.dir = 1
        else:
            # control por teclado (← →)
            vx = 0
            if keys[pygame.K_LEFT]:  vx -= self.speed
            if keys[pygame.K_RIGHT]: vx += self.speed
            self.rect.x += int(vx * dt)
            # límites duros
            if self.rect.left < self.min_x:
                self.rect.left = self.min_x
            if self.rect.right > self.max_x:
                self.rect.right = self.max_x

    def draw(self, surf):
        pygame.draw.rect(surf, AZUL, self.rect, border_radius=10)


class Projectile:
    def __init__(self, x, y, vx, vy):
        # Configuración de imagen similar a la clase Bola
        if PROJECTILE_IMG:
            self.w = PROJECTILE_IMG.get_width()
            self.h = PROJECTILE_IMG.get_height()
            self.r = self.w // 2
        else:
            self.r = 8  # radio por defecto si no hay imagen
            self.w = self.r * 2
            
        self.x = x
        self.y = y
        self.vx = vx          # velocidad horizontal inicial
        self.vy = vy          # velocidad vertical inicial
        self.gravity = 500    # aceleración de la gravedad (px/s²)
        self.active = True
        
    def update(self, dt):
        if not self.active:
            return
            
        # Movimiento parabólico
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt  # La gravedad afecta solo la velocidad vertical
        
        # Desactivar si sale de la pantalla
        if self.x < 0 or self.x > W or self.y > H:
            self.active = False
    
    def get_rect(self):
        """Retorna un rect para detección de colisiones"""
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
            
    def draw(self, surf):
        if self.active:
            if PROJECTILE_IMG:
                # Centrar la imagen en (x, y) igual que en la clase Bola
                surf.blit(PROJECTILE_IMG, (self.x - self.w//2, self.y - self.h//2))
            else:
                # Fallback: dibujar círculo si no hay imagen
                pygame.draw.circle(surf, ROJO, (int(self.x), int(self.y)), self.r)

    def check_collision_with_platform(self, platform):
        """Verifica si el proyectil colisiona con la plataforma"""
        if not self.active:
            return False
        
        projectile_rect = self.get_rect()
        if projectile_rect.colliderect(platform.rect):
            self.active = False  # Desactivar el proyectil
            return True
        return False


# --- Configura aquí ---
AUTO = True  # True = oscilante, False = teclado
plataforma = Plataforma(x=200, y=450, w=160, h=20, speed=220,
                        min_x=80, max_x=W-80, auto=AUTO)

# Lista para almacenar los proyectiles
projectiles = []

def draw_arrow(surf, 
               color, 
               start, end, width=4, head_len=20, head_angle_deg=30, max_len=None):
    """
    Dibuja una flecha desde start -> end.
    - max_len: longitud máxima permitida de la flecha
    Retorna la posición final de la punta (para disparar desde ahí)
    """
    x1, y1 = start
    x2, y2 = end

    # Vector hacia el mouse
    dx, dy = (x2 - x1), (y2 - y1)
    length = math.hypot(dx, dy)

    # Si excede el máximo, acortar
    if max_len and length > max_len:
        factor = max_len / length
        dx *= factor
        dy *= factor
        x2, y2 = x1 + dx, y1 + dy

    # Línea (tallo)
    pygame.draw.line(surf, color, start, (x2, y2), width)

    # Geometría de la punta
    ang = math.atan2(dy, dx)
    head_angle = math.radians(head_angle_deg)
    left = (x2 - head_len * math.cos(ang - head_angle),
            y2 - head_len * math.sin(ang - head_angle))
    right = (x2 - head_len * math.cos(ang + head_angle),
             y2 - head_len * math.sin(ang + head_angle))

    pygame.draw.polygon(surf, color, [(x2, y2), left, right])
    
    # Retornar la punta de la flecha y la longitud original
    return (x2, y2), math.hypot(dx, dy)


def create_projectile(start_pos, end_pos, max_len=100):
    """
    Crea un proyectil basado en la posición de la flecha
    La velocidad inicial es proporcional a la longitud de la flecha
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    # Vector dirección
    dx, dy = (x2 - x1), (y2 - y1)
    length = math.hypot(dx, dy)
    
    # Limitar longitud para cálculo de velocidad
    effective_length = min(length, max_len) if max_len else length
    
    # Normalizar el vector dirección
    if length > 0:
        dx_norm = dx / length
        dy_norm = dy / length
    else:
        dx_norm = dy_norm = 0
    
    # La velocidad inicial es proporcional a la longitud de la flecha
    speed_factor = 5  # Ajusta este valor para cambiar la velocidad
    initial_speed = effective_length * speed_factor
    
    vx = dx_norm * initial_speed
    vy = dy_norm * initial_speed
    
    # El proyectil sale desde la punta de la flecha
    return Projectile(x2, y2, vx, vy)


# Demo
clock = pygame.time.Clock()
origin = (0, H)
running = True
hits = 0  # Contador de aciertos

while running:
    dt = clock.tick(60) / 1000.0
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Click izquierdo
                mouse_pos = pygame.mouse.get_pos()
                # Primero calcular la punta de la flecha
                arrow_tip, arrow_length = draw_arrow(screen, NEGRO, origin, mouse_pos, 
                                                   width=5, head_len=22, head_angle_deg=30, max_len=100)
                # Crear proyectil usando la punta de la flecha como destino
                projectile = create_projectile(origin, arrow_tip, max_len=100)
                projectiles.append(projectile)

    screen.fill(BLANCO)

    keys = pygame.key.get_pressed()
    plataforma.update(dt, keys)

    # Dibujar flecha
    mouse_pos = pygame.mouse.get_pos()
    arrow_tip, arrow_length = draw_arrow(screen, NEGRO, origin, mouse_pos, 
                                       width=5, head_len=22, head_angle_deg=30, max_len=100)

    # Actualizar proyectiles y verificar colisiones
    for projectile in projectiles[:]:  # Copia la lista para poder modificarla
        projectile.update(dt)
        
        # Verificar colisión con la plataforma
        if projectile.check_collision_with_platform(plataforma):
            hits += 1  # Incrementar contador de aciertos
        
        # Eliminar proyectiles inactivos
        if not projectile.active:
            projectiles.remove(projectile)
        else:
            projectile.draw(screen)

    plataforma.draw(screen)

    # Mostrar información en pantalla
    font = pygame.font.Font(None, 36)
    info_text = font.render(f"Proyectiles activos: {len(projectiles)}", True, NEGRO)
    screen.blit(info_text, (10, 10))
    
    length_text = font.render(f"Longitud flecha: {int(arrow_length)}", True, NEGRO)
    screen.blit(length_text, (10, 50))
    
    # Mostrar aciertos
    hits_text = font.render(f"Aciertos: {hits}", True, NEGRO)
    screen.blit(hits_text, (10, 90))

    pygame.display.flip()

pygame.quit()