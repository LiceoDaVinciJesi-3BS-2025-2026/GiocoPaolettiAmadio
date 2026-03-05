import pygame
import sys
import math
import random
import datetime
import os

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
            
    #aggiungo le informazioni sul nemico alla lista completa
    #0-1. coordinate del nemico
    #2. hp del nemico
    #3. tipologia nemico
    #4-5. larghezza/altezza nemico 
    #6. frame index
    #7. velocità di movimento
    #8. contatore anim. danno
    enemies.append([ex, ey, entry[1], entry[0], entry[3], entry[4], 0.0, entry[2], 0])
    
CLASSIFICA_FILE = "classifica.txt"

def salva_partita(nickname, wave, nemici, durata_sec, coltelli):
    """Aggiunge una riga al file classifica.txt"""
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    minuti = int(durata_sec // 60)
    secondi = int(durata_sec % 60)
    riga = f"{data} | {nickname:<12} | Wave: {wave:>3} | Nemici: {nemici:>4} | Durata: {minuti:02d}:{secondi:02d} | Coltelli: {coltelli:>4}\n"
    with open(CLASSIFICA_FILE, "a", encoding="utf-8") as f:
        f.write(riga)

def carica_classifica(max_righe=8):
    """Legge le ultime max_righe dal file classifica"""
    if not os.path.exists(CLASSIFICA_FILE):
        return []
    with open(CLASSIFICA_FILE, "r", encoding="utf-8") as f:
        righe = f.readlines()
    return [r.rstrip("\n") for r in righe[-max_righe:]]

#---------------------------------------------------------------------------------------#
#funzione run del gioco

def main() -> None:
    pygame.init()
    
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Crimson Guard")
    clock = pygame.time.Clock()

    # ================== SCHERMATA INIZIALE (caricata una volta sola) ==================
    start_screen_img = pygame.image.load("materiali\Crimsonguard.png").convert_alpha()
    start_screen_img = pygame.transform.scale(start_screen_img, (SCREEN_W, SCREEN_H))
    START_BUTTON_RECT = pygame.Rect(522, 600, 300, 90)

    # --- COSTANTI PERSONAGGIO ---
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
    ORB_NUM = 3

    # --- COSTANTI COLTELLI ---
    KNIFE_SPEED    = 12
    KNIFE_DAMAGE   = 25
    KNIFE_COOLDOWN = 18
    KNIFE_LENGTH   = 18
    KNIFE_WIDTH    = 3
    KNIFE_MAX_RANGE = 300
    
    # --- COSTANTI ORDE ---
    PAUSE_DURATION = 4000
    SPAWN_INTERVAL = 400
    
    # --- COSTANTI IN GIOCO ---
    HIT_FLASH_DURATION = 8

    # --- CARICAMENTO ASSET (una volta sola) ---
    backstage = pygame.image.load("materiali\StageRettangolare.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))
    
    shrine_75 = pygame.image.load("materiali\Tempio75hpRifilato.png").convert_alpha()
    shrine_75 = pygame.transform.scale(shrine_75, (int(shrine_75.get_width()*0.5), int(shrine_75.get_height()*0.5)))
    shrine_rect = shrine_75.get_rect(center = (SCREEN_W//2, SCREEN_H//2))

    shrine_100 = load_shrine_state("materiali\Tempio1nosfondo.png", shrine_rect)
    shrine_50  = load_shrine_state("materiali\Tempio50hpRifilato.png", shrine_rect)
    shrine_25  = load_shrine_state("materiali\Tempio25hpRifilato.png", shrine_rect)
    shrine_0   = load_shrine_state("materiali\Tempio0hpRifilato.png", shrine_rect)

    def get_shrine_img(hp):
        if   hp > 75: return shrine_100
        elif hp > 50: return shrine_75
        elif hp > 25: return shrine_50
        elif hp > 0:  return shrine_25
        return shrine_0

    # --- CARICAMENTO SAMURAI ---
    frames_idle_right = get_samurai_frames("materiali\Samurai-idle-v1.png", FRAME_SIZE_samurai)
    frames_idle_left  = [pygame.transform.flip(f, True, False) for f in frames_idle_right]

    frames_walk_up    = get_samurai_frames("materiali\SamuraiUpgiusto.png",   FRAME_SIZE_samurai)
    frames_walk_down  = get_samurai_frames("materiali\SamuraiDowngiusto.png", FRAME_SIZE_samurai)
    frames_walk_right = get_samurai_frames("materiali\SamuraiDxgiusto.png",   FRAME_SIZE_samurai)
    frames_walk_left  = [pygame.transform.flip(f, True, False) for f in frames_walk_right]

    frames_run_up    = get_samurai_frames("materiali\SamuraiRunUpgiusto.png",   FRAME_SIZE_samurai)
    frames_run_down  = get_samurai_frames("materiali\SamuraiRunDowngiusto.png", FRAME_SIZE_samurai)
    frames_run_right = get_samurai_frames("materiali\SamuraiRunDxgiusto.png",   FRAME_SIZE_samurai)
    frames_run_left  = [pygame.transform.flip(f, True, False) for f in frames_run_right]

    # --- CARICAMENTO NEMICI ---
    slime_sheet  = pygame.image.load("materiali\SlimeSpriteSheet.png").convert_alpha()
    frames_slime = rescale_frames(load_frames(slime_sheet, 1, 4, 32, 32), 2.5)

    dragon_sheet        = pygame.image.load("materiali\Baby_Dragon_2D.png").convert_alpha()
    frames_dragon_left  = rescale_frames(load_frames(dragon_sheet, 2, 2, 64, 64), 2.5)
    frames_dragon_right = [pygame.transform.flip(f, True, False) for f in frames_dragon_left]

    font_health = pygame.font.Font(None, 36)
    font_wave   = pygame.font.Font(None, 72)
    font_small  = pygame.font.Font(None, 30)

    # ==================================================================================
    # LOOP ESTERNO: schermata iniziale → partita → game over → torna all'inizio
    # ==================================================================================
    while True:

        # ================== SCHERMATA INIZIALE ==================
        in_start_screen = True
        while in_start_screen:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if START_BUTTON_RECT.collidepoint(event.pos):
                        in_start_screen = False
            screen.blit(start_screen_img, (0, 0))
            pygame.display.flip()

        # ================== INIT VARIABILI DI GIOCO ==================
        wave_state   = "WAVE_SPAWN"
        current_wave = 1
        spawn_queue  = build_spawn_queue(calcola_orda(current_wave))
        spawn_timer  = 0
        pause_timer  = 0

        shrine_max_hp, shrine_current_hp = 100.0, 100.0
        px, py         = SCREEN_W // 2, SCREEN_H // 2
        side_pg        = 'R'
        frame_index    = 0.0
        current_frames = frames_idle_right

        orb_angle         = 0.0
        orb_hit_cooldowns = []
        orb_positions     = []

        knives      = []
        knife_timer = 0

        enemies   = []
        running   = True
        game_over = False

        # --- STATISTICHE PARTITA ---
        nemici_uccisi  = 0
        coltelli_sparati = 0
        tempo_inizio   = pygame.time.get_ticks()

        # ================== LOOP PRINCIPALE ==================
        while running:
            dt = clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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
                    knives.append([pg_cx, pg_cy, vx, vy, surf, hs, 0])
                    coltelli_sparati += 1

                
                # --- AGGIORNA ORB ---
            #calcolo angolazione della orb
            orb_angle += ORB_SPEED * (dt / 1000.0)
            #centro del personaggio
            pg_cx = px + 64
            pg_cy = py + 64
            orb_positions = []
            
            for i in range(ORB_NUM):
                #dividiamo il cerchio in tanti angoli congruenti  quante sono le orbe
                angs_equi = 2 * math.pi / ORB_NUM
                #per ogni orb diversa, aggiungo l'angolo congruente all'angolo attuale delle orb
                #math.cos(angolo): Ci dice quanto dobbiamo spostarci a DESTRA o SINISTRA dal centro, in proporzione
                orb_dist_x = math.cos(orb_angle + i * angs_equi) * ORB_ORBIT_RADIUS
                #math.sin(angolo): Ci dice quanto dobbiamo spostarci in ALTO o BASSO dal centro, in proporzione
                orb_dist_y = math.sin(orb_angle + i * angs_equi) * ORB_ORBIT_RADIUS
                #*ORB_ORBIT_RADIUS moltiplica il valore trovato con sin e cos per il raggio, lo allunga
                #aggiungiamo le coordinate rispetto al centro del personaggio, pg_cx e pg_cy
                orb_positions.append((pg_cx + orb_dist_x, pg_cy + orb_dist_y))
            

                new_orb_hit_cooldowns = []
                for entry in orb_hit_cooldowns:
                    entry[1] -= 1
                    if entry[1] > 0:
                        new_orb_hit_cooldowns.append(entry)
                orb_hit_cooldowns = new_orb_hit_cooldowns

                # --- AGGIORNA COLTELLI ---
                for k in knives.copy():
                    k[0] += k[2]
                    k[1] += k[3]
                    k[6] += KNIFE_SPEED
                    if k[0] < -60 or k[0] > SCREEN_W+60 or k[1] < -60 or k[1] > SCREEN_H+60 or k[6] >= KNIFE_MAX_RANGE:
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
                        wave_state  = "WAVE_PAUSE"
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
                screen.blit(shrine_img, (shrine_rect.x, shrine_rect.y + (shrine_75.get_height() - shrine_img.get_height())))

                # --- LOGICA NEMICI ---
                for enemy in enemies.copy():
                    ecx = enemy[0] + enemy[4] / 2
                    ecy = enemy[1] + enemy[5] / 2

                    dx   = shrine_rect.centerx - ecx
                    dy   = shrine_rect.centery - ecy
                    dist = math.hypot(dx, dy)

                    if dist > 60:
                        enemy[0] += (dx / dist) * enemy[7]
                        enemy[1] += (dy / dist) * enemy[7]
                    else:
                        shrine_current_hp -= 0.05

                    enemy[6] += 0.15
                    if enemy[6] >= 4:
                        enemy[6] = 0

                    # Collisione ORB
                    eid = id(enemy)
                    gia_colpito = False
                    for entry in orb_hit_cooldowns:
                        if entry[0] == eid:
                            gia_colpito = True
                            break

                    if not gia_colpito:
                        for (ox, oy) in orb_positions:
                            if math.hypot(ox - ecx, oy - ecy) < ORB_RADIUS + max(enemy[4], enemy[5]) / 2:
                                enemy[2] -= ORB_DAMAGE
                                enemy[8]  = HIT_FLASH_DURATION
                                orb_hit_cooldowns.append([eid, ORB_DAMAGE_COOLDOWN])
                                break

                    enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[4], enemy[5])

                    # Collisione COLTELLI
                    for k in knives.copy():
                        knife_rect = pygame.Rect(k[0]-k[5], k[1]-k[5], k[5]*2, k[5]*2)
                        if enemy_rect.colliderect(knife_rect):
                            enemy[2] -= KNIFE_DAMAGE
                            enemy[8]  = HIT_FLASH_DURATION
                            if k in knives:
                                knives.remove(k)
                            break

                    if enemy[2] <= 0 and enemy in enemies:
                        enemies.remove(enemy)
                        nemici_uccisi += 1

                # Controllo game over
                if shrine_current_hp <= 0:
                    shrine_current_hp = 0
                    running   = False
                    game_over = True
                    durata_sec = (pygame.time.get_ticks() - tempo_inizio) / 1000.0

                # --- DISEGNO COLTELLI ---
                for k in knives:
                    screen.blit(k[4], (int(k[0]) - k[5], int(k[1]) - k[5]))

                # --- DISEGNO NEMICI ---
                for e in enemies:
                    if e[3] == 'slime':
                        img = frames_slime[int(e[6]) % 4]
                    else:
                        if e[0] < SCREEN_W//2:
                            img = frames_dragon_right[int(e[6]) % 4]
                        else:
                            img = frames_dragon_left[int(e[6]) % 4]

                    screen.blit(img, (e[0], e[1]))

                    if e[8] > 0:
                        e[8] -= 1
                        red_overlay = img.copy()
                        red_overlay.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
                        screen.blit(red_overlay, (e[0], e[1]))

                # --- DISEGNO SAMURAI ---
                screen.blit(current_frames[int(frame_index) % len(current_frames)], (px, py))

                # --- DISEGNO ORB ---
                for (ox, oy) in orb_positions:
                    glow = pygame.Surface((ORB_RADIUS*4, ORB_RADIUS*4), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (255, 210, 0, 70), (ORB_RADIUS*2, ORB_RADIUS*2), ORB_RADIUS*2)
                    screen.blit(glow, (int(ox) - ORB_RADIUS*2, int(oy) - ORB_RADIUS*2))
                    pygame.draw.circle(screen, (255, 220, 0),   (int(ox), int(oy)), ORB_RADIUS)
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

            pygame.display.flip()

        # ================== GAME OVER: inserimento nickname ==================
        nickname       = ""
        salvato        = False
        classifica     = []
        inserimento_ok = False  # diventa True dopo INVIO

        while game_over:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #uscita#
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not inserimento_ok:
                        # --- fase di digitazione nickname ---
                        if event.key == pygame.K_RETURN and nickname.strip():
                            # salva e carica classifica
                            salva_partita(nickname.strip(), current_wave,
                                          nemici_uccisi, durata_sec, coltelli_sparati)
                            classifica     = carica_classifica()
                            inserimento_ok = True
                        elif event.key == pygame.K_BACKSPACE:
                            # --- cancella in inserimento ---
                            nickname = nickname[:-1]
                        else:
                            if len(nickname) < 16 and event.unicode.isprintable():
                                nickname += event.unicode
                    else:
                        # --- fase di visualizzazione risultati ---
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_SPACE:
                            game_over = False  # torna al while True esterno

            # --- DISEGNO SFONDO ---
            screen.blit(backstage, (0, 0))
            shrine_img = get_shrine_img(shrine_current_hp)
            screen.blit(shrine_img, (shrine_rect.x, shrine_rect.y + (shrine_75.get_height() - shrine_img.get_height())))
            screen.blit(current_frames[int(frame_index) % len(current_frames)], (px, py))

            # overlay scuro
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            cx = SCREEN_W // 2

            if not inserimento_ok:
                # --- SCHERMATA INSERIMENTO NICKNAME ---
                over_txt = font_wave.render("SHRINE DESTROYED!", True, (255, 50, 50))
                screen.blit(over_txt, (cx - over_txt.get_width()//2, 80))

                minuti  = int(durata_sec // 60)
                secondi = int(durata_sec % 60)
                stats = [
                    f"Wave raggiunta:   {current_wave}",
                    f"Nemici uccisi:    {nemici_uccisi}",
                    f"Durata partita:   {minuti:02d}:{secondi:02d}",
                    f"Coltelli lanciati: {coltelli_sparati}",
                ]
                for i, riga in enumerate(stats):
                    s = font_health.render(riga, True, (220, 220, 180))
                    screen.blit(s, (cx - s.get_width()//2, 200 + i * 44))

                prompt = font_health.render("Inserisci il tuo nome e premi INVIO:", True, (255, 230, 80))
                screen.blit(prompt, (cx - prompt.get_width()//2, 420))

                # box nickname
                box_rect = pygame.Rect(cx - 180, 465, 360, 44)
                pygame.draw.rect(screen, (60, 60, 80), box_rect, border_radius=6)
                pygame.draw.rect(screen, (200, 200, 100), box_rect, 2, border_radius=6)
                cursore = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
                nick_surf = font_health.render(nickname + cursore, True, (255, 255, 255))
                screen.blit(nick_surf, (box_rect.x + 10, box_rect.y + 8))

            else:
                # --- SCHERMATA CLASSIFICA ---
                titolo = font_wave.render("CLASSIFICA", True, (255, 220, 60))
                screen.blit(titolo, (cx - titolo.get_width()//2, 40))

                # statistiche ultima partita (riquadro a sinistra)
                minuti  = int(durata_sec // 60)
                secondi = int(durata_sec % 60)
                tua_txt = font_health.render("La tua partita:", True, (180, 220, 255))
                screen.blit(tua_txt, (80, 130))
                stats = [
                    f"Nickname:          {nickname.strip()}",
                    f"Wave raggiunta:    {current_wave}",
                    f"Nemici uccisi:     {nemici_uccisi}",
                    f"Durata:            {minuti:02d}:{secondi:02d}",
                    f"Coltelli lanciati: {coltelli_sparati}",
                ]
                i = 0
                for riga in stats:
                    s = font_small.render(riga, True, (210, 210, 210))
                    screen.blit(s, (80, 165 + i * 32))
                    i += 1
                    
                # separatore verticale
                pygame.draw.line(screen, (120, 120, 120), (cx - 320, 120), (cx - 320, SCREEN_H - 80), 1)

                # ultime partite (colonna destra)
                storico_txt = font_health.render("Ultime partite:", True, (180, 220, 255))
                screen.blit(storico_txt, (cx -300, 130))
                i = 0
                for riga in classifica:
                    #se il nickname del giocatore è già presente, evidenzio le partite in giallo. altrimenti è grigio
                    if nickname.strip() in riga:
                        colore = (255, 255, 100)
                    else:
                        colore = (200, 200, 200)
                        
                    s = font_small.render(riga, True, colore)
                    screen.blit(s, (cx - 300, 165 + i * 34))
                    i += 1
                    

                # istruzioni
                hint = font_small.render("SPAZIO per ricominciare  |  ESC per uscire", True, (160, 160, 160))
                screen.blit(hint, (cx - hint.get_width()//2, SCREEN_H - 50))

            pygame.display.flip()

        # game_over == False → il while True esterno riparte dalla schermata iniziale


# --- AVVIO ---
if __name__ == "__main__":
    main()