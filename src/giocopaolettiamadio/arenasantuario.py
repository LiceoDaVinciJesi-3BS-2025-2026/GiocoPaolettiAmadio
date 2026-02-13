def main() -> None:
    import pygame
    import sys

    pygame.init()
    
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Phoenix Quest - Defend the Shrine")
    clock = pygame.time.Clock()
    
    
    # --- FUNZIONI DI SUPPORTO ---

    def load_frames(sheet, ROWS, COLS, FRAME_SIZE):
        frames = []
        for row in range(ROWS):
            for col in range(COLS):
                x = col * FRAME_SIZE
                y = row * FRAME_SIZE
                rect = pygame.Rect(x, y, FRAME_SIZE, FRAME_SIZE)
                frames.append(sheet.subsurface(rect))
        return frames

    def rescale_frames(lista_frames, fattore):
        frames = []
        for frame in lista_frames:
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w*fattore), int(h*fattore)))
            frames.append(frame)
        return frames
    
    
    # COSTANTI SPRITE PERSONAGGIO
    COLS_samurai = 5
    ROWS_samurai = 5
    FRAME_SIZE_samurai = 256
    ANIM_SPEED = 0.15
    SPEED_WALK = 4
    SPEED_RUN = 8
    Side_pg = 'R'

    # --- CARICAMENTO SFONDO ---
    backstage = pygame.image.load("arenavuota.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))
    
    # --- CARICAMENTO SANTUARIO (PNG TRASPARENTE CENTRATO) ---
    shrine_img = pygame.image.load("Adobe Express - file (1).png").convert_alpha()

    shrine_scale = 0.7
    w = shrine_img.get_width()
    h = shrine_img.get_height()
    shrine_img = pygame.transform.scale(
        shrine_img,
        (int(w * shrine_scale), int(h * shrine_scale))
    )

    shrine_x = (SCREEN_W - shrine_img.get_width()) // 2
    shrine_y = (SCREEN_H - shrine_img.get_height()) // 2
    
    # HP Santuario
    shrine_max_hp = 100
    shrine_current_hp = shrine_max_hp
    
    # --- CARICAMENTO SPRITE SAMURAI ---
    sheet_idle = pygame.image.load("Samurai-idle-v1.png").convert_alpha()
    sheet_up = pygame.image.load("SamuraiUpgiusto.png").convert_alpha()
    sheet_down = pygame.image.load("SamuraiDowngiusto.png").convert_alpha()
    sheet_right = pygame.image.load("SamuraiDxgiusto.png").convert_alpha()

    sheet_run_up = pygame.image.load("SamuraiRunUpgiusto.png").convert_alpha()
    sheet_run_down = pygame.image.load("SamuraiRunDowngiusto.png").convert_alpha()
    sheet_run_right = pygame.image.load("SamuraiRunDxgiusto.png").convert_alpha()

    frames_idle_right = rescale_frames(
        load_frames(sheet_idle, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )

    frames_idle_left = [
        pygame.transform.flip(frame, True, False)
        for frame in frames_idle_right
    ]

    frames_walk_up = rescale_frames(
        load_frames(sheet_up, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_walk_down = rescale_frames(
        load_frames(sheet_down, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_walk_right = rescale_frames(
        load_frames(sheet_right, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_walk_left = [
        pygame.transform.flip(frame, True, False)
        for frame in frames_walk_right
    ]

    frames_run_up = rescale_frames(
        load_frames(sheet_run_up, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_run_down = rescale_frames(
        load_frames(sheet_run_down, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_run_right = rescale_frames(
        load_frames(sheet_run_right, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai), 0.5
    )
    frames_run_left = [
        pygame.transform.flip(frame, True, False)
        for frame in frames_run_right
    ]

    # Font
    font_health = pygame.font.Font(None, 40)
    font_big = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 35)

    # Stato personaggio
    x, y = SCREEN_W // 2, SCREEN_H // 2
    current_frames = frames_idle_right
    frame_index = 0

    # --- LOOP PRINCIPALE ---
    running = True
    game_over = False

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            speed = SPEED_RUN if is_running else SPEED_WALK

            moved = False

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                y -= speed
                current_frames = frames_run_up if is_running else frames_walk_up
                moved = True

            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                y += speed
                current_frames = frames_run_down if is_running else frames_walk_down
                moved = True

            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                x += speed
                Side_pg = 'R'
                current_frames = frames_run_right if is_running else frames_walk_right
                moved = True

            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                x -= speed
                Side_pg = 'L'
                current_frames = frames_run_left if is_running else frames_walk_left
                moved = True

            if not moved:
                current_frames = frames_idle_right if Side_pg == 'R' else frames_idle_left

            # Animazione
            anim_speed = ANIM_SPEED * 2 if is_running else ANIM_SPEED
            frame_index += anim_speed
            if frame_index >= len(current_frames):
                frame_index = 0

            current_image = current_frames[int(frame_index)]

            # Limiti schermo
            x = max(0, min(x, SCREEN_W - 128))
            y = max(0, min(y, SCREEN_H - 128))

            # TEST: Premi K per danneggiare il santuario
            if keys[pygame.K_k]:
                shrine_current_hp -= 0.5
                if shrine_current_hp <= 0:
                    shrine_current_hp = 0
                    game_over = True

        # --- DISEGNO ---
        screen.blit(backstage, (0, 0))
        screen.blit(shrine_img, (shrine_x, shrine_y))

        # Barra HP
        shrine_bar_width = 300
        shrine_bar_height = 25
        shrine_bar_x = (SCREEN_W - shrine_bar_width) // 2
        shrine_bar_y = shrine_y - 40

        pygame.draw.rect(screen, (50, 50, 50),
                         (shrine_bar_x, shrine_bar_y,
                          shrine_bar_width, shrine_bar_height))

        shrine_hp_percentage = shrine_current_hp / shrine_max_hp
        current_shrine_bar = int(shrine_bar_width * shrine_hp_percentage)

        if shrine_hp_percentage > 0.6:
            shrine_color = (0, 200, 255)
        elif shrine_hp_percentage > 0.3:
            shrine_color = (255, 200, 0)
        else:
            shrine_color = (255, 50, 50)

        pygame.draw.rect(screen, shrine_color,
                         (shrine_bar_x, shrine_bar_y,
                          current_shrine_bar, shrine_bar_height))

        pygame.draw.rect(screen, (255, 255, 255),
                         (shrine_bar_x, shrine_bar_y,
                          shrine_bar_width, shrine_bar_height), 3)

        shrine_hp_text = font_health.render(
            f"Shrine HP: {int(shrine_current_hp)}/{shrine_max_hp}",
            True, (255, 255, 255)
        )

        screen.blit(shrine_hp_text,
                    ((SCREEN_W - shrine_hp_text.get_width()) // 2,
                     shrine_bar_y - 35))

        screen.blit(current_image, (x, y))

        if game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))

            game_over_text = font_big.render(
                "SHRINE DESTROYED!", True, (255, 50, 50)
            )
            screen.blit(game_over_text,
                        ((SCREEN_W - game_over_text.get_width()) // 2,
                         SCREEN_H // 2 - 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


main()
