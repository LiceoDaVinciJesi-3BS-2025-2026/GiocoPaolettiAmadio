def main() -> None:
    
    import pygame
    import sys

    pygame.init()

    # FINESTRA
    SCREEN_W, SCREEN_H = 1280, 656
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Samurai + Luce iniziale")
    clock = pygame.time.Clock()

    # COSTANTI SPRITE
    COLS = 5
    ROWS = 5
    FRAME_SIZE = 256
    ANIM_SPEED = 0.15
    SPEED_WALK = 4
    SPEED_RUN = 8

    # CARICAMENTO SPRITE SHEET
    sheet_idle = pygame.image.load("Samurai-idle-v1.png").convert_alpha()

    sheet_up = pygame.image.load("SamuraiUpgiusto.png").convert_alpha()
    sheet_down = pygame.image.load("SamuraiDowngiusto.png").convert_alpha()
    sheet_right = pygame.image.load("SamuraiDxgiusto.png").convert_alpha()

    sheet_run_up = pygame.image.load("SamuraiRunUpgiusto.png").convert_alpha()
    sheet_run_down = pygame.image.load("SamuraiRunDowngiusto.png").convert_alpha()
    sheet_run_right = pygame.image.load("SamuraiRunDxgiusto.png").convert_alpha()

    # FUNZIONE FRAME
    def load_frames(sheet):
        frames = []

        for row in range(ROWS):
            for col in range(COLS):
                x = col * FRAME_SIZE
                y = row * FRAME_SIZE
                rect = pygame.Rect(x, y, FRAME_SIZE, FRAME_SIZE)
                frames.append(sheet.subsurface(rect))

        return frames

    # FRAME ANIMAZIONI
    frames_idle = load_frames(sheet_idle)

    frames_walk_up = load_frames(sheet_up)
    frames_walk_down = load_frames(sheet_down)
    frames_walk_right = load_frames(sheet_right)
    frames_walk_left = []

    for frame in frames_walk_right:
        frames_walk_left.append(pygame.transform.flip(frame, True, False))

    frames_run_up = load_frames(sheet_run_up)
    frames_run_down = load_frames(sheet_run_down)
    frames_run_right = load_frames(sheet_run_right)
    frames_run_left = []

    for frame in frames_run_right:
        frames_run_left.append(pygame.transform.flip(frame, True, False))

    # STATO PERSONAGGIO
    x, y = SCREEN_W // 2, SCREEN_H // 2
    current_frames = frames_idle
    frame_index = 0

    # LOOP PRINCIPALE
    running = True
    while running:
        #gestione tempo
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        #contenitore di tutti i tasti premuti
        keys = pygame.key.get_pressed()
        #pulsanti corsa
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        #calcolo velocità
        if is_running:
            speed = SPEED_RUN
        else:
            speed = SPEED_WALK

        # MOVIMENTO + ANIMAZIONE
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y -= speed
            current_frames = frames_run_up if is_running else frames_walk_up

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y += speed
            current_frames = frames_run_down if is_running else frames_walk_down

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += speed
            current_frames = frames_run_right if is_running else frames_walk_right

        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= speed
            current_frames = frames_run_left if is_running else frames_walk_left

        else:
            current_frames = frames_idle

        # ANIMAZIONE
        anim_speed = ANIM_SPEED * (2 if is_running else 1)
        frame_index += anim_speed

        if frame_index >= len(current_frames):
            frame_index = 0

        current_image = current_frames[int(frame_index)]

        # DISEGNO
        screen.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, "yellow", mouse_pos, 80)

        screen.blit(current_image, (x, y))
        pygame.display.flip()

    pygame.quit()
    
    #interrompe lo script in modo più pulito
    sys.exit()

main()
