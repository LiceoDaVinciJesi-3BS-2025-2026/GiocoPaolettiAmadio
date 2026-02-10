def main() -> None:
    import pygame
    import sys

    pygame.init()
    
    #nascondiamo il mouse
    pygame.mouse.set_visible(False)
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Samurai + Luce iniziale + Fenice")
    clock = pygame.time.Clock()
    
    # COSTANTI SPRITE
    COLS = 5
    ROWS = 5
    FRAME_SIZE = 256
    ANIM_SPEED = 0.15
    SPEED_WALK = 4
    SPEED_RUN = 8

    # --- FUNZIONI DI SUPPORTO ---

    def load_frames(sheet):
        frames = []
        for row in range(ROWS):
            for col in range(COLS):
                x = col * FRAME_SIZE
                y = row * FRAME_SIZE
                rect = pygame.Rect(x, y, FRAME_SIZE, FRAME_SIZE)
                frames.append(sheet.subsurface(rect))
        return frames

    def rescale_frames(lista_frames):
        frames = []
        for frame in lista_frames:
            w, h = frame.get_size()
            fattore = 0.5
            frame = pygame.transform.scale(frame, (int(w*fattore), int(h*fattore)))
            frames.append(frame)
        return frames

    # --- CARICAMENTO SPRITE SAMURAI ---
    backstage = pygame.image.load("stageDefinitivo.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))

    sheet_idle = pygame.image.load("Samurai-idle-v1.png").convert_alpha()
    sheet_up = pygame.image.load("SamuraiUpgiusto.png").convert_alpha()
    sheet_down = pygame.image.load("SamuraiDowngiusto.png").convert_alpha()
    sheet_right = pygame.image.load("SamuraiDxgiusto.png").convert_alpha()

    sheet_run_up = pygame.image.load("SamuraiRunUpgiusto.png").convert_alpha()
    sheet_run_down = pygame.image.load("SamuraiRunDowngiusto.png").convert_alpha()
    sheet_run_right = pygame.image.load("SamuraiRunDxgiusto.png").convert_alpha()

    frames_idle = load_frames(sheet_idle)
    frames_idle = rescale_frames(frames_idle)

    frames_walk_up = load_frames(sheet_up)
    frames_walk_up = rescale_frames(frames_walk_up)
    frames_walk_down = load_frames(sheet_down)
    frames_walk_down= rescale_frames(frames_walk_down)
    frames_walk_right = load_frames(sheet_right)
    frames_walk_right = rescale_frames(frames_walk_right)

    frames_walk_left = []
    flip_x = True
    flip_y = False
    for frame in frames_walk_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_walk_left.append(flipped_frame)

    frames_run_up = load_frames(sheet_run_up)
    frames_run_up = rescale_frames(frames_run_up)
    frames_run_down = load_frames(sheet_run_down)
    frames_run_down = rescale_frames(frames_run_down)
    frames_run_right = load_frames(sheet_run_right)
    frames_run_right = rescale_frames(frames_run_right)

    frames_run_left = []
    for frame in frames_run_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_run_left.append(flipped_frame)

    # --- CARICAMENTO SPRITE FENICE ---
    # Assumiamo che la fenice abbia una sprite sheet orizzontale di 4 frame, 24*16 dimensioni
    phoenix_sheet = []
    for num in range(1,5):
        phoenix_a = pygame.image.load(f"{num}rett.png").convert_alpha()
        phoenix_sheet.append(phoenix_a)
#         
#     PHOENIX_FRAME_WIDTH = 24
#     PHOENIX_FRAME_HEIGHT = 16
#     PHOENIX_FRAME_COUNT = 4
# 
#     frames_phoenix = []
#     for i in range(PHOENIX_FRAME_COUNT):
#         rect = pygame.Rect(i * PHOENIX_FRAME_WIDTH, 0, PHOENIX_FRAME_WIDTH, PHOENIX_FRAME_HEIGHT)
#         frame = phoenix_sheet.subsurface(rect)
#         frames_phoenix.append(frame)

#     # Ridimensioniamo fenice se vuoi (opzionale)
#     scale_factor_phoenix = 1  # puoi cambiare se vuoi
#     if scale_factor_phoenix != 1:
#         frames_phoenix = [pygame.transform.scale(f, (int(PHOENIX_FRAME_WIDTH*scale_factor_phoenix), int(PHOENIX_FRAME_HEIGHT*scale_factor_phoenix))) for f in frames_phoenix]
# 
    # --- STATO PERSONAGGIO SAMURAI ---
    x, y = SCREEN_W // 2, SCREEN_H // 2
    current_frames = frames_idle
    frame_index = 0

#     # --- STATO FENICE ---
#     phoenix_x = -PHOENIX_FRAME_WIDTH  # parte da fuori schermo a sinistra
#     phoenix_y = 100                   # altezza fenice
#     phoenix_speed = 3                 # velocità movimento
    phoenix_frame_index = 0
    phoenix_anim_speed = 0.2

    # --- LOOP PRINCIPALE ---
    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if is_running:
            speed = SPEED_RUN
        else:
            speed = SPEED_WALK

        # MOVIMENTO + ANIMAZIONE SAMURAI
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y -= speed
            if is_running:
                current_frames = frames_run_up 
            else:
                current_frames = frames_walk_up

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y += speed
            if is_running:
                current_frames = frames_run_down
            else:
                current_frames = frames_walk_down

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += speed
            if is_running:
                 current_frames = frames_run_right
            else:
                current_frames = frames_walk_right

        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= speed
            if is_running:
                 current_frames = frames_run_left
            else:
                current_frames = frames_walk_left

        else:
            current_frames = frames_idle

        # ANIMAZIONE SAMURAI
        anim_speed = ANIM_SPEED
        if is_running:
            anim_speed = ANIM_SPEED * 2
        frame_index += anim_speed
        if frame_index >= len(current_frames):
            frame_index = 0
        current_image = current_frames[int(frame_index)]

#         # MOVIMENTO + ANIMAZIONE FENICE
#         phoenix_x += phoenix_speed
#         if phoenix_x > SCREEN_W:
#             phoenix_x = -PHOENIX_FRAME_WIDTH  # torna a partire da sinistra
# 
        phoenix_frame_index += phoenix_anim_speed
        if phoenix_frame_index >= len(phoenix_sheet):
            phoenix_frame_index = 0
        phoenix_image = phoenix_sheet[int(phoenix_frame_index)]

        # DISEGNO
        screen.blit(backstage, (0,0))
        
        # samurai
        screen.blit(current_image, (x, y))

        # luce mouse
        mouse_pos = pygame.mouse.get_pos()

        # fenice
        screen.blit(phoenix_image, mouse_pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

main()
