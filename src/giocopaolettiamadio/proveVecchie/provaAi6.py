
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
    ANIM_SPEED = 0.15
    SPEED_WALK = 4
    SPEED_RUN = 8

    # --- COSTANTI ORB ---
    ORB_ORBIT_RADIUS = 80      # distanza dal centro del samurai
    ORB_RADIUS = 12            # raggio visivo del cerchio
    ORB_SPEED = 2.5            # velocità di rotazione (radianti/secondo)
    ORB_DAMAGE = 50           # danno per contatto
    ORB_DAMAGE_COOLDOWN = 30   # frame di pausa tra un danno e l'altro per nemico
    
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
    frames_idle_left = [pygame.transform.flip(f, True, False) for f in frames_idle_right]
    frames_walk_up = get_samurai_frames("SamuraiUpgiusto.png")
    frames_walk_down = get_samurai_frames("SamuraiDowngiusto.png")
    frames_walk_right = get_samurai_frames("SamuraiDxgiusto.png")
    frames_walk_left = [pygame.transform.flip(f, True, False) for f in frames_walk_right]
    frames_run_up = get_samurai_frames("SamuraiRunUpgiusto.png")
    frames_run_down = get_samurai_frames("SamuraiRunDowngiusto.png")
    frames_run_right = get_samurai_frames("SamuraiRunDxgiusto.png")
    frames_run_left = [pygame.transform.flip(f, True, False) for f in frames_run_right]

    # --- CARICAMENTO ANIMAZIONE ATTACCO ---
    def get_attack_frames(filename):
        sheet = pygame.image.load(filename).convert_alpha()
        return rescale_frames(load_frames(sheet, 5, 5, 400), 0.5)

    frames_attack_right = get_attack_frames("sprite-256px-251.png")
    frames_attack_left = [pygame.transform.flip(f, True, False) for f in frames_attack_right]

    # --- CARICAMENTO NEMICI ---
    slime_sheet = pygame.image.load("SlimeSpriteSheet.png").convert_alpha()
    frames_slime = rescale_frames(load_frames(slime_sheet, 1, 4, 32, 32), 2.5)
    
    dragon_sheet = pygame.image.load("Baby_Dragon_2D.png").convert_alpha() 
    frames_dragon_left = rescale_frames(load_frames(dragon_sheet, 2, 2, 64, 64), 2.5)
    frames_dragon_right = [pygame.transform.flip(f, True, False) for f in frames_dragon_left]

    # --- VARIABILI DI GIOCO ---
    shrine_max_hp, shrine_current_hp = 100.0, 100.0
    px, py = SCREEN_W // 2, SCREEN_H // 2
    side_pg = 'R'
    frame_index = 0
    current_frames = frames_idle_right

    # --- STATO ATTACCO ---
    is_attacking = False
    attack_frame = 0.0
    attack_damage_dealt = False
    ATTACK_ANIM_SPEED = 0.35
    ATTACK_TOTAL_FRAMES = len(frames_attack_right)

    # --- STATO ORB ---
    orb_angle = 0.0
    orb_hit_cooldowns = {}   # id(enemy) -> frame di cooldown rimanenti

    enemies = []
    spawn_timer = 0
    wave_size = 3
    
    font_health = pygame.font.Font(None, 36)
    running = True 
    game_over = False

    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not is_attacking:
                    is_attacking = True
                    attack_frame = 0.0
                    attack_damage_dealt = False

        if not game_over:
            keys = pygame.key.get_pressed()
            is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            speed = SPEED_RUN if is_running else SPEED_WALK
            moved = False

            # --- GESTIONE ANIMAZIONE ATTACCO ---
            if is_attacking:
                current_frames = frames_attack_right if side_pg == 'R' else frames_attack_left
                attack_frame += ATTACK_ANIM_SPEED
                if attack_frame >= ATTACK_TOTAL_FRAMES * 0.5 and not attack_damage_dealt:
                    attack_damage_dealt = True
                    for enemy in enemies.copy():
                        dist_to_pg = math.hypot(px + 64 - enemy[0], py + 64 - enemy[1])
                        if dist_to_pg < 120:
                            enemy[2] -= 2
                            if enemy[2] <= 0:
                                enemies.remove(enemy)
                if attack_frame >= ATTACK_TOTAL_FRAMES:
                    is_attacking = False
                    attack_frame = 0.0
                    current_frames = frames_idle_right if side_pg == 'R' else frames_idle_left
                frame_index = attack_frame

            else:
                # --- INPUT E MOVIMENTO ---
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    py -= speed
                    current_frames = frames_run_up if is_running else frames_walk_up
                    moved = True
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    py += speed
                    current_frames = frames_run_down if is_running else frames_walk_down
                    moved = True
                elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    px -= speed
                    side_pg = 'L'
                    current_frames = frames_run_left if is_running else frames_walk_left
                    moved = True
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    px += speed
                    side_pg = 'R'
                    current_frames = frames_run_right if is_running else frames_walk_right
                    moved = True

                if not moved:
                    current_frames = frames_idle_right if side_pg == 'R' else frames_idle_left

                anim_speed = ANIM_SPEED * 1.5 if is_running else ANIM_SPEED
                frame_index += anim_speed
                if frame_index >= len(current_frames):
                    frame_index = 0

            px = max(90, min(px, SCREEN_W - 218))
            py = max(75, min(py, SCREEN_H - 218))

            # --- AGGIORNA ANGOLO ORB ---
            orb_angle += ORB_SPEED * (dt / 1000.0)

            # Centro visivo del samurai
            pg_cx = px + 64
            pg_cy = py + 64

            # Calcola le due posizioni orb (sfasate di 180°)
            orb_positions = []
            for i in range(2):
                angle = orb_angle + i * math.pi
                ox = pg_cx + math.cos(angle) * ORB_ORBIT_RADIUS
                oy = pg_cy + math.sin(angle) * ORB_ORBIT_RADIUS
                orb_positions.append((ox, oy))

            # Decrementa cooldown orb
            for eid in list(orb_hit_cooldowns.keys()):
                orb_hit_cooldowns[eid] -= 1
                if orb_hit_cooldowns[eid] <= 0:
                    del orb_hit_cooldowns[eid]

            # 2. SPAWN NEMICI
            spawn_timer += dt
            if spawn_timer > 3000:
                spawn_timer = 0
                for _ in range(wave_size):
                    side = random.choice(['T', 'B', 'L', 'R'])
                    ex = random.randint(0, SCREEN_W) if side in ['T','B'] else (0 if side=='L' else SCREEN_W)
                    ey = random.randint(0, SCREEN_H) if side in ['L','R'] else (0 if side=='T' else SCREEN_H)
                    e_type = random.choice(['slime', 'dragon'])
                    if e_type == 'slime':
                        hp = 30
                        speed = 2.0
                        e_w = 80
                        e_h = 80
                    elif e_type == 'dragon':
                        hp = 50
                        speed = 1.2
                        e_w = 160
                        e_h = 160
                    enemies.append([ex, ey, hp, e_type, e_w, e_h, 0.0, speed])

            # --- DISEGNO ---
            screen.blit(backstage, (0, 0))
            screen.blit(shrine_img, shrine_rect)

            # 3. LOGICA NEMICI
            for enemy in enemies.copy():
                dx = shrine_rect.centerx - enemy[0]
                dy = shrine_rect.centery - enemy[1]
                dist = math.hypot(dx, dy)
                
                if dist > 60:
                    enemy[0] += (dx / dist) * enemy[-1]
                    enemy[1] += (dy / dist) * enemy[-1]
                else:
                    shrine_current_hp -= 0.05

                enemy[-2] += 0.15
                if enemy[-2] >= (8 if enemy[3] == 'slime' else 4):
                    enemy[-2] = 0

                # --- COLLISIONE ORB → NEMICO ---
                eid = id(enemy)
                if eid not in orb_hit_cooldowns:
                    enemy_cx = enemy[0] + enemy[4] / 2
                    enemy_cy = enemy[1] + enemy[5] / 2
                    for (ox, oy) in orb_positions:
                        dist_orb = math.hypot(ox - enemy_cx, oy - enemy_cy)
                        # soglia = raggio orb + metà dimensione nemico
                        if dist_orb < ORB_RADIUS + max(enemy[4], enemy[5]) / 2:
                            enemy[2] -= ORB_DAMAGE
                            orb_hit_cooldowns[eid] = ORB_DAMAGE_COOLDOWN
                            break

                if enemy[2] <= 0 and enemy in enemies:
                    enemies.remove(enemy)

            if shrine_current_hp <= 0:
                shrine_current_hp = 0
                game_over = True

            # --- DISEGNO NEMICI ---
            for e in enemies:
                if e[3] == 'slime':
                    img = frames_slime[int(e[-2]) % 4]
                elif e[3] == 'dragon':
                    if e[0] < SCREEN_W // 2:
                        img = frames_dragon_right[int(e[-2]) % 4]
                    else:
                        img = frames_dragon_left[int(e[-2]) % 4]
                screen.blit(img, (e[0], e[1]))

            # --- DISEGNO SAMURAI ---
            current_image = current_frames[int(frame_index) % len(current_frames)]
            screen.blit(current_image, (px, py))

        # --- DISEGNO ORB (sopra tutto il resto) ---
        
            for (ox, oy) in orb_positions:
                # alone giallo semitrasparente
                glow_surf = pygame.Surface((ORB_RADIUS * 4, ORB_RADIUS * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 210, 0, 70), (ORB_RADIUS * 2, ORB_RADIUS * 2), ORB_RADIUS * 2)
                screen.blit(glow_surf, (int(ox) - ORB_RADIUS * 2, int(oy) - ORB_RADIUS * 2))
                # corpo principale
                pygame.draw.circle(screen, (255, 220, 0), (int(ox), int(oy)), ORB_RADIUS)
                # riflesso bianco interno
                pygame.draw.circle(screen, (255, 255, 210), (int(ox) - 3, int(oy) - 3), ORB_RADIUS // 3)

        # --- UI ---
        pygame.draw.rect(screen, (50, 50, 50), (SCREEN_W//2 - 150, 30, 300, 20))
        pygame.draw.rect(screen, (0, 200, 255), (SCREEN_W//2 - 150, 30, (shrine_current_hp/shrine_max_hp)*300, 20))
        txt = font_health.render(f"SHRINE HP: {int(shrine_current_hp)}", True, (255, 255, 255))
        screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 55))

        if game_over:
            over_txt = font_health.render("SHRINE DESTROYED! ESC to Quit", True, (255, 50, 50))
            screen.blit(over_txt, (SCREEN_W//2 - over_txt.get_width()//2, SCREEN_H//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
