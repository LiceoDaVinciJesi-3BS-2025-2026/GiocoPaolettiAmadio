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
    
    
    # ========== FUNZIONE UNIVERSALE PER CARICARE MOSTRI ==========
    def load_monster(
        idle_path, idle_rows, idle_cols, idle_frame_size,
        walk_up_path, walk_up_rows, walk_up_cols, walk_up_frame_size,
        walk_down_path, walk_down_rows, walk_down_cols, walk_down_frame_size,
        walk_right_path, walk_right_rows, walk_right_cols, walk_right_frame_size,
        scale_factor=1.0

    ):
        """
        Carica tutte le animazioni di un mostro con configurazioni flessibili.
        
        Parametri obbligatori:
        - idle_path: percorso sprite sheet idle
        - idle_rows, idle_cols, idle_frame_size: configurazione sprite idle
        - walk_up/down/right_path: percorsi sprite sheet movimento
        - walk_up/down/right_rows, cols, frame_size: configurazioni sprite movimento
        - scale_factor: fattore di ridimensionamento (default 1.0)
        

        
        Ritorna una lista con 8 elementi (o 12 se ha animazioni di corsa):
        [0] frames_idle_right
        [1] frames_idle_left
        [2] frames_walk_up
        [3] frames_walk_down
        [4] frames_walk_right
        [5] frames_walk_left

        """
        
        # Carica IDLE
        sheet_idle = pygame.image.load(idle_path).convert_alpha()
        frames_idle_right = load_frames(sheet_idle, idle_rows, idle_cols, idle_frame_size)
        frames_idle_right = rescale_frames(frames_idle_right, scale_factor)
        
        frames_idle_left = []
        for frame in frames_idle_right:
            flipped_frame = pygame.transform.flip(frame, True, False)
            frames_idle_left.append(flipped_frame)
        
        # Carica WALK UP
        sheet_walk_up = pygame.image.load(walk_up_path).convert_alpha()
        frames_walk_up = load_frames(sheet_walk_up, walk_up_rows, walk_up_cols, walk_up_frame_size)
        frames_walk_up = rescale_frames(frames_walk_up, scale_factor)
        
        # Carica WALK DOWN
        sheet_walk_down = pygame.image.load(walk_down_path).convert_alpha()
        frames_walk_down = load_frames(sheet_walk_down, walk_down_rows, walk_down_cols, walk_down_frame_size)
        frames_walk_down = rescale_frames(frames_walk_down, scale_factor)
        
        # Carica WALK RIGHT
        sheet_walk_right = pygame.image.load(walk_right_path).convert_alpha()
        frames_walk_right = load_frames(sheet_walk_right, walk_right_rows, walk_right_cols, walk_right_frame_size)
        frames_walk_right = rescale_frames(frames_walk_right, scale_factor)
        
        # Carica WALK LEFT (flip di right)
        frames_walk_left = []
        for frame in frames_walk_right:
            flipped_frame = pygame.transform.flip(frame, True, False)
            frames_walk_left.append(flipped_frame)
        

        
        return [
            frames_idle_right,   # 0
            frames_idle_left,    # 1
            frames_walk_up,      # 2
            frames_walk_down,    # 3
            frames_walk_right,   # 4
            frames_walk_left,    # 5

        ]
    
    
    # ========== FUNZIONE SEMPLIFICATA PER MOSTRI SOLO IDLE ==========
    def load_monster_idle_only(idle_path, idle_rows, idle_cols, idle_frame_size, scale_factor=1.0):
        """
        Carica solo l'animazione idle per mostri statici.
        Ritorna [frames_idle_right, frames_idle_left]
        """
        try:
            sheet_idle = pygame.image.load(idle_path).convert_alpha()
            print(f"Caricato {idle_path}: {sheet_idle.get_width()}x{sheet_idle.get_height()}")
            print(f"Frame size richiesto: {idle_frame_size}, Righe: {idle_rows}, Colonne: {idle_cols}")
            
            frames_idle_right = load_frames(sheet_idle, idle_rows, idle_cols, idle_frame_size)
            print(f"Frames estratti: {len(frames_idle_right)}")
            
            frames_idle_right = rescale_frames(frames_idle_right, scale_factor)
            
            frames_idle_left = []
            for frame in frames_idle_right:
                flipped_frame = pygame.transform.flip(frame, True, False)
                frames_idle_left.append(flipped_frame)
            
            return [frames_idle_right, frames_idle_left]
        except Exception as e:
            print(f"ERRORE nel caricamento di {idle_path}: {e}")
            raise
    
    
    # ========== CARICAMENTO MOSTRI CON FUNZIONE UNIVERSALE ==========
    
    # --- CARICAMENTO SPRITE SLIME ---
    slime_animations = load_monster_idle_only('SlimeSpriteSheet.png', 1, 4, 32, scale_factor=2.0)
    slime_idle_right = slime_animations[0]
    slime_idle_left = slime_animations[1]
    slime_frame_index = 0
    slime_anim_speed = 0.10
    
    # --- CARICAMENTO SPRITE BABY DRAGON ---
    dragon_animations = load_monster_idle_only('Baby_Dragon_2D.png', 2, 2, 64, scale_factor=3.0)
    dragon_idle_right = dragon_animations[0]
    dragon_idle_left = dragon_animations[1]
    dragon_frame_index = 0
    dragon_anim_speed = 0.08
    dragon_x, dragon_y = 900, 400
    
    # --- CARICAMENTO SPRITE ARCH DEMON ---
    demon_animations = load_monster_idle_only('ArchDemonIdle001-Sheet.png', 1, 6, 128, scale_factor=1.5)
    demon_idle_right = demon_animations[0]
    demon_idle_left = demon_animations[1]
    demon_frame_index = 0
    demon_anim_speed = 0.12
    demon_x, demon_y = 200, 450
           
    
    
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
    
    # --- CARICAMENTO SPRITE SAMURAI (CODICE ORIGINALE) ---
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


    # --- CARICAMENTO SPRITE FENICE (CODICE ORIGINALE) ---
    phoenix_sheet = []
    scale_factor_phoenix = 3  # ingrandimento della fenice

    for num in range(1,5):
        phoenix_a = pygame.image.load(f"{num}rett.png").convert_alpha()
        w, h = phoenix_a.get_size()
        phoenix_a = pygame.transform.scale(phoenix_a, (w * scale_factor_phoenix, h * scale_factor_phoenix))
        phoenix_sheet.append(phoenix_a)


 
    
    # Variabili per Oscuramento
    oscurita_attuale = 0      
    velocita_oscuramento = 4  
    target_oscurita = 255     # Il punto di buio totale
    
    #nebbia: divido per la qualità dell'animazione
    fog_surface = pygame.Surface((SCREEN_W // 16, SCREEN_H // 16))



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
    night = False
    scurimento = True
    while running:
        Old_mouse_pos = pygame.mouse.get_pos()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        #logica per la notte
        if scurimento:
            # Aumentiamo l'oscurità gradualmente fino al target
            if oscurita_attuale < target_oscurita:
                oscurita_attuale += velocita_oscuramento
            elif oscurita_attuale > target_oscurita: 
                oscurita_attuale = target_oscurita
                


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
        if slime_frame_index >= len(slime_idle_right):
            slime_frame_index = 0
        slime_image = slime_idle_right[int(slime_frame_index)]
        
        #ANIMAZIONE DISEGNO BABY DRAGON
        dragon_frame_index += dragon_anim_speed
        if dragon_frame_index >= len(dragon_idle_right):
            dragon_frame_index = 0
        dragon_image = dragon_idle_right[int(dragon_frame_index)]
        
        #ANIMAZIONE DISEGNO ARCH DEMON
        demon_frame_index += demon_anim_speed
        if demon_frame_index >= len(demon_idle_right):
            demon_frame_index = 0
        demon_image = demon_idle_right[int(demon_frame_index)]
            
        # DISEGNO
        screen.blit(backstage, (0,0))
        
        #mostri
        # slime
        screen.blit(slime_image, (600, 300))
        
        # baby dragon
        screen.blit(dragon_image, (dragon_x, dragon_y))
        
        # arch demon
        screen.blit(demon_image, (demon_x, demon_y))
        
        # Prepariamo la maschera di oscurità
        fog_surface.fill((0, 0, 0))          # Riempiamo di nero
        fog_surface.set_alpha(oscurita_attuale) # Applichiamo il livello di buio attuale
        
        pygame.draw.circle(fog_surface, (255, 255, 255), ((mouse_pos[0] + 24) // 16, (mouse_pos[1] + 16) // 16), 7)
        
        # Applichiamo la nebbia sopra il gioco: la ridimensiono all'origine
        screen.blit(pygame.transform.scale(fog_surface, (SCREEN_W, SCREEN_H)), (0, 0))
    

        #samurai
        screen.blit(current_image, (x, y))

        # fenice
        screen.blit(phoenix_image, mouse_pos)
        
        
        #trasparenza del cerchio di luce
        fog_surface.set_colorkey((255, 255, 255))
        
        # aggiorna schermo
        pygame.display.flip()
        
        
        
        
        
    pygame.quit()
    sys.exit()

main()