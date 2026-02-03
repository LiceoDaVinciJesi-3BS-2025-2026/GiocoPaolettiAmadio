def main() -> None:
    import pygame

    pygame.init()
    SCREEN_WIDTH = 1400
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
    pygame.display.set_caption("Il mio primo gioco con Sebotto!")
    # posizione iniziale
    x = SCREEN_WIDTH // 2
    y = SCREEN_HEIGHT // 2

    # dimensioni rettangolo
    w = 40
    h = 20

    # velocità di spostamento
    speed = 4


    running = True

    #loop degli eventi
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()  
        if keys[pygame.K_ESCAPE]:
            running = False
        
        #calcolo spostamento
        if keys[pygame.K_LEFT] and x > 0: 
            w,h = 40,20
            x -= speed 
        if keys[pygame.K_RIGHT] and x < SCREEN_WIDTH - w: 
            w,h = 40,20
            x += speed 
        if keys[pygame.K_UP] and y > 0: 
            w,h = 20,40
            y -= speed 
        if keys[pygame.K_DOWN] and y < SCREEN_HEIGHT - h: 
            w,h = 20,40
            y += speed
            
        #posizione del mouse
        mpos = pygame.mouse.get_pos()
        
        
        
        
        screen.fill("black")
        
        # cerchio cerchio di luce di raggio 80 con il centro nel mouse
        # c è il "rettangolo" che contiene il cerchio disegnato
        c = pygame.draw.circle(screen, "yellow", mpos, 80)
        
        #personaggio
        player = pygame.draw.rect(screen, "red", (x, y, w, h)) 
        
        pygame.display.flip()

    pygame.quit()
