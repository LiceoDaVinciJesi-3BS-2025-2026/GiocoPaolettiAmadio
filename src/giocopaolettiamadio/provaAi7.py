def main() -> None:
    import pygame
    import sys
    import math
    import random
    pygame.init()
    
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Phoenix Quest - Defend the Shrine")
    clock = pygame.time.Clock()
    
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
    PAUSE_DURATION = 4000   # ms di pausa tra un'orda e la prossima
    SPAWN_INTERVAL = 400    # ms tra uno spawn e il successivo dentro l'orda

    # --- CARICAMENTO ASSET ---
    backstage = pygame.image.load("arenaRettangolare.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))
    
    shrine_img = pygame.image.load("Adobe Express - file (1).png").convert_alpha()
    shrine_img = pygame.transform.scale(shrine_img, (int(shrine_img.get_width()*0.6), int(shrine_img.get_height()*0.6)))
    shrine_rect = shrine_img.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
    
    # --- CARICAMENTO SAMURAI ---
    def get_samurai_frames(filename):
        sheet = pygame.image.load(filename).convert_alpha()
        return rescale_frames(load_frames(sheet, 5, 5, FRAME_SIZE_samurai), 0.5)

    frames_idle_right = get_samurai_frames("Samurai-idle-v1.png")
    frames_idle_left  = [pygame.transform.flip(f, True, False) for f in frames_idle_right]
    frames_walk_up    = get_samurai_frames("SamuraiUpgiusto.png")
    frames_walk_down  = get_samurai_frames("SamuraiDowngiusto.png")
    frames_walk_right = get_samurai_frames("SamuraiDxgiusto.png")
    frames_walk_left  = [pygame.transform.flip(f, True, False) for f in frames_walk_right]
    frames_run_up     = get_samurai_frames("SamuraiRunUpgiusto.png")
    frames_run_down   = get_samurai_frames("SamuraiRunDowngiusto.png")
    frames_run_right  = get_samurai_frames("SamuraiRunDxgiusto.png")
    frames_run_left   = [pygame.transform.flip(f, True, False) for f in frames_run_right]

    # --- CARICAMENTO NEMICI ---
    slime_sheet = pygame.image.load("SlimeSpriteSheet.png").convert_alpha()
    frames_slime = rescale_frames(load_frames(slime_sheet, 1, 4, 32, 32), 2.5)
    
    dragon_sheet        = pygame.image.load("Baby_Dragon_2D.png").convert_alpha()
    frames_dragon_left  = rescale_frames(load_frames(dragon_sheet, 2, 2, 64, 64), 2.5)
    frames_dragon_right = [pygame.transform.flip(f, True, False) for f in frames_dragon_left]

    # --- CREA SURFACE COLTELLO ---
    def make_knife_surface(angle_rad):
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

    # ---------------------------------------------------------------------------
    # SISTEMA ORDE
    # ---------------------------------------------------------------------------
    def calcola_orda(wave_num):
        """Restituisce i parametri di difficoltà scalati per l'onda corrente."""
        totale     = 4 + (wave_num - 1) * 2          # onda 1→4, onda 2→6, ecc.
        prob_dragon = min(0.1 + (wave_num - 1) * 0.1, 0.7)  # cresce fino al 70%
        hp_mult    = 1.0 + (wave_num - 1) * 0.2      # onda 1→x1.0, onda 3→x1.4
        return {"totale": totale, "prob_dragon": prob_dragon, "hp_mult": hp_mult}

    def build_spawn_queue(params):
        """Prepara la lista di nemici da spawnare per questa onda."""
        queue = []
        for _ in range(params["totale"]):
            e_type = 'dragon' if random.random() < params["prob_dragon"] else 'slime'
            if e_type == 'slime':
                hp = int(30 * params["hp_mult"]); espeed = 2.0; e_w, e_h = 80,  80
            else:
                hp = int(50 * params["hp_mult"]); espeed = 1.2; e_w, e_h = 160, 160
            queue.append({"type": e_type, "hp": hp, "speed": espeed, "w": e_w, "h": e_h})
        return queue

    def spawn_one(entry):
        """Spawna un singolo nemico da un bordo casuale dello schermo."""
        side = random.choice(['T', 'B', 'L', 'R'])
        ex = random.randint(0, SCREEN_W) if side in ['T', 'B'] else (0 if side == 'L' else SCREEN_W)
        ey = random.randint(0, SCREEN_H) if side in ['L', 'R'] else (0 if side == 'T' else SCREEN_H)
        enemies.append([ex, ey, entry["hp"], entry["type"], entry["w"], entry["h"], 0.0, entry["speed"]])

    # Stato iniziale macchina a stati
    wave_state   = "WAVE_SPAWN"
    current_wave = 1
    spawn_queue  = build_spawn_queue(calcola_orda(current_wave))
    spawn_timer  = 0
    pause_timer  = 0
    # ---------------------------------------------------------------------------

    # --- VARIABILI DI GIOCO ---
    shrine_max_hp, shrine_current_hp = 100.0, 100.0
    px, py      = SCREEN_W // 2, SCREEN_H // 2
    side_pg     = 'R'
    frame_index = 0.0
    current_frames = frames_idle_right

    # --- STATO ORB ---
    orb_angle         = 0.0
    orb_hit_cooldowns = {}

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
                py += speed; current_frames = frames_walk_down_down if is_walking else frames_run_down; moved = True
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                px -= speed; side_pg = 'L'; current_frames = frames_walk_left if is_walking else frames_run_left; moved = True
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                px += speed; side_pg = 'R'; current_frames = frames_walk_right if is_walking else frames_run_right; moved = True

            if not moved:
                current_frames = frames_idle_right if side_pg == 'R' else frames_idle_left

            anim_speed = ANIM_SPEED  if is_walking else ANIM_SPEED * 1.5
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
                side_pg = 'L' if mx < pg_cx else 'R'
                vx = math.cos(angle) * KNIFE_SPEED
                vy = math.sin(angle) * KNIFE_SPEED
                surf = make_knife_surface(angle)
                hs   = surf.get_width() // 2
                knives.append([pg_cx, pg_cy, vx, vy, surf, hs])

            # --- AGGIORNA ORB ---
            orb_angle += ORB_SPEED * (dt / 1000.0)
            pg_cx = px + 64; pg_cy = py + 64
            orb_positions = [
                (pg_cx + math.cos(orb_angle + i * math.pi) * ORB_ORBIT_RADIUS,
                 pg_cy + math.sin(orb_angle + i * math.pi) * ORB_ORBIT_RADIUS)
                for i in range(2)
            ]
            for eid in list(orb_hit_cooldowns):
                orb_hit_cooldowns[eid] -= 1
                if orb_hit_cooldowns[eid] <= 0:
                    del orb_hit_cooldowns[eid]

            # --- AGGIORNA COLTELLI ---
            for k in knives.copy():
                k[0] += k[2]; k[1] += k[3]
                if k[0] < -60 or k[0] > SCREEN_W+60 or k[1] < -60 or k[1] > SCREEN_H+60:
                    knives.remove(k)

            # -------------------------------------------------------------------
            # MACCHINA A STATI ORDE
            # -------------------------------------------------------------------
            if wave_state == "WAVE_SPAWN":
                # Spawna un nemico dalla coda ogni SPAWN_INTERVAL ms
                spawn_timer += dt
                if spawn_timer >= SPAWN_INTERVAL and spawn_queue:
                    spawn_timer = 0
                    spawn_one(spawn_queue.pop(0))
                # Quando la coda è vuota tutti i nemici sono stati immessi:
                # passa allo stato attivo
                if not spawn_queue:
                    wave_state = "WAVE_ACTIVE"

            elif wave_state == "WAVE_ACTIVE":
                # L'onda finisce quando non ci sono più nemici vivi
                # NÉ nemici in coda (spawn_queue è già vuota in questo stato)
                if len(enemies) == 0:
                    wave_state = "WAVE_PAUSE"
                    pause_timer = 0

            elif wave_state == "WAVE_PAUSE":
                # Aspetta, poi prepara e avvia l'onda successiva
                pause_timer += dt
                if pause_timer >= PAUSE_DURATION:
                    current_wave += 1
                    spawn_queue  = build_spawn_queue(calcola_orda(current_wave))
                    spawn_timer  = 0
                    wave_state   = "WAVE_SPAWN"
            # -------------------------------------------------------------------

            # --- DISEGNO SFONDO ---
            screen.blit(backstage, (0, 0))
            screen.blit(shrine_img, shrine_rect)

            # --- LOGICA NEMICI ---
            for enemy in enemies.copy():
                dx   = shrine_rect.centerx - enemy[0]
                dy   = shrine_rect.centery - enemy[1]
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
                if eid not in orb_hit_cooldowns:
                    ecx = enemy[0] + enemy[4] / 2
                    ecy = enemy[1] + enemy[5] / 2
                    for (ox, oy) in orb_positions:
                        if math.hypot(ox - ecx, oy - ecy) < ORB_RADIUS + max(enemy[4], enemy[5]) / 2:
                            enemy[2] -= ORB_DAMAGE
                            orb_hit_cooldowns[eid] = ORB_DAMAGE_COOLDOWN
                            break

                # Collisione COLTELLI
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[4], enemy[5])
                for k in knives.copy():
                    knife_rect = pygame.Rect(k[0]-k[5], k[1]-k[5], k[5]*2, k[5]*2)
                    if enemy_rect.colliderect(knife_rect):
                        enemy[2] -= KNIFE_DAMAGE
                        if k in knives:
                            knives.remove(k)
                        break

                if enemy[2] <= 0 and enemy in enemies:
                    enemies.remove(enemy)

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

        # Numero onda (angolo in alto a sinistra)
        wave_txt = font_small.render(f"WAVE  {current_wave}", True, (255, 220, 80))
        screen.blit(wave_txt, (20, 20))

        # Nemici rimasti durante l'onda attiva
        if wave_state == "WAVE_ACTIVE":
            rem_txt = font_small.render(f"Nemici: {len(enemies)}", True, (220, 220, 220))
            screen.blit(rem_txt, (20, 48))

        # Conto alla rovescia tra orde
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