def main() -> None:
    
    import pygame
    import sys

    pygame.init()

    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
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
    
    #immagine scenario
    backstage = pygame.image.load("stageDefinitivo.png").convert_alpha()
    backstage = pygame.transform.scale(backstage,(SCREEN_W,SCREEN_H))
    

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
    
    #funzione ridimensiona frames
    def rescale_frames(lista_frames):
        frames = []
        
        for frame in lista_frames:
            w, h = frame.get_size()
            fattore = 0.5
            frame = pygame.transform.scale(frame, (int(w*fattore), int(h*fattore)))
            frames.append(frame)
         
        return frames
    
    # FRAME ANIMAZIONI
    frames_idle_right = load_frames(sheet_idle)
    frames_idle_right = rescale_frames(frames_idle_right)

    frames_idle_left = []

    flip_x = True
    flip_y = False

    for frame in frames_idle_right:
        flipped_frame = pygame.transform.flip(frame, flip_x, flip_y)
        frames_idle_left.append(flipped_frame)
        
        
    frames_walk_up = load_frames(sheet_up)
    frames_walk_up = rescale_frames(frames_walk_up)
    frames_walk_down = load_frames(sheet_down)
    frames_walk_down= rescale_frames(frames_walk_down)
    frames_walk_right = load_frames(sheet_right)
    frames_walk_right = rescale_frames(frames_walk_right)
    

    frames_walk_left = []

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


    # STATO PERSONAGGIO
    x, y = SCREEN_W // 2, SCREEN_H // 2
    current_frames = frames_idle_right
    frame_index = 0
    side_pg = 'R'
    
    
    # LOOP PRINCIPALE
    running = True
    while running:
        #gestione tempo
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
            side_pg = 'R'
            x += speed
            if is_running:
                 current_frames = frames_run_right
            else:
                current_frames = frames_walk_right

        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            side_pg = 'L'
            x -= speed
            if is_running:
                 current_frames = frames_run_left
                 
            else:
                current_frames = frames_walk_left

        else:
            if side_pg == 'R':
                current_frames = frames_idle_right
            else:
                current_frames = frames_idle_left

        # ANIMAZIONE
        anim_speed = ANIM_SPEED

        if is_running:
            anim_speed = ANIM_SPEED * 2

        frame_index += anim_speed

        if frame_index >= len(current_frames):
            frame_index = 0

        current_image = current_frames[int(frame_index)]

        # DISEGNO
        
        #scenario
        screen.blit(backstage,(0,0) )
        
        #mouse
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, "yellow", mouse_pos, 80)
        
        #pg
        screen.blit(current_image, (x, y))
        pygame.display.flip()

    pygame.quit()
    
    #interrompe lo script in modo più pulito
    sys.exit()

main()