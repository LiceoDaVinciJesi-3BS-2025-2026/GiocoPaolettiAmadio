import pygame
import sys
import math
import random
import datetime
import os
from platformdirs import PlatformDirs

# --- FUNZIONI DI SUPPORTO ---
def load_frames(sheet, ROWS, COLS, FRAME_SIZE_W, FRAME_SIZE_H=None):
    """
    Estrae i singoli frame da uno spritesheet pygame.
    Argomenti
        sheet:        La superficie pygame che contiene lo spritesheet.
        ROWS:         Numero di righe di frame nello spritesheet.
        COLS:         Numero di colonne di frame nello spritesheet.
        FRAME_SIZE_W: Larghezza di ogni frame in pixel.
        FRAME_SIZE_H: Altezza di ogni frame in pixel.
                      Se None, viene usato FRAME_SIZE_W (frame quadrati).
    Returns:
        Lista di superfici pygame, una per ogni frame,
        ordinati da sinistra a destra e dall'alto verso il basso.
    """
    frames = []
    if FRAME_SIZE_H is None:
        FRAME_SIZE_H = FRAME_SIZE_W
    for row in range(ROWS):
        #Quindi pygame Rect definisce il rettangolo di ritaglio, e sheet.subsurface(rect) ritaglia quel pezzo dallo spritesheet e lo salva in frames.
        for col in range(COLS):
            rect = pygame.Rect(col * FRAME_SIZE_W, row * FRAME_SIZE_H, FRAME_SIZE_W, FRAME_SIZE_H)
            frames.append(sheet.subsurface(rect))
    return frames

def rescale_frames(lista_frames, fattore):
    """
    Riscala tutti i frame di una lista in base a un fattore moltiplicativo.

    Args:
        lista_frames: Lista di superfici pygame da riscalare.
        fattore:      Fattore di scala (es. 2 = doppia dimensione, 0.5 = metà dimensione).

    Returns:
        Nuova lista di superfici pygame riscalate.
    """
    frames_riscalati = []  # Lista che conterrà i frame riscalati
    for f in lista_frames:  # Scorre ogni frame della lista originale
        nuova_larghezza = int(f.get_width() * fattore)   # Calcola la nuova larghezza moltiplicando quella originale per il fattore
        nuova_altezza = int(f.get_height() * fattore)    # Calcola la nuova altezza moltiplicando quella originale per il fattore
        frame_riscalato = pygame.transform.scale(f, (nuova_larghezza, nuova_altezza))  # Riscala il frame alle nuove dimensioni
        frames_riscalati.append(frame_riscalato)  # Aggiunge il frame riscalato alla lista

    return frames_riscalati  # Restituisce la lista con tutti i frame riscalati

def load_shrine_state(filename, shrine_rect):
    """
    Carica un'immagine e la riscala proporzionalmente alla larghezza del rettangolo fornito.

    Argomenti:
        filename:    Percorso del file immagine da caricare.
        shrine_rect: Rettangolo pygame che definisce le dimensioni target (viene usata la larghezza).

    Returns:
        Superficie pygame riscalata proporzionalmente alla larghezza di shrine_rect.
    """
    img = pygame.image.load(filename).convert_alpha()  # Carica l'immagine dal file mantenendo la trasparenza

    scale_factor = shrine_rect.width / img.get_width()  # Calcola il fattore di scala in base al rapporto tra la larghezza target e quella originale

    return pygame.transform.scale(img, (shrine_rect.width, int(img.get_height() * scale_factor)))  
    # Riscala l'immagine mantenendo le proporzioni: larghezza fissa a shrine_rect.width, altezza scalata proporzionalmente

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
    pts = [  # Calcola i 4 vertici del rettangolo della lama ruotato attorno al centro
        (cx + cos_a*hl - sin_a*hw,  cy + sin_a*hl + cos_a*hw),  # Punta destra
        (cx + cos_a*hl + sin_a*hw,  cy + sin_a*hl - cos_a*hw),  # Punta sinistra
        (cx - cos_a*hl + sin_a*hw,  cy - sin_a*hl - cos_a*hw),  # Manico sinistro
        (cx - cos_a*hl - sin_a*hw,  cy - sin_a*hl + cos_a*hw),  # Manico destro
    ]
    pygame.draw.polygon(surf, (190, 210, 230), pts)  # Disegna la lama con colore grigio-azzurro, i 3 numeri sono quelli che danno il colore
    pygame.draw.polygon(surf, (240, 250, 255), pts, 1) #(1px è lo spessore dle bordo)
    pygame.draw.circle(surf, (255, 255, 255), (int(cx + cos_a*hl), int(cy + sin_a*hl)), 2 )  # Disegna un piccolo cerchio bianco sulla punta del coltello, spessore 2px
    # Calcola i 4 vertici del rettangolo del manico, posizionato all'estremità opposta alla punta
    # È leggermente più largo della lama (hw+2) e lungo 5 pixel (hl -> hl-5)
    h_pts = [ 
        (cx - cos_a*hl        - sin_a*(hw+2),  cy - sin_a*hl        + cos_a*(hw+2)),
        #Per ruotare un punto attorno a un centro si usa questa formula matematica:
#xruotato = cx (x delpunto) + cos(angolo)*x_originale - sin(angolo)*y_originale
#yruotato = cy (y del punto) + sin(angolo)*x_originale + cos(angolo)*y_originale
        (cx - cos_a*hl        + sin_a*(hw+2),  cy - sin_a*hl        - cos_a*(hw+2)),
        (cx - cos_a*(hl-5)    + sin_a*(hw+2),  cy - sin_a*(hl-5)    - cos_a*(hw+2)),
        (cx - cos_a*(hl-5)    - sin_a*(hw+2),  cy - sin_a*(hl-5)    + cos_a*(hw+2)),
    ] #Il risultato è una lista delle 4 coordinate calcolate con gli angoli del manico del coltello.
    pygame.draw.polygon(surf, (100, 70, 40), h_pts) #disegna  il manico con colore marrone scuro
    return surf

# --- SISTEMA ORDE ---
def calcola_orda(wave_num, sets):
    totale      = int(4 + (wave_num - 1) * sets[17])
    #massimo raggiunto intorno alla wave 7
    prob_dragon = min(sets[18]*(wave_num / 7), sets[18])
    hp_mult     = 1.0 + (wave_num - 1) * 0.1 * sets[17]
    params = [totale, prob_dragon, hp_mult]
    return params #parametri per ogni orda, aumentati mano a mano che le ordine aumentano

def build_spawn_queue(params, hp_slime, hp_dragon, speed_slime, speed_dragon):
    """
    Costruisce una coda di nemici da spawnare in base ai parametri dell'ondata.

    Argomenti:
        params: Lista [totale, prob_dragon, hp_mult] generata da calcola_orda()
                - params[0]: numero totale di nemici da generare
                - params[1]: probabilità che un nemico sia un drago (0.0 - 1.0)
                - params[2]: moltiplicatore degli HP dei nemici

    Return:
        Lista di nemici, ognuno rappresentato come [e_type, hp, espeed, e_w, e_h]
    """
    queue = [] # lista che conterrà tutti i nemici che appariranno
    for coso in range(params[0]): # Ripete per ogni nemico da generare
        #Genera un numero casuale tra 0 e 1 e lo confronta con la probabilità drago
        # se il numero è minore della probabilità spawn di un drago, altrimenti uno slime
        if random.random() < params[1]:
            e_type = 'dragon'
        else:
            e_type = 'slime'

        if e_type == 'slime':
            hp     = int(hp_slime * params[2])
            espeed = speed_slime
            e_w    = 80
            e_h    = 80
        else:
            hp     = int(hp_dragon * params[2])
            espeed = speed_dragon
            e_w    = 160
            e_h    = 160

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
    
    
# --- FUNZIONI CLASSIFICA/SALVATAGGIO DEL GIOCO
#creo l'oggetto platformdirs per la mia app
#creo il path per il file aggiunto
#lo metto nella direcotry dell'APP sull'Utente
dirs = PlatformDirs("CrimsonGuard", ensure_exists=True)  
CLASSIFICA_FILE = dirs.user_data_path / "classifica.txt"

def chiave_modalita(settings):
    """Crea per ogni set di parametri di gioco una chiave,
       sequenza di riconoscimento."""
    parti = []
    for v in settings:
        parti.append(str(round(v, 2)))
    return "-".join(parti)



def salva_partita(nickname, wave, nemici, durata_sec, coltelli, settings):
    """Aggiunge una riga al file classifica.txt"""
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    minuti = int(durata_sec // 60)
    secondi = int(durata_sec % 60)
    nickname = nickname[:12]
    riga = f"{data} | {nickname:<3} | Wave: {wave:>3} | Nemici: {nemici:>4} | Durata: {minuti:02d}:{secondi:02d} | Coltelli: {coltelli:>4}\n"
    chiave  = chiave_modalita(settings)
    intestazione = f"[MODALITA:{chiave}]\n"
    
    # leggo tutto il file esistente
    if os.path.exists(CLASSIFICA_FILE):
        f = open(CLASSIFICA_FILE, "r", encoding="utf-8")
        contenuto = f.readlines()
        f.close()
    else:
        contenuto = []
    
    # cerco se la modalità esiste già
    trovata = False
    nuove_righe = []
    i = 0
    while i < len(contenuto):
        nuove_righe.append(contenuto[i])
        if contenuto[i] == intestazione:
            trovata = True
            # aggiungo la riga subito dopo l'intestazione, prima della prossima modalità
            i += 1
            while i < len(contenuto) and not contenuto[i].startswith("[MODALITA:"):
                nuove_righe.append(contenuto[i])
                i += 1
            nuove_righe.append(riga)
            continue
        i += 1

    # se la modalità non esiste, la aggiungo in fondo
    if not trovata:
        nuove_righe.append(intestazione)
        nuove_righe.append(riga)
    
    
    f = open(CLASSIFICA_FILE, "w", encoding="utf-8") 
    f.writelines(nuove_righe)
    f.close()
    
def carica_classifica(max_righe=8, sets=None):
    """Legge le ultime max_righe dal file classifica"""
    if not os.path.exists(CLASSIFICA_FILE):
        return []
    f = open(CLASSIFICA_FILE, "r", encoding="utf-8")
    contenuto = f.readlines()
    f.close()
    
    if sets is None:
        # fallback: prende tutte le righe non-intestazione
        righe = []
        for r in contenuto:
            if not r.startswith("[MODALITA:"):
                righe.append(r.rstrip("\n"))
        return righe[-max_righe:]
    
    #se prosegue, vuol dire ci sono dei settings
    chiave      = chiave_modalita(sets)
    intestazione = f"[MODALITA:{chiave}]\n"

    # trovo il blocco della modalità corrente
    righe_modalita = []
    dentro = False
    for r in contenuto:
        if r == intestazione:
            dentro = True
            continue
        if r.startswith("[MODALITA:") and dentro:
            break
        
        #r.strip() è un controllo per la riga non vuota
        if dentro and r.strip():
            righe_modalita.append(r.rstrip("\n"))

    if max_righe is None:
            return righe_modalita
    return righe_modalita[-max_righe:]
    
    
def carica_top_classifica(max_righe=8, sets=None):
    """Legge tutte le righe, le ordina per wave decrescente e restituisce le migliori max_righe."""
    righe = carica_classifica(max_righe=None, sets=sets)
    if not righe:
        return []
    
    
    # estraggo il numero di wave da ogni riga (formato: "... | Wave: NNN | ...")
    def estrai_orda(riga):
        parte_wave = riga.split("|")[2]
        numero = parte_wave.split(":")[1]
        return numero    
    
    #key è il parametro(numero di orda) su cui mi baso per l'ordine crescente
    #con reverse inverto la lista (ordine decrescente)
    righe.sort(key=estrai_orda, reverse=True)

    if len(righe) <= max_righe:
        return righe

    migliori = []
    for pos in range(max_righe):
        migliori.append(righe[pos])
    return migliori
    
    
       
    

def disegna_classifica(screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H,
                       classifica, nickname="", mostra_top=False, GameEnd = True):
    """Disegna la schermata classifica. Usata sia dal game over che dalla schermata iniziale.
       Restituisce il rect del pulsante switch per gestire i click nel loop chiamante."""
    cx = SCREEN_W // 2

    titolo = font_wave.render("CLASSIFICA", True, (255, 220, 60))
    screen.blit(titolo, (cx - titolo.get_width()//2, 40))

    pygame.draw.line(screen, (120, 120, 120), (cx - 320, 120), (cx - 320, SCREEN_H - 80), 1)

    # etichetta modalità corrente
    if mostra_top:
        label = font_health.render("Top 8 per Wave:", True, (180, 220, 255))
    else:
        label = font_health.render("Ultime 8 partite:", True, (180, 220, 255))
    screen.blit(label, (cx - 300, 130))

    i = 0
    for riga in classifica:
        parti = []
        for p in riga.split("|"):
            parti.append(p.strip())
        colore = (200, 200, 200)
        for parte in parti:
            if nickname and parte == nickname.strip():
                colore = (255, 255, 100)
                break
            
        s = font_small.render(riga, True, colore)
        screen.blit(s, (cx - 300, 165 + i * 34))
        i += 1

    # pulsante switch
    if mostra_top:
        btn_label = font_small.render("[ Ultime 8 ]", True, (255, 220, 60))
    else:
        btn_label = font_small.render("[ Top 8 Wave ]", True, (255, 220, 60))
    switch_rect = pygame.Rect(cx + 260, 125, btn_label.get_width() + 16, 30)
    pygame.draw.rect(screen, (60, 60, 90), switch_rect, border_radius=5)
    pygame.draw.rect(screen, (180, 180, 100), switch_rect, 1, border_radius=5)
    screen.blit(btn_label, (switch_rect.x + 8, switch_rect.y + 5))
    
    if GameEnd:
        hint = font_small.render("SPAZIO per ricominciare  |  ESC per uscire", True, (160, 160, 160))
                
    else:
        hint = font_small.render("ESC per chiudere", True, (160, 160, 160))
        
    screen.blit(hint, (cx - hint.get_width()//2, SCREEN_H - 50))
    
    return switch_rect


def disegna_istruzioni(screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H):
    """Disegna la schermata istruzioni/tutorial."""
    cx = SCREEN_W // 2

    titolo = font_wave.render("COME SI GIOCA", True, (255, 220, 60))
    screen.blit(titolo, (cx - titolo.get_width()//2, 30))

    righe = [
        ("OBIETTIVO",          (255, 180, 60)),
        ("Uccidi i mostri prima che raggiungano il tempio al centro della mappa.", (220, 220, 180)),
        ("Quando i mostri sono vicini al tempio lo attaccano, riducendone gli HP.", (220, 220, 180)),
        ("Se gli HP del tempio arrivano a zero: GAME OVER.",                        (220, 220, 180)),
        ("",                   (255, 255, 255)),
        ("ORDE",          (255, 180, 60)),
        ("Man mano che uccidi nemici, le orde si fanno sempre più numerose.", (220, 220, 180)),
        ("Inoltre, più vai avanti con le orde, più i mostri saranno forti e resistenti.", (220, 220, 180)),
        ("",                   (255, 255, 255)),
        ("MOVIMENTO",          (255, 180, 60)),
        ("WASD  /  Frecce direzionali:   corri sulla mappa",                    (220, 220, 180)),
        ("Tieni premuto SHIFT mentre ti muovi:   cammina lentamente",                   (220, 220, 180)),
        ("",                   (255, 255, 255)),
        ("ATTACCARE",          (255, 180, 60)),
        ("Orb rotanti:  colpiscono automaticamente i nemici che toccano.",           (220, 220, 180)),
        ("Coltelli:   premi TASTO SINISTRO del mouse per lanciare un coltello.",    (220, 220, 180)),
        ("            I coltelli volano verso il puntatore del mouse.",             (220, 220, 180)),
        ("",                   (255, 255, 255)),
        ("ALTRO",              (255, 180, 60)),
        ("ESC:   chiude il gioco in qualsiasi momento",                          (220, 220, 180)),
    ]

    y = 120
    for testo, colore in righe:
        if testo == "":
            y += 10
            continue
        # titoli di sezione in font_health, resto in font_small
        if colore == (255, 180, 60):
            surf = font_health.render(testo, True, colore)
        else:
            surf = font_small.render(testo, True, colore)
        screen.blit(surf, (cx - surf.get_width()//2, y))
        y += surf.get_height() + 6

    hint = font_small.render("ESC per chiudere", True, (160, 160, 160))
    screen.blit(hint, (cx - hint.get_width()//2, SCREEN_H - 50))


def disegna_settings(screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H, icon_plus, icon_minus, settings):
    """Disegna la schermata settings con slider/valori modificabili."""
    cx = SCREEN_W // 2

    titolo = font_wave.render("IMPOSTAZIONI", True, (255, 220, 60))
    screen.blit(titolo, (cx - titolo.get_width()//2, 30))

    voci = [
        "Velocità camminata",
        "Velocità corsa",
        "Velocità dei coltelli",
        "Danno coltello",
        "Portata dei coltelli",
        "Danno orb",
        "N° orb",
        "Raggio orbite delle orb",
        "Velocità orb",
        "Hp del tempio",
        "Vita draghi",
        "Danno draghi sul tempio",                          
        "Velocità draghi",
        "Vita slime",
        "Danno slime sul tempio",                                   
        "Velocità slime",                                    
        "Pausa tra orde (ms)",
        "Velocità incremento difficoltà",
        "% max spawn draghi",
        "Volume musica"
    ]
    
    
    # colonna sinistra: indici 0-8, colonna destra: indici 9-17
    col_x = [cx - 580, cx + 20]   # x di partenza testo per ogni colonna
    btn_x = [cx - 130, cx + 470]  # x di partenza pulsanti per ogni colonna

    btn_rects = []
    y_start = 110
    y_step  = 52

    for i in range(20):
        colonna  = 0 if i < 10 else 1
        riga     = i if i < 10 else i - 10
        y        = y_start + riga * y_step

        valore = settings[i]
        testo  = font_small.render(f"{voci[i]}:  {valore}", True, (220, 220, 180))
        screen.blit(testo, (col_x[colonna], y))

        r_minus = pygame.Rect(btn_x[colonna],      y, 32, 28)
        r_plus  = pygame.Rect(btn_x[colonna] + 36, y, 32, 28)

        for r in [r_minus, r_plus]:
            pygame.draw.rect(screen, (70, 70, 100), r, border_radius=5)
            pygame.draw.rect(screen, (180, 180, 220), r, 1, border_radius=5)
        screen.blit(icon_minus, (r_minus.x + 0, r_minus.y - 2))
        screen.blit(icon_plus,  (r_plus.x  + 0, r_plus.y  - 2))

        btn_rects.append((r_minus, r_plus))

    # linea divisoria verticale tra le due colonne
    pygame.draw.line(screen, (100, 100, 140), (cx - 10, 100), (cx - 10, SCREEN_H - 60), 1)

    hint = font_small.render("ESC per chiudere", True, (160, 160, 160))
    screen.blit(hint, (cx - hint.get_width()//2, SCREEN_H - 40))

    return btn_rects
    
#---------------------------------------------------------------------------------------#
#funzione run del gioco

def main() -> None:
    pygame.init()
        # ===================== AGGIUNTA AUDIO =====================
    pygame.mixer.init()
        
    MUSICA_MENU  = "materiali\danzadellelame.mp3"
    MUSICA_GIOCO = "materiali\danzadellelame2.mp3"
    musica_corrente = ""   # tiene traccia di quale file è caricato
    # ==========================================================
    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Crimson Guard")
    clock = pygame.time.Clock()

    # ================== SCHERMATA INIZIALE (caricata una volta sola) ==================
    start_screen_img = pygame.image.load("materiali\schermataI.png").convert_alpha()
    start_screen_img = pygame.transform.scale(start_screen_img, (SCREEN_W, SCREEN_H))
    START_BUTTON_RECT = pygame.Rect(522, 600, 300, 90)
    
    # --- PULSANTE (schermata iniziale) ---
    #r -> raw string -> faccio capire a python che deve interpretare \ in modo letterale 
    ui_sheet = pygame.image.load(r"materiali\UI_grey_buttons_1.png").convert_alpha()
    # ogni icona è 16x16 pixel nello sheet;
    #considerando la prima colonna/riga come 'zero' come nelle liste
    #prendo riga 0 colon 4 (icona lista/elenco)
    icon_size = 16
    
    #icona per la classifica
    icon_raw = ui_sheet.subsurface(pygame.Rect(4 * icon_size, 0 * icon_size, icon_size, icon_size))
    icon_img = pygame.transform.scale(icon_raw, (48, 48))
    CLASSIFICA_BTN_RECT = pygame.Rect(SCREEN_W - 80, SCREEN_H - 80, 60, 60)

    # carico le icone + e - dallo sheet
    icon_plus_raw  = ui_sheet.subsurface(pygame.Rect(0 * icon_size, 5 * icon_size, icon_size, icon_size))
    icon_minus_raw = ui_sheet.subsurface(pygame.Rect(1 * icon_size, 5 * icon_size, icon_size, icon_size))
    icon_plus  = pygame.transform.scale(icon_plus_raw,  (32, 32))
    icon_minus = pygame.transform.scale(icon_minus_raw, (32, 32))

    #icona punto interrogativo per le istruzioni (riga 5, colonna 4)
    icon_raw_info = ui_sheet.subsurface(pygame.Rect(4 * icon_size, 5 * icon_size, icon_size, icon_size))
    icon_img_info = pygame.transform.scale(icon_raw_info, (48, 48))
    INFO_BTN_RECT = pygame.Rect(SCREEN_W - 80, SCREEN_H - 150, 60, 60)
    
    #icona per i settings
    icon_raw_settings = ui_sheet.subsurface(pygame.Rect(3 * icon_size, 2 * icon_size, icon_size, icon_size))
    icon_img_settings = pygame.transform.scale(icon_raw_settings, (48, 48))
    SETTINGS_BTN_RECT = pygame.Rect(SCREEN_W - 80, SCREEN_H - 220, 60, 60)  # sopra il pulsante info
    
    
    
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
    ORB_NUM = 2

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
    
    # --- COSTANTI MOSTRI ---
    SLIME_HP = 30
    DRAGON_HP = 50
    SLIME_SPEED = 2.0
    DRAGON_SPEED = 1.2
    SLIME_DAMAGE = 0.05
    DRAGON_DAMAGE = 0.07
    
    # -- costante shrine ---
    shrine_max_hp = 100.0
    
    
    # --- durata danno in game ---
    HIT_FLASH_DURATION = 8
    
    # --- coefficiente difficoltà crescente del gioco ---
    COEFF_DIF = 2

    # --- probabilità massimo di spawn del drago in percentuale
    prob_dragon_max = 0.7

    # --- volume musica in game ---
    STANDARD_VOLUME = 0.5
    
    # --- SETTINGS MODIFICABILI DA UI ---
    settings = [
            SPEED_WALK,
            SPEED_RUN,
            KNIFE_SPEED,
            KNIFE_DAMAGE,
            KNIFE_MAX_RANGE,
            ORB_DAMAGE,
            ORB_NUM,
            ORB_ORBIT_RADIUS,
            ORB_SPEED,
            shrine_max_hp,
            DRAGON_HP,
            DRAGON_DAMAGE,
            DRAGON_SPEED,
            SLIME_HP,
            SLIME_DAMAGE,
            SLIME_SPEED,
            PAUSE_DURATION,
            COEFF_DIF,
            prob_dragon_max,
            STANDARD_VOLUME
    ]
    


    
    
    
    
    
    
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

    def get_shrine_img(hp_cur, max_hp):
        percentuale = (hp_cur / max_hp) * 100
        if   percentuale > 75:
            return shrine_100
        elif percentuale > 50:
            return shrine_75
        elif percentuale > 25:
            return shrine_50
        elif percentuale > 0:
            return shrine_25
        return shrine_0

    # --- CARICAMENTO SAMURAI ---
    frames_idle_right = get_samurai_frames("materiali\Samurai-idle-v1.png", FRAME_SIZE_samurai)

    frames_idle_left = []
    for f in frames_idle_right:
        frame_flippato = pygame.transform.flip(f, True, False) #pygame.transform.flip(superficie, flip_orizzontale, flip_verticale)
        frames_idle_left.append(frame_flippato)

    frames_walk_up    = get_samurai_frames("materiali\SamuraiUpgiusto.png",   FRAME_SIZE_samurai)
    frames_walk_down  = get_samurai_frames("materiali\SamuraiDowngiusto.png", FRAME_SIZE_samurai)
    frames_walk_right = get_samurai_frames("materiali\SamuraiDxgiusto.png",   FRAME_SIZE_samurai)

    frames_walk_left = []
    for f in frames_walk_right:
        frame_flippato = pygame.transform.flip(f, True, False)
        frames_walk_left.append(frame_flippato)

    frames_run_up    = get_samurai_frames("materiali\SamuraiRunUpgiusto.png",   FRAME_SIZE_samurai)
    frames_run_down  = get_samurai_frames("materiali\SamuraiRunDowngiusto.png", FRAME_SIZE_samurai)
    frames_run_right = get_samurai_frames("materiali\SamuraiRunDxgiusto.png",   FRAME_SIZE_samurai)

    frames_run_left = []
    for f in frames_run_right:
        frame_flippato = pygame.transform.flip(f, True, False)
        frames_run_left.append(frame_flippato)

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
            
                # ===================== AGGIUNTA AUDIO =====================
    # Avvia la musica del menu solo se non stava già suonando
        if musica_corrente != MUSICA_MENU:
            musica_corrente = MUSICA_MENU
            pygame.mixer.music.load(MUSICA_MENU)
            #ssettings[19] è il volume preimpostato, valore tra 0.0 e 1.0
            pygame.mixer.music.set_volume(settings[19])
            pygame.mixer.music.play(-1)   # -1 = loop infinito, ad esempio con 0 si ripete una volta
        # ================== SCHERMATA INIZIALE ==================
        in_start_screen = True
        mostra_classifica_start = False
        mostra_top_start = False
        switch_rect_start = None
        mostra_istruzioni = False
        mostra_settings = False
        settings_btn_rects = []
        while in_start_screen:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if mostra_classifica_start:
                            mostra_classifica_start = False
                        elif mostra_istruzioni:
                            mostra_istruzioni = False
                        elif mostra_settings:
                            mostra_settings = False
                        else:
                            pygame.quit()
                            sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #mi assicuro che nessun menù sia aperto per l'avvio del gioco
                    if not mostra_classifica_start and not mostra_istruzioni and not mostra_settings and START_BUTTON_RECT.collidepoint(event.pos):
                        in_start_screen = False
                    if CLASSIFICA_BTN_RECT.collidepoint(event.pos):
                        mostra_classifica_start = not mostra_classifica_start
                        mostra_istruzioni = False
                        mostra_settings = False
                    if INFO_BTN_RECT.collidepoint(event.pos):
                        mostra_istruzioni = not mostra_istruzioni
                        mostra_classifica_start = False
                        mostra_settings = False
                    if SETTINGS_BTN_RECT.collidepoint(event.pos):
                        mostra_settings = not mostra_settings
                        mostra_classifica_start = False
                        mostra_istruzioni = False
                    
                    if mostra_settings and settings_btn_rects:
                        i = 0
                        for (r_minus, r_plus) in settings_btn_rects:
                            #step diverso per pausa tra le orde
                            if i == 16 :
                                step = 100
                            
                            #step diverso per velocità mostri e velocità incremento rode
                            elif i == 8 or i == 12 or i == 15 or i == 17:
                                step = 0.1
                            
                            #step diverso per danni mostri
                            elif i == 11 or i == 14 or i == 18 or i == 19:
                                step = 0.01
                            
                            else:
                                step = 1
                                
                            if r_minus.collidepoint(event.pos):
                                if i == 18 or i == 19:
                                    #la musica può arrivare anche a zero(muto)
                                    #la prob dei draghi può esser nulla(solo slime)
                                    #round evita errori di rappresentazione decimale
                                    settings[i] = round(max(0, settings[i] - step), 2)
                                else:
                                    #per il resto, il valore minimo è lo step
                                    #round evita errori di rappresentazione decimale
                                    settings[i] = round(max(step, settings[i] - step), 2)
                                    
                            if r_plus.collidepoint(event.pos):
                                if i == 18 or i == 19:
                                    #max valore per il volmue musica è 1
                                    #la prob dei draghi è al massimo 1(100%)
                                    #round evita errori di rappresentazione decimale
                                    settings[i] = round(min(1.0, settings[i] + step), 2)
                                else:
                                    #per il resto, non ci sono massimi
                                    #round evita errori di rappresentazione decimale
                                    settings[i] = round(settings[i] + step, 2)
                
                            pygame.mixer.music.set_volume(settings[19])
                            i += 1
                            
                    
                    if mostra_classifica_start:
                        if switch_rect_start and switch_rect_start.collidepoint(event.pos):
                            mostra_top_start = not mostra_top_start
                            if mostra_top_start:
                                classifica_dati = carica_top_classifica(sets=settings)
                            else:
                                classifica_dati = carica_classifica(sets=settings)
                                
            screen.blit(start_screen_img, (0, 0))

            if mostra_classifica_start:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                if mostra_top_start:
                    classifica_dati = carica_top_classifica(sets=settings)
                else:
                    classifica_dati = carica_classifica(sets=settings)
                switch_rect_start = disegna_classifica(screen, font_wave, font_health, font_small,
                                   SCREEN_W, SCREEN_H, classifica_dati, mostra_top=mostra_top_start, GameEnd=False)
            
            if mostra_istruzioni:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                disegna_istruzioni(screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H)
            
            
            if mostra_settings:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                settings_btn_rects = disegna_settings(screen, font_wave, font_health, font_small,
                                               SCREEN_W, SCREEN_H, icon_plus, icon_minus, settings)
            
            
            
            # --- disegno pulsante classifica ---
            btn_color = (80, 80, 120) if CLASSIFICA_BTN_RECT.collidepoint(pygame.mouse.get_pos()) else (50, 50, 90)
            pygame.draw.rect(screen, btn_color, CLASSIFICA_BTN_RECT, border_radius=8)
            pygame.draw.rect(screen, (180, 180, 220), CLASSIFICA_BTN_RECT, 2, border_radius=8)
            screen.blit(icon_img, (CLASSIFICA_BTN_RECT.x + 6, CLASSIFICA_BTN_RECT.y + 6))
            
            
            # --- disegno pulsante istruzioni ---
            btn_color_info = (80, 80, 120) if INFO_BTN_RECT.collidepoint(pygame.mouse.get_pos()) else (50, 50, 90)
            pygame.draw.rect(screen, btn_color_info, INFO_BTN_RECT, border_radius=8)
            pygame.draw.rect(screen, (180, 180, 220), INFO_BTN_RECT, 2, border_radius=8)
            screen.blit(icon_img_info, (INFO_BTN_RECT.x + 6, INFO_BTN_RECT.y + 6))
            
            
            # --- disegno pulsante settings ---
            btn_color_set = (80, 80, 120) if SETTINGS_BTN_RECT.collidepoint(pygame.mouse.get_pos()) else (50, 50, 90)
            pygame.draw.rect(screen, btn_color_set, SETTINGS_BTN_RECT, border_radius=8)
            pygame.draw.rect(screen, (180, 180, 220), SETTINGS_BTN_RECT, 2, border_radius=8)
            screen.blit(icon_img_settings, (SETTINGS_BTN_RECT.x + 6, SETTINGS_BTN_RECT.y + 6))
            
            
            pygame.display.flip()
        # Passaggio menu → gioco: carica e avvia la musica di gioco    
        musica_corrente = MUSICA_GIOCO
        print("Carico:", MUSICA_GIOCO)
        pygame.mixer.music.load(MUSICA_GIOCO)
        print("Loaded OK")
        pygame.mixer.music.play(-1)
        print("Playing:", pygame.mixer.music.get_busy())
        
        # ================== INIT VARIABILI DI GIOCO ==================
        wave_state   = "WAVE_SPAWN"
        current_wave = 1
        spawn_queue  = build_spawn_queue(calcola_orda(current_wave, sets=settings), settings[13], settings[10], settings[15], settings[12])
        spawn_timer  = 0
        pause_timer  = 0

        
        shrine_current_hp = settings[9]
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
                #settings[0] è speed_walk, settings[1] è speed_run
                speed      = settings[0] if is_walking else settings[1]
                moved      = False

                # --- MOVIMENTO ---
                if keys[pygame.K_w] or keys[pygame.K_UP]:    #se si preme il tasto w o la freccia direzionale verso l'alto
                    py -= speed                           #asse y diminuisce andando verso l'alto in python
                    if is_walking:      #se viene utilizzata quella combinazione di tasti per camminare allora:
                        current_frames = frames_walk_up      #cammina verso alto 
                    else:
                        current_frames = frames_run_up    #sennò corre
                    moved = True
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    py += speed                         #asse y aumenta andando verso il basso in python
                    if is_walking:
                        current_frames = frames_walk_down
                    else:
                        current_frames = frames_run_down
                    moved = True
                elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    px -= speed          #asse x dimuisce andando verso sinistra in python
                    side_pg = 'L'           #personaggio rivolto verso sinistra
                    if is_walking:              #se cammina verso sx si utilizzano i frame, impostati precedentemente, del personaggio che cammina a sx
                        current_frames = frames_walk_left
                    else:
                        current_frames = frames_run_left    #altrimenti corre normalmente verso destra
                    moved = True
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    px += speed             #asse x aumenta andando verso destra in python
                    side_pg = 'R'           #personaggio rivolto verso destra
                    if is_walking:           #se cammina verso dx si utilizzano i frame, impostati precedentemente, del personaggio che cammmina a dx
                        current_frames = frames_walk_right
                    else:
                        current_frames = frames_run_right  #altrimenti corre normalmente verso destra
                    moved = True

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
                    vx = math.cos(angle) * settings[2]
                    vy = math.sin(angle) * settings[2]
                    surf = make_knife_surface(angle, KNIFE_LENGTH, KNIFE_WIDTH)
                    hs   = surf.get_width() // 2
                    knives.append([pg_cx, pg_cy, vx, vy, surf, hs, 0])
                    coltelli_sparati += 1

                
                    # --- AGGIORNA ORB ---
                #calcolo angolazione della orb
                orb_angle += settings[8] * (dt / 1000.0)
                #centro del personaggio
                pg_cx = px + 64
                pg_cy = py + 64
                orb_positions = []
                
                for i in range(settings[6]):
                    #dividiamo il cerchio in tanti angoli congruenti  quante sono le orbe
                    angs_equi = 2 * math.pi / settings[6]
                    #per ogni orb diversa, aggiungo l'angolo congruente all'angolo attuale delle orb
                    #math.cos(angolo): Ci dice quanto dobbiamo spostarci a DESTRA o SINISTRA dal centro, in proporzione
                    orb_dist_x = math.cos(orb_angle + i * angs_equi) * settings[7]
                    #math.sin(angolo): Ci dice quanto dobbiamo spostarci in ALTO o BASSO dal centro, in proporzione
                    orb_dist_y = math.sin(orb_angle + i * angs_equi) * settings[7]
                    #*settings[7](raggio dell'orbita) moltiplica il valore trovato con sin e cos per il raggio, lo allunga
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
                    k[6] += settings[2]
                    if k[0] < -60 or k[0] > SCREEN_W+60 or k[1] < -60 or k[1] > SCREEN_H+60 or k[6] >= settings[4]:
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
                    if pause_timer >= settings[16]:
                        current_wave += 1
                        spawn_queue  = build_spawn_queue(calcola_orda(current_wave, sets=settings), settings[13], settings[10], settings[15], settings[12])
                        spawn_timer  = 0
                        wave_state   = "WAVE_SPAWN"

                # --- DISEGNO SFONDO ---
                screen.blit(backstage, (0, 0))
                shrine_img = get_shrine_img(shrine_current_hp, settings[9])
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
                        if enemy[3] == 'slime':
                            shrine_current_hp -= settings[14]
                        else:
                            shrine_current_hp -= settings[11]
                        
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
                                enemy[2] -= settings[5] #danno orb
                                enemy[8]  = HIT_FLASH_DURATION
                                orb_hit_cooldowns.append([eid, ORB_DAMAGE_COOLDOWN])
                                break

                    enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[4], enemy[5])

                    # Collisione COLTELLI
                    for k in knives.copy():
                        knife_rect = pygame.Rect(k[0]-k[5], k[1]-k[5], k[5]*2, k[5]*2)
                        if enemy_rect.colliderect(knife_rect):
                            enemy[2] -= settings[3] #danno coltelli
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
                        ecx_drag = e[0] + e[4] / 2   # centro X del drago corrente
                        if ecx_drag < shrine_rect.centerx:
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
            pygame.draw.rect(screen, (0, 200, 255), (SCREEN_W//2-150, 30, (shrine_current_hp/settings[9])*300, 20))
            txt = font_health.render(f"SHRINE HP: {int(shrine_current_hp)}", True, (255,255,255))
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 55))

            wave_txt = font_small.render(f"WAVE  {current_wave}", True, (255, 220, 80))
            screen.blit(wave_txt, (20, 20))

            if wave_state == "WAVE_ACTIVE":
                rem_txt = font_small.render(f"Nemici: {len(enemies)}", True, (220, 220, 220))
                screen.blit(rem_txt, (20, 48))

            if wave_state == "WAVE_PAUSE":
                seconds_left = max(1, int((settings[16] - pause_timer) / 1000) + 1)
                ann = font_wave.render(f"WAVE  {current_wave + 1}  in  {seconds_left}...", True, (255, 230, 60))
                screen.blit(ann, (SCREEN_W//2 - ann.get_width()//2, SCREEN_H//2 - 40))

            pygame.display.flip()

        # ================== GAME OVER: inserimento nickname ==================
        nickname       = ""
        salvato        = False
        classifica     = []
        inserimento_ok = False  # diventa True dopo INVIO
        mostra_top_gameover = False
        switch_rect_go = None
        
        
        while game_over:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #uscita#
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        pygame.quit()
                        sys.exit()
                    if not inserimento_ok:
                        # --- fase di digitazione nickname ---
                        if event.key == pygame.K_RETURN and nickname.strip():
                            # salva e carica classifica
                            salva_partita(nickname.strip(), current_wave,
                                          nemici_uccisi, durata_sec, coltelli_sparati, settings)
                            classifica     = carica_classifica(sets=settings)
                            inserimento_ok = True
                        elif event.key == pygame.K_BACKSPACE:
                            # --- cancella in inserimento ---
                            nickname = nickname[:-1]
                        else:
                            if len(nickname) <= 8 and event.unicode.isprintable():
                                nickname += event.unicode
                    else:
                        # --- fase di visualizzazione risultati ---
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_SPACE:
                            game_over = False  # torna al while True esterno
                
                if event.type == pygame.MOUSEBUTTONDOWN and inserimento_ok:
                    if switch_rect_go and switch_rect_go.collidepoint(event.pos):
                        mostra_top_gameover = not mostra_top_gameover
                        if mostra_top_gameover:
                            classifica = carica_top_classifica(sets=settings)
                        else:
                            classifica = carica_classifica(sets=settings)
                
                
            # --- DISEGNO SFONDO ---
            screen.blit(backstage, (0, 0))
            shrine_img = get_shrine_img(shrine_current_hp, settings[9])
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
                
                i = 0
                for riga in stats:
                    s = font_health.render(riga, True, (220, 220, 180))
                    screen.blit(s, (cx - s.get_width()//2, 200 + i * 44))
                    i += 1
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
                switch_rect_go = disegna_classifica(screen, font_wave, font_health, font_small,
                                   SCREEN_W, SCREEN_H, classifica, nickname, mostra_top_gameover, GameEnd=True)
                
                
                # statistiche ultima partita (colonna sinistra)
                minuti  = int(durata_sec // 60)
                secondi = int(durata_sec % 60)
                tua_txt = font_health.render("La tua partita:", True, (180, 220, 255))
                screen.blit(tua_txt, (70, 130))
                stats = [
                    f"Nickname: {nickname.strip()}",
                    f"Wave raggiunta: {current_wave}",
                    f"Nemici uccisi:  {nemici_uccisi}",
                    f"Durata:         {minuti:02d}:{secondi:02d}",
                    f"Coltelli lanciati: {coltelli_sparati}",
                ]
                i = 0
                for riga in stats:
                    s = font_small.render(riga, True, (210, 210, 210))
                    screen.blit(s, (70, 165 + i * 32))
                    i += 1

                

            
            pygame.display.flip()

        # game_over == False → il while True esterno riparte dalla schermata iniziale

# --- AVVIO ---
if __name__ == "__main__":
    main()
