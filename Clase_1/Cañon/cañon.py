import pygame, math

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flecha con longitud limitada")

BLANCO = (255,255,255)
NEGRO  = (0,0,0)
AZUL   = (40,120,220)

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


# --- Configura aquí ---
AUTO = True  # True = oscilante, False = teclado
plataforma = Plataforma(x=200, y=350, w=160, h=20, speed=420,
                        min_x=250, max_x=W-80, auto=AUTO)

def draw_arrow(surf, 
               color, 
               start, end, width=4, head_len=20, head_angle_deg=30, max_len=None):
    """
    Dibuja una flecha desde start -> end.
    - max_len: longitud máxima permitida de la flecha
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


# Demo
clock = pygame.time.Clock()
origin = (0, H)
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill(BLANCO)

    keys = pygame.key.get_pressed()
    plataforma.update(dt, keys)

    mouse_pos = pygame.mouse.get_pos()
    draw_arrow(screen, NEGRO, origin, mouse_pos, width=5, head_len=22, head_angle_deg=30, max_len=100)

    plataforma.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

