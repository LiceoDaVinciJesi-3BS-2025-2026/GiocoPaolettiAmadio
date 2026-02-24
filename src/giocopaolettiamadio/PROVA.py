import pygame
import sys
import math
import random

# --- FUNZIONI DI SUPPORTO ---
def load_frames(sheet, ROWS, COLS, FRAME_SIZE_W, FRAME_SIZE_H=None):
    frames = []
    if FRAME_SIZE_H is None:
        FRAME_SIZE_H = FRAME_SIZE_W
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * FRAME_SIZE_W, row * FRAME_SIZE_H, FRAME_SIZE_W, FRAME_SIZE_H)
            frames.append(sheet.subsurface(rect))
    return frames

def rescale_frames(lista_frames, fattore):
    return [pygame.transform.scale(f, (int(f.get_width()*fattore), int(f.get_height()*fattore))) for f in lista_frames]

def load_shrine_state(filename, shrine_rect):
    img = pygame.image.load(filename).convert_alpha()
    scale_factor = shrine_rect.width / img.get_width()
    return pygame.transform.scale(img, (shrine_rect.width, int(img.get_height() * scale_factor)))

def get_samurai_frames(filename, FRAME_SIZE_samurai):
    sheet = pygame.image.load(filename).convert_alpha()
    return rescale_frames(load_frames(sheet, 5, 5, FRAME_SIZE_samurai), 0.5)

def make_knife_surface(angle_rad, KNIFE_LENGTH, KNIFE_WIDTH):
    size = KNIFE_LENGTH * 2 + 4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    cos_a  = math.cos(angle_rad)
    sin_a  = math.sin(angle_rad)
    hw, hl = KNIFE_WIDTH, KNIFE_LENGTH
    pts = [
        (cx + cos_a*hl - sin_a*hw,  cy + sin_a*hl + cos_a*hw),
        (cx + cos_a*hl + sin_a*hw,  cy + sin_a*hl - cos_a*hw),
        (cx - cos_a*hl + sin_a*hw,  cy - sin_a*hl - cos_a*hw),
        (cx - cos_a*hl - sin_a*hw,  cy - sin_a*hl + cos_a*hw),
    ]
    pygame.draw.polygon(surf, (190, 210, 230), pts)
    pygame.draw.polygon(surf, (240, 250, 255), pts, 1)
    pygame.draw.circle(surf, (255, 255, 255), (int(cx + cos_a*hl), int(cy + sin_a*hl)), 2)
    h_pts = [
        (cx - cos_a*hl        - sin_a*(hw+2),  cy - sin_a*hl        + cos_a*(hw+2)),
        (cx - cos_a*hl        + sin_a*(hw+2),  cy - sin_a*hl        - cos_a*(hw+2)),
        (cx - cos_a*(hl-5)    + sin_a*(hw+2),  cy - sin_a*(hl-5)    - cos_a*(hw+2)),
        (cx - cos_a*(hl-5)    - sin_a*(hw+2),  cy - sin_a*(hl-5)    + cos_a*(hw+2)),
    ]
    pygame.draw.polygon(surf, (100, 70, 40), h_pts)
    return surf

# --- SISTEMA ORDE ---
def calcola_orda(wave_num):
    totale      = 4 + (wave_num - 1) * 2
    prob_dragon = min(0.1 + (wave_num - 1) * 0.1, 0.7)
    hp_mult     = 1.0 + (wave_num - 1) * 0.2
    params = [totale, prob_dragon, hp_mult]
    return params

def build_spawn_queue(params):
    queue = []
    for coso in range(params[0]):
        e_type = 'dragon' if random.random() < params[1] else 'slime'
        if e_type == 'slime':
            hp = int(30 * params[2]); espeed = 2.0; e_w, e_h = 80,  80
        else:
            hp = int(50 * params[2]); espeed = 1.2; e_w, e_h = 160, 160
        queue.append([e_type, hp, espeed, e_w, e_h])
    return queue

def spawn_one(entry, enemies, SCREEN_W, SCREEN_H):
    side = random.choice(['T', 'B', 'L', 'R'])
    # Calcolo coordinata X
    if side in ['T', 'B']:
        ex = random.randint(0, SCREEN_W)
    else:
        if side == 'L':
            ex = 0
        else:
            ex = SCREEN_W

    # Calcolo coordinata Y
    if side in ['L', 'R']:
        ey = random.randint(0, SCREEN_H)
    else:
        if side == 'T':
            ey = 0
        else:
            ey = SCREEN_H
    enemies.append([ex, ey, entry[1], entry[0], entry[3], entry[4], 0.0, entry[2]])

def main() -> None:
    pygame.init()
    
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Phoenix Quest - Defend the Shrine")
    clock = pygame.time.Clock()

    # --- COSTANTI ---
    FRAME_SIZE_samurai = 256
    ANIM_SPEED  = 0.15
    SPEED_WALK  = 4
    SPEED_RUN   = 8

    # --- COSTANTI ORB ---
    ORB_ORBIT_RADIUS    = 80
    ORB_RADIUS          = 12
    ORB_SPEED           = 2.5
    ORB_DAMAGE          = 50
    ORB_DAMAGE_COOLDOWN = 30

    # --- COSTANTI COLTELLI ---
    KNIFE_SPEED    = 12
    KNIFE_DAMAGE   = 25
    KNIFE_COOLDOWN = 18
    KNIFE_LENGTH   = 18
    KNIFE_WIDTH    = 3

    # --- COSTANTI ORDE ---
    PAUSE_DURATION = 4000
    SPAWN_INTERVAL = 400

    # --- CARICAMENTO ASSET ---
    backstage = pygame.image.load("arenaRettangolare.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))
    
    shrine_75 = pygame.image.load("tempio75hpRifilato.png").convert_alpha()
    shrine_75 = pygame.transform.scale(shrine_75, (int(shrine_75.get_width()*0.5), int(shrine_75.get_height()*0.5)))
    shrine_rect = shrine_75.get_rect(center = (SCREEN_W//2, SCREEN_H//2))

    shrine_100 = load_shrine_state("tempio1nosfondo.png", shrine_rect)
    shrine_50 = load_shrine_state("tempio50hpRifilato.png", shrine_rect)
    shrine_25 = load_shrine_state("tempio25hpRifilato.png", shrine_rect)
    shrine_0  = load_shrine_state("tempio0hpRifilato.png", shrine_rect)

    def get_shrine_img(hp):
        if   hp > 75:
            return shrine_100
        elif hp > 50:
            return shrine_75
        elif hp > 25:
            return shrine_50
        elif hp > 0:
            return shrine_25
        else:
            return shrine_0
    
    # --- CARICAMENTO SAMURAI ---
    # --- CARICAMENTO SAMURAI ---
    frames_idle_right = get_samurai_frames("Samurai-idle-v1.png", FRAME_SIZE_samurai)
    frames_idle_left = []
    for f in frames_idle_right:
        frames_idle_left.append(pygame.transform.flip(f, True, False))

    frames_walk_up    = get_samurai_frames("SamuraiUpgiusto.png", FRAME_SIZE_samurai)
    frames_walk_down  = get_samurai_frames("SamuraiDowngiusto.png", FRAME_SIZE_samurai)
    frames_walk_right = get_samurai_frames("SamuraiDxgiusto.png", FRAME_SIZE_samurai)

    frames_walk_left = []
    for f in frames_walk_right:
        frames_walk_left.append(pygame.transform.flip(f, True, False))

    frames_run_up    = get_samurai_frames("SamuraiRunUpgiusto.png", FRAME_SIZE_samurai)
    frames_run_down  = get_samurai_frames("SamuraiRunDowngiusto.png", FRAME_SIZE_samurai)
    frames_run_right = get_samurai_frames("SamuraiRunDxgiusto.png", FRAME_SIZE_samurai)

    frames_run_left = []
    for f in frames_run_right:
        frames_run_left.append(pygame.transform.flip(f, True, False))

        # --- CARICAMENTO NEMICI ---
        slime_sheet = pygame.image.load("SlimeSpriteSheet.png").convert_alpha()
        frames_slime = rescale_frames(load_frames(slime_sheet, 1, 4, 32, 32), 2.5)
        
        dragon_sheet        = pygame.image.load("Baby_Dragon_2D.png").convert_alpha()
        frames_dragon_left  = rescale_frames(load_frames(dragon_sheet, 2, 2, 64, 64), 2.5)
        frames_dragon_right = []
    for f in frames_dragon_left:
    # Ribalto orizzontalmente (True) e non verticalmente (False)
        frame_specchiato = pygame.transform.flip(f, True, False)
        frames_dragon_right.append(frame_specchiato)

    # --- STATO ORDE ---
    wave_state   = "WAVE_SPAWN"
    current_wave = 1
    spawn_queue  = build_spawn_queue(calcola_orda(current_wave))
    spawn_timer  = 0
    pause_timer  = 0

    # --- VARIABILI DI GIOCO ---
    shrine_max_hp, shrine_current_hp = 100.0, 100.0
    px, py      = SCREEN_W // 2, SCREEN_H // 2
    side_pg     = 'R'
    frame_index = 0.0
    current_frames = frames_idle_right

    # --- STATO ORB ---
    orb_angle         = 0.0
    orb_hit_cooldowns = []

    # --- STATO COLTELLI ---
    knives      = []
    knife_timer = 0

    enemies = []

    font_health = pygame.font.Font(None, 36)
    font_wave   = pygame.font.Font(None, 72)
    font_small  = pygame.font.Font(None, 30)
    running     = True
    game_over   = False

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not game_over:
            keys       = pygame.key.get_pressed()
            is_walking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            speed      = SPEED_WALK if is_walking else SPEED_RUN
            moved      = False

            # --- MOVIMENTO ---
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                py -= speed; current_frames = frames_walk_up if is_walking else frames_run_up; moved = True
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                py += speed; current_frames = frames_walk_down if is_walking else frames_run_down; moved = True
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                px -= speed; side_pg = 'L'; current_frames = frames_walk_left if is_walking else frames_run_left; moved = True
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                px += speed; side_pg = 'R'; current_frames = frames_walk_right if is_walking else frames_run_right; moved = True

            if not moved:
                current_frames = frames_idle_right if side_pg == 'R' else frames_idle_left

            anim_speed = ANIM_SPEED if is_walking else ANIM_SPEED * 1.5
            frame_index += anim_speed
            if frame_index >= len(current_frames):
                frame_index = 0

            px = max(90,  min(px, SCREEN_W - 218))
            py = max(75,  min(py, SCREEN_H - 218))

            # --- LANCIO COLTELLI ---
            if knife_timer > 0:
                knife_timer -= 1
            if pygame.mouse.get_pressed()[0] and knife_timer == 0:
                knife_timer = KNIFE_COOLDOWN
                pg_cx = px + 64; pg_cy = py + 64
                mx, my = pygame.mouse.get_pos()
                angle  = math.atan2(my - pg_cy, mx - pg_cx)
                if mx < pg_cx:
                    side_pg = 'L'
                else:
                    side_pg = 'R'
                vx = math.cos(angle) * KNIFE_SPEED
                vy = math.sin(angle) * KNIFE_SPEED
                surf = make_knife_surface(angle, KNIFE_LENGTH, KNIFE_WIDTH)
                hs   = surf.get_width() // 2
                knives.append([pg_cx, pg_cy, vx, vy, surf, hs])

            # --- AGGIORNA ORB ---
            #calcolo angolazione della orb
            orb_angle += ORB_SPEED * (dt / 1000.0)
            #centro del personaggio
            pg_cx = px + 64; pg_cy = py + 64
            orb_positions = []
            
            for i in range(2):
                #i = 0 -> 0° prima orb
                #i = 1 -> 180° seconda orb, diametralmente opposta
                #math.cos(angolo): Ci dice quanto dobbiamo spostarci a DESTRA o SINISTRA dal centro, in proporzione
                #math.sin(angolo): Ci dice quanto dobbiamo spostarci in ALTO o BASSO dal centro, in proporzione
                #*ORB_ORBIT_RADIUS moltiplica il valore trovato con sin e cos per il raggio, lo allunga
                orb_positions.append((pg_cx + math.cos(orb_angle + i * math.pi) * ORB_ORBIT_RADIUS, pg_cy + math.sin(orb_angle + i * math.pi) * ORB_ORBIT_RADIUS))
            
            
            #orb_hit_cooldowns: un nemico deve aspettare un tot per essere colpito nuovamente dalla orb
            # Creiamo una nuova lista tenendo solo chi ha ancora un timer attivo
            new_orb_hit_cooldowns = []
            for entry in orb_hit_cooldowns:
                entry[1] -= 1  # Abbassa il timer (che è in posizione 1)
                if entry[1] > 0: #lo teniamo solo se ancora deve scontare tempo [elimina chi ha timer nullo]
                    new_orb_hit_cooldowns.append(entry)
                orb_hit_cooldowns = new_orb_hit_cooldowns

            # --- AGGIORNA COLTELLI ---
            for k in knives.copy():
                k[0] += k[2]; k[1] += k[3]
                if k[0] < -60 or k[0] > SCREEN_W+60 or k[1] < -60 or k[1] > SCREEN_H+60:
                    knives.remove(k)

            # --- MACCHINA A STATI ORDE ---
            if wave_state == "WAVE_SPAWN":
                spawn_timer += dt
                if spawn_timer >= SPAWN_INTERVAL and spawn_queue:
                    spawn_timer = 0
                    spawn_one(spawn_queue.pop(0), enemies, SCREEN_W, SCREEN_H)
                if not spawn_queue:
                    wave_state = "WAVE_ACTIVE"

            elif wave_state == "WAVE_ACTIVE":
                if len(enemies) == 0:
                    wave_state = "WAVE_PAUSE"
                    pause_timer = 0

            elif wave_state == "WAVE_PAUSE":
                pause_timer += dt
                if pause_timer >= PAUSE_DURATION:
                    current_wave += 1
                    spawn_queue  = build_spawn_queue(calcola_orda(current_wave))
                    spawn_timer  = 0
                    wave_state   = "WAVE_SPAWN"

            # --- DISEGNO SFONDO ---
            screen.blit(backstage, (0, 0))
            shrine_img = get_shrine_img(shrine_current_hp)
            screen.blit(shrine_img, (shrine_rect.x, shrine_rect.y + (shrine_75.get_height() - shrine_img.get_height()) ))
            
            # --- LOGICA NEMICI ---
            for enemy in enemies.copy():
                #coordinate centro del nemico
                ecx = enemy[0] + enemy[4] / 2
                ecy = enemy[1] + enemy[5] / 2
                
                #dist6anza del nemico dallo shrine
                dx   = shrine_rect.centerx - enemy[0]
                dy   = shrine_rect.centery - enemy[1]
                dist = math.hypot(dx, dy)

                if dist > 60:
                    enemy[0] += (dx / dist) * enemy[7]
                    enemy[1] += (dy / dist) * enemy[7]
                else:
                    shrine_current_hp -= 0.05
                
                #animazione dei nemici
                enemy[6] += 0.15
                if enemy[6] >= 4:
                    enemy[6] = 0

                # Collisione ORB
                #id è l'identificativo del preciso slime nella memoria stesso del computer(RAM) tipo (1465367)
                eid = id(enemy)
                 # Controlliamo se il nemico è "in punizione"
                gia_colpito = False
                for entry in orb_hit_cooldowns:
                    #entry contiene l'id del nemico e il tempo che deve scontare
                    if entry[0] == eid:
                        gia_colpito = True
                        break

                if not gia_colpito:
                    for (ox, oy) in orb_positions:
                        #se sono nel raggio delle orbe
                        if math.hypot(ox - ecx, oy - ecy) < ORB_RADIUS + max(enemy[4], enemy[5]) / 2:
                            #riduzione hp nemico [enemy2]
                            enemy[2] -= ORB_DAMAGE
                            # Aggiungiamo il nemico alla lista con il suo timer
                            orb_hit_cooldowns.append([eid, ORB_DAMAGE_COOLDOWN])
                            #break per evitare il 'doppio danno' (se entrambe le orb toccano il nemico)
                            break
                    

                #rettangolo del nemico
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[4], enemy[5])
                
                # Collisione COLTELLI
                for k in knives.copy():
                    knife_rect = pygame.Rect(k[0]-k[5], k[1]-k[5], k[5]*2, k[5]*2)
                    if enemy_rect.colliderect(knife_rect):
                        enemy[2] -= KNIFE_DAMAGE
                        if k in knives:
                            knives.remove(k)
                        break

                if enemy[2] <= 0 and enemy in enemies:
                    enemies.remove(enemy)
            
            #controllo del game over
            if shrine_current_hp <= 0:
                shrine_current_hp = 0
                game_over = True

            # --- DISEGNO COLTELLI ---
            for k in knives:
                screen.blit(k[4], (int(k[0]) - k[5], int(k[1]) - k[5]))

            # --- DISEGNO NEMICI ---
            for e in enemies:
                if e[3] == 'slime':
                    img = frames_slime[int(e[6]) % 4]
                else:
                    img = frames_dragon_right[int(e[6]) % 4] if e[0] < SCREEN_W//2 else frames_dragon_left[int(e[6]) % 4]
                screen.blit(img, (e[0], e[1]))

            # --- DISEGNO SAMURAI ---
            screen.blit(current_frames[int(frame_index) % len(current_frames)], (px, py))

            # --- DISEGNO ORB ---
             for (ox, oy) in orb_positions:
                #disegno della trasparenza
                #glow è una superficie che supporta la trasparenza, su di essa ci disegniamo un cerchio doppio della orb
                glow = pygame.Surface((ORB_RADIUS*4, ORB_RADIUS*4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 210, 0, 70), (ORB_RADIUS*2, ORB_RADIUS*2), ORB_RADIUS*2)
                screen.blit(glow, (int(ox) - ORB_RADIUS*2, int(oy) - ORB_RADIUS*2))
                #disegno del nucleo della orb
                pygame.draw.circle(screen, (255, 220, 0),   (int(ox), int(oy)), ORB_RADIUS)
                #disegno del cerchio bianco 'punto di luce', leggermente in alto a sinistra
                pygame.draw.circle(screen, (255, 255, 210), (int(ox)-3, int(oy)-3), ORB_RADIUS//3)
                
        # --- UI ---
        pygame.draw.rect(screen, (50, 50, 50),  (SCREEN_W//2-150, 30, 300, 20))
        pygame.draw.rect(screen, (0, 200, 255), (SCREEN_W//2-150, 30, (shrine_current_hp/shrine_max_hp)*300, 20))
        txt = font_health.render(f"SHRINE HP: {int(shrine_current_hp)}", True, (255,255,255))
        screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 55))

        wave_txt = font_small.render(f"WAVE  {current_wave}", True, (255, 220, 80))
        screen.blit(wave_txt, (20, 20))

        if wave_state == "WAVE_ACTIVE":
            rem_txt = font_small.render(f"Nemici: {len(enemies)}", True, (220, 220, 220))
            screen.blit(rem_txt, (20, 48))

        if wave_state == "WAVE_PAUSE":
            seconds_left = max(1, int((PAUSE_DURATION - pause_timer) / 1000) + 1)
            ann = font_wave.render(f"WAVE  {current_wave + 1}  in  {seconds_left}...", True, (255, 230, 60))
            screen.blit(ann, (SCREEN_W//2 - ann.get_width()//2, SCREEN_H//2 - 40))

        if game_over:
            over_txt = font_health.render("SHRINE DESTROYED! ESC to Quit", True, (255,50,50))
            screen.blit(over_txt, (SCREEN_W//2 - over_txt.get_width()//2, SCREEN_H//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()