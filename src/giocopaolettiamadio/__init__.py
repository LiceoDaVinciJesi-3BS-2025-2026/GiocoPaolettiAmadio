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
    
    
    
    # --- FUNZIONI DI SUPPORTO ---

    def load_frames(sheet, ROWS, COLS, FRAME_SIZE):
        frames = []
        for row in range(ROWS):
            for col in range(COLS):
                x = col * FRAME_SIZE
                y = row * FRAME_SIZE
                rect = pygame.Rect(x, y, FRAME_SIZE, FRAME_SIZE)
                #ritaglio una superficie dell'intero foglio
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
    backstage = pygame.image.load("stageDefinitivo.png").convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))
    
    # --- CARICAMENTO SPRITE SAMURAI ---
    sheet_idle = pygame.image.load("Samurai-idle-v1.png").convert_alpha()
    sheet_up = pygame.image.load("SamuraiUpgiusto.png").convert_alpha()
    sheet_down = pygame.image.load("SamuraiDowngiusto.png").convert_alpha()
    sheet_right = pygame.image.load("SamuraiDxgiusto.png").convert_alpha()

    sheet_run_up = pygame.image.load("SamuraiRunUpgiusto.png").convert_alpha()
    sheet_run_down = pygame.image.load("SamuraiRunDowngiusto.png").convert_alpha()
    sheet_run_right = pygame.image.load("SamuraiRunDxgiusto.png").convert_alpha()

    frames_idle_right= load_frames(sheet_idle, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_idle_right = rescale_frames(frames_idle_right, 0.5)
    frames_idle_left = []
    flip_x = True
    flip_y = False
    for frame in frames_idle_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_idle_left.append(flipped_frame)
    
    
    frames_walk_up = load_frames(sheet_up, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_walk_up = rescale_frames(frames_walk_up, 0.5)
    frames_walk_down = load_frames(sheet_down, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_walk_down = rescale_frames(frames_walk_down, 0.5)
    frames_walk_right = load_frames(sheet_right, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_walk_right = rescale_frames(frames_walk_right, 0.5)

    frames_walk_left = []
    for frame in frames_walk_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_walk_left.append(flipped_frame)

    frames_run_up = load_frames(sheet_run_up, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_run_up = rescale_frames(frames_run_up, 0.5)
    frames_run_down = load_frames(sheet_run_down, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_run_down = rescale_frames(frames_run_down, 0.5)
    frames_run_right = load_frames(sheet_run_right, ROWS_samurai, COLS_samurai, FRAME_SIZE_samurai)
    frames_run_right = rescale_frames(frames_run_right, 0.5)

    frames_run_left = []
    for frame in frames_run_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_run_left.append(flipped_frame)

    # --- CARICAMENTO SPRITE FENICE (INGRANDITA) ---
    phoenix_sheet = []
    scale_factor_phoenix = 3  # ingrandimento della fenice

    for num in range(1,5):
        phoenix_a = pygame.image.load(f"{num}rett.png").convert_alpha()
        w, h = phoenix_a.get_size()
        phoenix_a = pygame.transform.scale(phoenix_a, (w * scale_factor_phoenix, h * scale_factor_phoenix))
        phoenix_sheet.append(phoenix_a)


    # --- CARICAMENTO SPRITE SLIME ---
    sheet_slime = pygame.image.load('SlimeSpriteSheet.png').convert_alpha()
    COLS_slime = 4
    ROWS_slime = 1
    FRAME_SIZE_slime = 32    
    slime_idle = load_frames(sheet_slime, ROWS_slime, COLS_slime, FRAME_SIZE_slime)
    slime_idle = rescale_frames(slime_idle, 2)
    slime_frame_index = 0
    slime_anim_speed = 0.10
    

    




    # --- STATO PERSONAGGIO SAMURAI ---
    x, y = SCREEN_W // 2, SCREEN_H // 2
    current_frames = frames_idle_right
    frame_index = 0

    # --- STATO FENICE ---
    phoenix_frame_index = 0
    phoenix_anim_speed = 0.15
    Side_phoenix = 'R'


    # --- LOOP PRINCIPALE ---
    running = True
    while running:
        Old_mouse_pos = pygame.mouse.get_pos()
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
            Side_pg = 'R'
            if is_running:
                 current_frames = frames_run_right
            else:
                current_frames = frames_walk_right

        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= speed
            Side_pg = 'S'
            if is_running:
                 current_frames = frames_run_left
            else:
                current_frames = frames_walk_left

        else:
            if Side_pg == 'R':
                current_frames = frames_idle_right
            else:
                current_frames = frames_idle_left

        # ANIMAZIONE SAMURAI
        anim_speed = ANIM_SPEED
        if is_running:
            anim_speed = ANIM_SPEED * 2
        frame_index += anim_speed
        if frame_index >= len(current_frames):
            frame_index = 0
        current_image = current_frames[int(frame_index)]
        
        #rettangolo che contiene il samurai
        samurai_rect = current_image.get_rect(topleft=(x, y))
        samurai_rect = samurai_rect.inflate(-90, -26)
        
        # posizione mouse
        mouse_pos = pygame.mouse.get_pos()
        
        #ANIMAZIONE DISEGNO FENICE
        phoenix_frame_index += phoenix_anim_speed
        if phoenix_frame_index >= len(phoenix_sheet):
            phoenix_frame_index = 0
        phoenix_image = phoenix_sheet[int(phoenix_frame_index)]
        
        # R/S fenice
        if mouse_pos > Old_mouse_pos:
            Side_phoenix = 'R'
        elif mouse_pos < Old_mouse_pos:
            Side_phoenix = 'S'
          
        if Side_phoenix == 'S':
            phoenix_image = pygame.transform.flip(phoenix_image, True, False)
            
            
        #ANIMAZIONE DISEGNO SLIME
        slime_frame_index += slime_anim_speed
        if slime_frame_index >= 2:
            slime_frame_index = 0
        slime_image = slime_idle[int(slime_frame_index)]
            
        # DISEGNO
        screen.blit(backstage, (0,0))
        
        #samurai
        screen.blit(current_image, (x, y))

        # fenice
        screen.blit(phoenix_image, mouse_pos)
        
        # slime
        screen.blit(slime_image, (600, 300))
        
        # aggiorna schermo
        pygame.display.flip()
        
        
        #mostri
        screen.blit(slime_image, (600, 300))
        
        
        
    pygame.quit()
    sys.exit()

main()
