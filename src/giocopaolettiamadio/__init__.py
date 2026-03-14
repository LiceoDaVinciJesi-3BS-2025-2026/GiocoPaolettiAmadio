import datetime
import math
import os
import random
import sys
from importlib.resources import files

import pygame
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
        FRAME_SIZE_H = FRAME_SIZE_W  # se non viene fornita l'altezza, si assume che i frame siano quadrati
    for row in range(ROWS):
        # pygame Rect definisce il rettangolo di ritaglio, e sheet.subsurface(rect) ritaglia quel pezzo dallo spritesheet e lo salva in frames.
        for col in range(COLS):
            # Calcola la posizione in pixel del frame in base alla sua riga e colonna nello spritesheet
            # col * FRAME_SIZE_W = offset orizzontale, row * FRAME_SIZE_H = offset verticale
            rect = pygame.Rect(
                col * FRAME_SIZE_W, row * FRAME_SIZE_H, FRAME_SIZE_W, FRAME_SIZE_H
            )
            # subsurface() crea una nuova Surface che fa riferimento alla stessa area di memoria del foglio originale
            # (non è una copia fisica separata, è più efficiente)
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
        nuova_larghezza = int(
            f.get_width() * fattore
        )  # Calcola la nuova larghezza moltiplicando quella originale per il fattore
        nuova_altezza = int(
            f.get_height() * fattore
        )  # Calcola la nuova altezza moltiplicando quella originale per il fattore
        frame_riscalato = pygame.transform.scale(
            f, (nuova_larghezza, nuova_altezza)
        )  # Riscala il frame alle nuove dimensioni
        frames_riscalati.append(
            frame_riscalato
        )  # Aggiunge il frame riscalato alla lista

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
    img = pygame.image.load(
        filename
    ).convert_alpha()  # Carica l'immagine dal file mantenendo la trasparenza

    scale_factor = (
        shrine_rect.width / img.get_width()
    )  # Calcola il fattore di scala in base al rapporto tra la larghezza target e quella originale

    return pygame.transform.scale(
        img, (shrine_rect.width, int(img.get_height() * scale_factor))
    )
    # Riscala l'immagine mantenendo le proporzioni: larghezza fissa a shrine_rect.width, altezza scalata proporzionalmente


def get_samurai_frames(filename, FRAME_SIZE_samurai):
    """
    Carica lo spritesheet del samurai e restituisce i frame ridimensionati al 50%,
    convertiti per supportare la trasparenza.

    Argomenti:
        filename:          Percorso del file immagine dello spritesheet.
        FRAME_SIZE_samurai: Larghezza (e altezza) in pixel di ogni frame nello spritesheet originale.

    Returns:
        Lista di 25 superfici pygame (5 righe × 5 colonne) riscalate al 50%.
    """

    sheet = pygame.image.load(filename).convert_alpha()
    # load_frames estrae i 25 frame (5 righe × 5 colonne) dal foglio,
    # poi rescale_frames li riduce al 50% per adattarli alle dimensioni di gioco
    return rescale_frames(load_frames(sheet, 5, 5, FRAME_SIZE_samurai), 0.5)


def get_shrine_img(hp_cur, max_hp, lista):
    """
    Restituisce l'immagine del tempio corrispondente agli HP correnti.
    Le soglie sono: >75% → intatto, >50% → dannegg. legg., >25% → danneggiato, >0% → quasi distrutto

    Argomenti:
        hp_cur: HP correnti del tempio.
        max_hp: HP massimi del tempio (settings[9]).
        lista:  Lista di 5 superfici pygame del tempio in ordine di danno crescente:
                [0] intatto (>75%), [1] danneggiato lievemente (>50%),
                [2] danneggiato (>25%), [3] quasi distrutto (>0%), [4] distrutto (0%).

    Returns:
        La superficie pygame corrispondente allo stato di salute attuale del tempio.
    """

    percentuale = (hp_cur / max_hp) * 100
    if percentuale > 75:
        return lista[0]
    elif percentuale > 50:
        return lista[1]
    elif percentuale > 25:
        return lista[2]
    elif percentuale > 0:
        return lista[3]
    return lista[4]  # se HP = 0 (game over), mostra il tempio completamente distrutto


def make_knife_surface(angle_rad, KNIFE_LENGTH, KNIFE_WIDTH):
    """
    Crea e restituisce una superficie pygame con il disegno del coltello ruotato all'angolo dato.
    La superficie è quadrata e abbastanza grande da contenere il coltello in qualsiasi orientamento
    senza che venga tagliato ai bordi. Lo sfondo è completamente trasparente.

    Argomenti:
        angle_rad:    Angolo di orientamento del coltello in radianti,
                      calcolato con atan2 verso il cursore del mouse.
        KNIFE_LENGTH: Lunghezza della lama in pixel (usata anche per calcolare la dimensione
                      della superficie: KNIFE_LENGTH * 2 + 4).
        KNIFE_WIDTH:  Metà larghezza della lama in pixel; controlla lo spessore del coltello.

    Returns:
        Superficie pygame quadrata con il coltello disegnato (lama grigio-azzurra,
        bordo bianco, punta bianca, manico marrone) centrato e ruotato secondo angle_rad.
    """

    size = KNIFE_LENGTH * 2 + 4
    # pygame.SRCALPHA abilita il canale alpha su tutta la superficie,
    # rendendo trasparente tutto ciò che non viene disegnato esplicitamente
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Il centro della superficie è il punto di rotazione del coltello
    cx, cy = size // 2, size // 2
    # Precalcola seno e coseno dell'angolo per evitare di ricalcolarli più volte
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    hw, hl = KNIFE_WIDTH, KNIFE_LENGTH  # Metà larghezza e lunghezza del coltello
    pts = [  # calcola i 4 vertici del rettangolo della lama ruotato attorno al centro e  aggiunti a questa lista
        (cx + cos_a * hl - sin_a * hw, cy + sin_a * hl + cos_a * hw),  # Punta destra
        (cx + cos_a * hl + sin_a * hw, cy + sin_a * hl - cos_a * hw),  # Punta sinistra
        (cx - cos_a * hl + sin_a * hw, cy - sin_a * hl - cos_a * hw),  # Manico sinistro
        (cx - cos_a * hl - sin_a * hw, cy - sin_a * hl + cos_a * hw),  # Manico destro
    ]
    pygame.draw.polygon(
        surf, (190, 210, 230), pts
    )  # disegna la lama con colore grigio-azzurro, i 3 numeri sono quelli che danno il colore

    pygame.draw.polygon(surf, (240, 250, 255), pts, 1)  # (1px è lo spessore dle bordo)
    pygame.draw.circle(
        surf, (255, 255, 255), (int(cx + cos_a * hl), int(cy + sin_a * hl)), 2
    )  # Disegna un piccolo cerchio bianco sulla punta del coltello, spessore 2px

    # Calcola i 4 vertici del rettangolo del manico, posizionato all'estremità opposta alla punta
    # È leggermente più largo della lama (hw+2) e lungo 5 pixel (hl -> hl-5)
    h_pts = [
        (cx - cos_a * hl - sin_a * (hw + 2), cy - sin_a * hl + cos_a * (hw + 2)),
        # Per ruotare un punto attorno a un centro si usa questa formula matematica:
        # xruotato = cx (x delpunto) + cos(angolo)*x_originale - sin(angolo)*y_originale
        # yruotato = cy (y del punto) + sin(angolo)*x_originale + cos(angolo)*y_originale
        (cx - cos_a * hl + sin_a * (hw + 2), cy - sin_a * hl - cos_a * (hw + 2)),
        (
            cx - cos_a * (hl - 5) + sin_a * (hw + 2),
            cy - sin_a * (hl - 5) - cos_a * (hw + 2),
        ),
        (
            cx - cos_a * (hl - 5) - sin_a * (hw + 2),
            cy - sin_a * (hl - 5) + cos_a * (hw + 2),
        ),
    ]  # Il risultato è una lista delle 4 coordinate calcolate con gli angoli del manico del coltello.
    pygame.draw.polygon(
        surf, (100, 70, 40), h_pts
    )  # disegna  il manico con colore marrone scuro
    return surf


# --- SISTEMA ORDE ---
def calcola_orda(wave_num, sets):
    """
    Calcola i parametri di difficoltà per una data ondata.

    Argomenti:
        wave_num: Numero dell'ondata corrente (parte da 1).
        sets:     Lista delle impostazioni di gioco.
                  - sets[17]: coefficiente di difficoltà, controlla la crescita
                               del numero di nemici e degli HP per ondata.
                  - sets[18]: probabilità massima di spawn dei draghi (0.0 - 1.0),
                               raggiunta intorno alla wave 7.

    Returns:
        Lista [totale, prob_dragon, hp_mult]:
            - totale:      numero totale di nemici da spawnare in questa ondata.
            - prob_dragon: probabilità (0.0 - 1.0) che ogni nemico sia un drago.
            - hp_mult:     moltiplicatore degli HP dei nemici per questa ondata.
    """
    # Il numero totale di nemici per ondata parte da 4 e cresce linearmente
    # in base al numero di wave e al coefficiente di difficoltà (sets[17])
    totale = int(4 + (wave_num - 1) * sets[17])

    # La probabilità di spawn dei draghi cresce fino a un massimo (sets[18])
    # la crescita è proporzionale ma raggiunge il massimo intorno alla wave 7
    # min() impedisce di superare il valore massimo configurato
    # massimo raggiunto intorno alla wave 7
    prob_dragon = min(sets[18] * (wave_num / 7), sets[18])

    # Gli HP dei nemici aumentano del 10% a ogni wave (moltiplicato per il coeff di difficoltà)
    # Alla wave 1 il moltiplicatore è 1.0 (nessun bonus), alla wave 2 è 1.1×coeff, ecc.
    hp_mult = 1.0 + (wave_num - 1) * 0.1 * sets[17]
    params = [totale, prob_dragon, hp_mult]
    return (
        params  # parametri per ogni orda, aumentati mano a mano che le ordine aumentano
    )


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
    queue = []  # lista che conterrà tutti i nemici che appariranno
    for coso in range(params[0]):  # Ripete per ogni nemico da generare
        # Genera un numero casuale tra 0 e 1 e lo confronta con la probabilità drago
        # se il numero è minore della probabilità spawn di un drago, altrimenti uno slime
        if random.random() < params[1]:
            e_type = "dragon"
        else:
            e_type = "slime"

        # Imposta hp, velocità e dimensioni in base al tipo di nemico
        # Gli hp vengono moltiplicati per hp_mult per scalare la difficoltà con le wave
        if e_type == "slime":
            hp = int(hp_slime * params[2])
            espeed = speed_slime
            e_w = 80  # Larghezza sprite slime in pixel
            e_h = 80  # Altezza sprite slime in pixel
        else:
            hp = int(hp_dragon * params[2])
            espeed = speed_dragon
            e_w = 160  # Il drago è più grande dello slime
            e_h = 160

        queue.append([e_type, hp, espeed, e_w, e_h])
    return queue


def spawn_one(entry, enemies, SCREEN_W, SCREEN_H):
    """
    Aggiunge un nemico alla lista enemies, spawnandolo su un bordo casuale dello schermo.

    Argomenti:
        entry:    Lista [e_type, hp, espeed, e_w, e_h] che descrive il nemico da spawnare,
                  come prodotta da build_spawn_queue().
        enemies:  Lista dei nemici attivi in gioco; il nuovo nemico viene aggiunto in coda.
        SCREEN_W: Larghezza dello schermo in pixel.
        SCREEN_H: Altezza dello schermo in pixel.
    """
    # Sceglie casualmente uno dei 4 lati dello schermo come punto di spawn
    # così i nemici arrivano da direzioni imprevedibili
    side = random.choice(["T", "B", "L", "R"])
    # Calcolo coordinata X
    if side in ["T", "B"]:
        # se lospawn avviene da sopra o sotto, la X è casuale lungo tutta la larghezza
        ex = random.randint(0, SCREEN_W)
    else:
        if side == "L":
            ex = 0  # Bordo sinistro: X = 0
        else:
            ex = SCREEN_W  # Bordo destro: X = larghezza schermo

    # Calcolo coordinata Y
    if side in ["L", "R"]:
        # se spawn dal bordo sinistro o destro, la Y è casuale lungo tutta l'altezza
        ey = random.randint(0, SCREEN_H)
    else:
        if side == "T":
            ey = 0  # Bordo superiore: Y = 0
        else:
            ey = SCREEN_H  # Bordo inferiore: Y = altezza schermo

    # aggiungo le informazioni sul nemico alla lista completa
    # 0-1. coordinate del nemico
    # 2. hp del nemico
    # 3. tipologia nemico
    # 4-5. larghezza/altezza nemico
    # 6. frame index
    # 7. velocità di movimento
    # 8. contatore anim. danno
    enemies.append([ex, ey, entry[1], entry[0], entry[3], entry[4], 0.0, entry[2], 0])


# --- FUNZIONI CLASSIFICA/SALVATAGGIO DEL GIOCO
# creo l'oggetto platformdirs per la mia app
# creo il path per il file aggiunto
# lo metto nella direcotry dell'APP sull'Utente
# PlatformDirs trova automaticamente la cartella giusta su ogni sistema operativo
# ensure_exists=True crea la cartella se non esiste già
dirs = PlatformDirs("CrimsonGuard", ensure_exists=True)

#  / su un Path è l'equivalente di os.path.join unisce il percorso base con il nome file
# inseriamo il file classifica nella directory dell'app sull'utente in locale
CLASSIFICA_FILE = dirs.user_data_path / "classifica.txt"


def chiave_modalita(settings):
    """Crea per ogni set di parametri di gioco una chiave,
      sequenza di riconoscimento.

    Esempio: 4-8-12-25-300-50-2-80-2.5-100-... (tutti i valori separati da -)
    Serve per separare le classifiche di giocatori con impostazioni diverse
    (altrimenti sarebbe ingiusto confrontare partite con difficoltà diverse)
    """
    parti = []
    for v in settings:
        parti.append(str(round(v, 2)))
    return "-".join(parti)


def salva_partita(nickname, wave, nemici, minuti, secondi, coltelli, settings):
    """Aggiunge una riga al file classifica.txt

    Argomenti:
        nickname: stringa del nome digitata dal player
        wave: numero di wave raggiunta
        nemici: statistica di gioco
        minuti: statistica di gioco
        secondi: statistica di gioco
        coltelli: statistica di gioco
        settings: impostazioni generali della partita
    """

    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    nickname = nickname[
        :9
    ]  # Tronca il nickname a 9 caratteri per evitare righe troppo lunghe nel file
    # crea la riga formattata per allineare le colonne nel file di testo
    # :>3 = allinea a destra in un campo largo 3, :<3 = allinea a sinistra in campo largo 3
    riga = f"{data} | {nickname:<3} | Wave: {wave:>3} | Nemici: {nemici:>4} | Durata: {minuti:02d}:{secondi:02d} | Coltelli: {coltelli:>4}\n"
    chiave = chiave_modalita(settings)
    # L'intestazione è il "separatore di sezione" nel file: ogni modalità ha il suo blocco
    intestazione = f"[MODALITA:{chiave}]\n"

    # leggo tutto il file esistente
    if os.path.exists(CLASSIFICA_FILE):
        # encoding indica come i caratteri sono identificati in byte nel file txt
        # utf è il tipo di encoding più diffuso
        f = open(CLASSIFICA_FILE, "r", encoding="utf-8")
        contenuto = f.readlines()
        f.close()
    else:
        contenuto = []  # Se il file non esiste ancora, partiamo con lista vuota

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

            # scorre tutte le righe del blocco di questa modalità (fino alla prossima intestazione)
            while i < len(contenuto) and not contenuto[i].startswith("[MODALITA:"):
                nuove_righe.append(contenuto[i])
                i += 1
            # Inserisce la nuova riga di partita alla fine del blocco della modalità
            nuove_righe.append(riga)
            continue
        i += 1

    # se la modalità non esiste, la aggiungo in fondo
    if not trovata:
        nuove_righe.append(
            intestazione
        )  # Prima scrivi l'intestazione della nuova modalità
        nuove_righe.append(riga)  # Poi la prima riga di punteggio per questa modalità

    # Riscrive l'intero file con il contenuto aggiornato
    # sovrascrittura completa, non append, per poter inserire la riga nel posto giusto
    f = open(CLASSIFICA_FILE, "w", encoding="utf-8")
    # wirtelines scrive una lista di stringhe, concatenandole, invece di write che scrive solo una stringa
    f.writelines(nuove_righe)
    f.close()


def carica_classifica(sets, max_righe=8):
    """Legge le ultime max_righe dal file classifica

    Argomenti:
        max_righe: numero di righe lette
        sets: settings della partita
    """
    if not os.path.exists(CLASSIFICA_FILE):
        return []  # Se il file non esiste restituisce lista vuota (nessuna partita salvata)

    f = open(CLASSIFICA_FILE, "r", encoding="utf-8")
    contenuto = f.readlines()
    f.close()

    # se prosegue, vuol dire ci sono dei settings
    chiave = chiave_modalita(sets)
    intestazione = f"[MODALITA:{chiave}]\n"

    # trovo il blocco della modalità corrente
    righe_modalita = []
    dentro = (
        False  # variabile che indica se siamo dentro il blocco della modalità cercata
    )
    for r in contenuto:
        if r == intestazione:
            dentro = True  # trovata l'intestazione quindi inizia a raccogliere le righe
            continue  # salta l'intestazione stessa, non va inclusa nei risultati
        if r.startswith("[MODALITA:") and dentro:
            break  # Trovata l'intestazione di un'altra modalità: fine del blocco cercato

        # r.strip() è un controllo per la riga non vuota
        if dentro and r.strip():
            righe_modalita.append(r.rstrip("\n"))

    if max_righe is None:
        return righe_modalita  # Ritorna tutto senza limite (usato internamente da carica_top_classifica)
    return righe_modalita[-max_righe:]  # Ritorna solo le ultime N righe del blocco


def carica_top_classifica(sets, max_righe=8):
    """
    Legge le partite salvate per la modalità corrente e restituisce le migliori per wave raggiunta.

    Argomenti:
        sets:      Lista delle impostazioni di gioco, usata per identificare
                   il blocco di modalità corretto nel file classifica.
        max_righe: Numero massimo di partite da restituire (default: 8).

    Returns:
        Lista di stringhe (fino a max_righe) ordinate per wave decrescente,
        nel formato prodotto da salva_partita(). Lista vuota se non ci sono partite salvate.
    """
    righe = carica_classifica(sets, max_righe=None)
    # se è vuota, non torna nulla
    if not righe:
        return []

    # estraggo il numero di wave da ogni riga (formato: "... | Wave: NNN | ...")
    def estrai_orda(riga):
        # Divide la riga in parti usando "|" come separatore
        # La parte [2] è quella che contiene "Wave: NNN"
        parte_wave = riga.split("|")[2]
        # Divide ulteriormente per ":" per ottenere solo il numero
        numero = parte_wave.split(":")[1]
        return numero

    # key è il parametro(numero di orda) su cui mi baso per l'ordine crescente
    # con reverse inverto la lista (ordine decrescente)
    # il confronto è su stringhe, ma funziona correttamente finché i numeri
    # hanno lo stesso numero di cifre (padding garantito dal formato ":>3" in salva_partita)
    righe.sort(key=estrai_orda, reverse=True)

    if len(righe) <= max_righe:
        return (
            righe  # se ci sono meno righe rispetto al massimo allora restituisce tutto
        )

    # Estrae solo le prime max_righe (le migliori, già ordinate per wave decrescente)
    migliori = []
    for pos in range(max_righe):
        migliori.append(righe[pos])
    return migliori


def disegna_classifica(
    screen,
    font_wave,
    font_health,
    font_small,
    SCREEN_W,
    SCREEN_H,
    classifica,
    nickname="",
    mostra_top=False,
    GameEnd=True,
):
    """
    Disegna la schermata classifica con le partite salvate e il pulsante switch.
    Usata sia nella schermata di game over che nella schermata iniziale.

    Argomenti:
        screen:      Superficie pygame su cui disegnare.
        font_wave:   Font grande per il titolo "CLASSIFICA".
        font_health: Font medio per le etichette di sezione.
        font_small:  Font piccolo per le righe della classifica e i suggerimenti.
        SCREEN_W:    Larghezza dello schermo in pixel.
        SCREEN_H:    Altezza dello schermo in pixel.
        classifica:  Lista di stringhe, una per partita, nel formato prodotto da carica_classifica().
        nickname:    Nickname del giocatore corrente; la sua riga viene evidenziata in giallo.
                     Stringa vuota se non applicabile (default: "").
        mostra_top:  Se True mostra la Top 8 per wave, altrimenti le ultime 8 partite (default: False).
        GameEnd:     Se True mostra i tasti per ricominciare/uscire (contesto game over),
                     altrimenti solo ESC per chiudere (contesto schermata iniziale) (default: True).

    Returns:
        pygame.Rect del pulsante switch, da usare nel loop chiamante per rilevare i click.
    """
    cx = SCREEN_W // 2  # centro orizzontale dello schermo

    # il secondo parametro, True, rende la scritta meno pixelosa
    titolo = font_wave.render("CLASSIFICA", True, (255, 220, 60))
    screen.blit(
        titolo, (cx - titolo.get_width() // 2, 40)
    )  # centra il titolo orizzontalmente

    # linea verticale per separare visivamente la colonna dati sinistri
    pygame.draw.line(
        screen, (120, 120, 120), (cx - 320, 120), (cx - 320, SCREEN_H - 80), 1
    )

    # etichetta modalità corrente
    if mostra_top:
        label = font_health.render("Top 8 per Wave:", True, (180, 220, 255))
    else:
        label = font_health.render("Ultime 8 partite:", True, (180, 220, 255))
    screen.blit(label, (cx - 300, 130))

    i = 0
    for riga in classifica:
        # Divide la riga in parti separate da "|" e rimuove gli spazi iniziali/finali da ciascuna
        parti = []
        for p in riga.split("|"):
            parti.append(p.strip())
        colore = (200, 200, 200)  # colore di default: grigio chiaro

        # Se il nickname del giocatore corrente è presente nella riga, la evidenzia in giallo
        for parte in parti:
            if nickname and parte == nickname.strip():
                colore = (255, 255, 100)  # Giallo per la riga del giocatore corrente
                break

        s = font_small.render(riga, True, colore)
        screen.blit(s, (cx - 300, 165 + i * 34))  # Ogni riga ha un'altezza di 34 pixel
        i += 1

    # pulsante switch: alterna tra "Ultime 8" e "Top 8 per Wave"
    if mostra_top:
        btn_label = font_small.render("[ Ultime 8 ]", True, (255, 220, 60))
    else:
        btn_label = font_small.render("[ Top 8 Wave ]", True, (255, 220, 60))
    # Il rettangolo del pulsante si adatta automaticamente alla larghezza del testo + padding (spazio del bottone oltre al testo) di 16px
    switch_rect = pygame.Rect(cx + 260, 125, btn_label.get_width() + 16, 30)
    pygame.draw.rect(
        screen, (60, 60, 90), switch_rect, border_radius=5
    )  # Sfondo del pulsante
    pygame.draw.rect(
        screen, (180, 180, 100), switch_rect, 1, border_radius=5
    )  # Bordo del pulsante
    screen.blit(
        btn_label, (switch_rect.x + 8, switch_rect.y + 5)
    )  # testo con padding 8px

    # mostra istruzioni diverse in base al contesto: game over o schermata iniziale
    if GameEnd:
        hint = font_small.render(
            "SPAZIO per ricominciare  |  ESC per uscire", True, (160, 160, 160)
        )

    else:
        hint = font_small.render("ESC per chiudere", True, (160, 160, 160))

    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 50))

    # Restituisce il rettangolo del pulsante switch perché il loop chiamante deve sapere dove si trova per rilevare i click del mouse
    return switch_rect


def disegna_istruzioni(screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H):
    """
    Disegna la schermata istruzioni/tutorial con le spiegazioni dei controlli e delle meccaniche.

    Argomenti:
        screen:      Superficie pygame su cui disegnare.
        font_wave:   Font grande per il titolo "COME SI GIOCA".
        font_health: Font medio per i titoli di sezione (OBIETTIVO, MOVIMENTO, ecc.).
        font_small:  Font piccolo per il testo descrittivo e il suggerimento ESC.
        SCREEN_W:    Larghezza dello schermo in pixel.
        SCREEN_H:    Altezza dello schermo in pixel.
    """
    cx = SCREEN_W // 2

    titolo = font_wave.render("COME SI GIOCA", True, (255, 220, 60))
    screen.blit(titolo, (cx - titolo.get_width() // 2, 30))

    # Ogni tupla è (testo, colore): le intestazioni di sezione sono in arancione,
    # il testo normale è in un tipo di bianco , le stringhe vuote aggiungono spazio
    righe = [
        ("OBIETTIVO", (255, 180, 60)),
        (
            "Uccidi i mostri prima che raggiungano il tempio al centro della mappa.",
            (220, 220, 180),
        ),
        (
            "Quando i mostri sono vicini al tempio lo attaccano, riducendone gli HP.",
            (220, 220, 180),
        ),
        ("Se gli HP del tempio arrivano a zero: GAME OVER.", (220, 220, 180)),
        ("", (255, 255, 255)),
        ("ORDE", (255, 180, 60)),
        (
            "Man mano che uccidi nemici, le orde si fanno sempre più numerose.",
            (220, 220, 180),
        ),
        (
            "Inoltre, più vai avanti con le orde, più i mostri saranno forti e resistenti.",
            (220, 220, 180),
        ),
        ("", (255, 255, 255)),
        ("MOVIMENTO", (255, 180, 60)),
        ("WASD  /  Frecce direzionali:   corri sulla mappa", (220, 220, 180)),
        ("Tieni premuto SHIFT mentre ti muovi:   cammina lentamente", (220, 220, 180)),
        ("", (255, 255, 255)),
        ("ATTACCARE", (255, 180, 60)),
        (
            "Orb rotanti:  colpiscono automaticamente i nemici che toccano.",
            (220, 220, 180),
        ),
        (
            "Coltelli:   premi/tieni premuto TASTO SINISTRO del mouse per lanciare un coltello.",
            (220, 220, 180),
        ),
        (
            "            I coltelli volano verso il puntatore del mouse.",
            (220, 220, 180),
        ),
        ("", (255, 255, 255)),
        ("ALTRO", (255, 180, 60)),
        ("ESC:   chiude il gioco in qualsiasi momento", (220, 220, 180)),
    ]

    y = 120
    for testo, colore in righe:
        if testo == "":
            y += 10  # Aggiunge solo uno spazio verticale per separare le sezioni
            continue
        # titoli di sezione in font_health, resto in font_small
        if colore == (255, 180, 60):
            surf = font_health.render(testo, True, colore)
        else:
            surf = font_small.render(testo, True, colore)
        screen.blit(surf, (cx - surf.get_width() // 2, y))
        y += surf.get_height() + 6  # Avanza Y di altezza testo + 6px di margine

    hint = font_small.render("ESC per chiudere", True, (160, 160, 160))
    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 50))


def disegna_settings(
    screen,
    font_wave,
    font_health,
    font_small,
    SCREEN_W,
    SCREEN_H,
    icon_plus,
    icon_minus,
    settings,
):
    """
    Disegna la schermata impostazioni con tutti i parametri modificabili tramite pulsanti + e -.

    Argomenti:
        screen:      Superficie pygame su cui disegnare.
        font_wave:   Font grande per il titolo "IMPOSTAZIONI".
        font_health: Font medio per i nomi dei parametri e i loro valori.
        font_small:  Font piccolo per il suggerimento ESC.
        SCREEN_W:    Larghezza dello schermo in pixel.
        SCREEN_H:    Altezza dello schermo in pixel.
        icon_plus:   Superficie pygame con l'icona del pulsante "+".
        icon_minus:  Superficie pygame con l'icona del pulsante "-".
        settings:    Lista delle impostazioni di gioco da visualizzare e modificare.

    Returns:
        Lista di coppie (rect_minus, rect_plus) per ogni parametro,
        da usare nel loop chiamante per rilevare i click sui pulsanti.
    """
    cx = SCREEN_W // 2

    titolo = font_wave.render("IMPOSTAZIONI", True, (255, 220, 60))
    screen.blit(titolo, (cx - titolo.get_width() // 2, 30))

    # Nomi leggibili per ciascun parametro della lista settings[]
    # L'ordine deve corrispondere esattamente agli indici di settings[]
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
        "Volume musica",
    ]

    # cifre decimali di ogni parametro
    # Ogni indice corrisponde alla voce nella lista voci[] sopra
    # 0 = nessun decimale (numero intero), 1 = 1 decimale, 2 = 2 decimali
    decimali = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0, 2, 1, 0, 1, 2, 2]

    # colonna sinistra: indici 0-8, colonna destra: indici 9-17
    col_x = [cx - 580, cx + 20]  # x di partenza testo per ogni colonna
    btn_x = [cx - 130, cx + 470]  # x di partenza pulsanti per ogni colonna

    btn_rects = []  # Raccoglierà le coppie (rect_minus, rect_plus) per rilevare i click
    y_start = 110  # Y del primo parametro
    y_step = 52  # Distanza verticale tra un parametro e il successivo

    for i in range(20):
        # I parametri 0-9 vanno nella colonna sinistra, 10-19 nella destra
        if i < 10:
            colonna = 0
        else:
            colonna = 1
        # La riga reset a 0 quando si passa alla seconda colonna
        if i < 10:
            riga = i
        else:
            riga = i - 10
        y = y_start + riga * y_step

        # Formatta il valore con il numero di decimali appropriato per questo parametro
        if decimali[i] > 0:
            valore_str = f"{settings[i]:.{decimali[i]}f}"
        else:
            valore_str = str(settings[i])
        testo = font_small.render(f"{voci[i]}:  {valore_str}", True, (220, 220, 180))
        screen.blit(testo, (col_x[colonna], y))

        # I pulsanti - e + sono affiancati: il + è spostato di 36px a destra del -
        r_minus = pygame.Rect(btn_x[colonna], y, 32, 28)
        r_plus = pygame.Rect(btn_x[colonna] + 36, y, 32, 28)

        # Disegna lo sfondo e il bordo di entrambi i pulsanti in stile identico
        for r in [r_minus, r_plus]:
            pygame.draw.rect(screen, (70, 70, 100), r, border_radius=5)  # Sfondo
            pygame.draw.rect(screen, (180, 180, 220), r, 1, border_radius=5)  # Bordo
        # Sovrappone le icone grafiche (caricate dallo spritesheet ) sui pulsanti
        screen.blit(icon_minus, (r_minus.x + 0, r_minus.y - 2))
        screen.blit(icon_plus, (r_plus.x + 0, r_plus.y - 2))

        btn_rects.append((r_minus, r_plus))  # Salva la coppia per il rilevamento click

    # linea divisoria verticale tra le due colonne
    pygame.draw.line(
        screen, (100, 100, 140), (cx - 10, 100), (cx - 10, SCREEN_H - 60), 1
    )

    hint = font_small.render("ESC per chiudere", True, (160, 160, 160))
    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 40))

    # Restituisce i rect dei pulsanti perché il loop chiamante deve rilevare i click su di essi
    return btn_rects


# ---------------------------------------------------------------------------------------#
# funzione run del gioco


def main() -> None:
    pygame.init()

    # ===================== AGGIUNTA AUDIO =====================
    pygame.mixer.init()
    # pygame.mixer gestisce l'audio. init() va chiamato separatamente da pygame.init()
    # perché potrebbe non essere disponibile su tutti i sistemi (es. headless server)

    MUSICA_MENU = files("giocopaolettiamadio") / "materiali" / "danzadellelame.mp3"
    MUSICA_GIOCO = files("giocopaolettiamadio") / "materiali" / "danzadellelame2.mp3"
    musica_corrente = ""  # tiene traccia di quale file è caricato
    # la variabile musica_corrente evita di ricaricare e riavviare la traccia audio, si ricarica solo quando cambia l'audio

    # FINESTRA
    SCREEN_W, SCREEN_H = 1344, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Crimson Guard")
    clock = pygame.time.Clock()  #  per limitare gli FPS e misurare il tempo trascorso

    # ================== SCHERMATA INIZIALE (caricata una volta sola) ==================
    start_screen_img = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "schermataI.png"
    ).convert_alpha()
    start_screen_img = pygame.transform.scale(start_screen_img, (SCREEN_W, SCREEN_H))
    # Rettangolo clickable per il pulsante "Start": definisce l'area sensibile al click
    START_BUTTON_RECT = pygame.Rect(522, 600, 300, 90)

    # --- PULSANTE (schermata iniziale) ---
    # r -> raw string -> faccio capire a python che deve interpretare \ in modo letterale
    # Senza la r, Python interpreterebbe \U, \S ecc. come sequenze di escape Unicode
    ui_sheet = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "UI_grey_buttons_1.png"
    ).convert_alpha()
    # ogni icona è 16x16 pixel nello sheet;
    icon_size = 16

    # icona per la classifica
    # considerando la prima colonna/riga come 'zero' come nelle liste
    # prendo riga 0 colonna 4 (icona lista/elenco)
    # subsurface() ritaglia un'area precisa del foglio UI usando coordinate in pixel
    icon_raw = ui_sheet.subsurface(
        pygame.Rect(4 * icon_size, 0 * icon_size, icon_size, icon_size)
    )
    # scala l'icona con la funzione da 16x16 a 48x48 pixel per renderla visibile nell'interfaccia
    icon_img = pygame.transform.scale(icon_raw, (48, 48))
    CLASSIFICA_BTN_RECT = pygame.Rect(SCREEN_W - 80, SCREEN_H - 80, 60, 60)

    # carico le icone + e - dallo sheet
    icon_plus_raw = ui_sheet.subsurface(
        pygame.Rect(0 * icon_size, 5 * icon_size, icon_size, icon_size)
    )
    icon_minus_raw = ui_sheet.subsurface(
        pygame.Rect(1 * icon_size, 5 * icon_size, icon_size, icon_size)
    )
    icon_plus = pygame.transform.scale(icon_plus_raw, (32, 32))
    icon_minus = pygame.transform.scale(icon_minus_raw, (32, 32))

    # icona per le istruzioni (riga 5, colonna 4 nella foto degli sheets)
    icon_raw_info = ui_sheet.subsurface(
        pygame.Rect(4 * icon_size, 5 * icon_size, icon_size, icon_size)
    )
    icon_img_info = pygame.transform.scale(icon_raw_info, (48, 48))
    INFO_BTN_RECT = pygame.Rect(SCREEN_W - 80, SCREEN_H - 150, 60, 60)

    # icona per i settings (riga 2, colonna 3 dello sheet)
    icon_raw_settings = ui_sheet.subsurface(
        pygame.Rect(3 * icon_size, 2 * icon_size, icon_size, icon_size)
    )
    icon_img_settings = pygame.transform.scale(icon_raw_settings, (48, 48))
    SETTINGS_BTN_RECT = pygame.Rect(
        SCREEN_W - 80, SCREEN_H - 220, 60, 60
    )  # sopra il pulsante info

    # --- COSTANTI PERSONAGGIO ---
    FRAME_SIZE_samurai = 256  # ogni frame nello spritesheet è 256x256 pixel
    ANIM_SPEED = (
        0.15  # Incremento dell'indice di animazione per frame (più alto = più veloce)
    )
    SPEED_WALK = 4  # velocità (in pixel/frame) in modalità camminata (con SHIFT)
    SPEED_RUN = 8  # velocità (in pixel/frame) in modalità corsa (senza SHIFT)

    # --- COSTANTI ORB ---
    ORB_ORBIT_RADIUS = (
        80  # raggio in pixel dell'orbita delle sfere circolare attorno al samurai
    )
    ORB_RADIUS = 12  # raggio visivo dell'orb (per collision e disegno)
    ORB_SPEED = 2.5  # velocità angolare in radianti al secondo
    ORB_DAMAGE = 50  # danno inflitto al nemico ad ogni contatto
    ORB_DAMAGE_COOLDOWN = 30  # frame di invincibilità dopo un colpo di orb (evita danni multipli istantanei)
    ORB_NUM = 2  # numero di sfere che ruotano attorno al personaggio

    # --- COSTANTI COLTELLI ---
    KNIFE_SPEED = 12  # velocità di avanzamento del coltello
    KNIFE_DAMAGE = 25  # Danno inflitto al nemico al momento dell'impatto
    KNIFE_COOLDOWN = 18  # Frame di attesa obbligatoria tra un lancio e il successivo
    KNIFE_LENGTH = 18  # Metà lunghezza visiva della lama in pixel
    KNIFE_WIDTH = 3  # Metà larghezza visiva della lama in pixel
    KNIFE_MAX_RANGE = (
        300  # Distanza massima percorribile dal coltello prima di scomparire
    )

    # --- COSTANTI ORDE ---
    PAUSE_DURATION = 4000  # millisecondi di pausa tra un'orda e la successiva
    SPAWN_INTERVAL = 400  # millisecondi tra la comparsa di un nemico e il successivo

    # --- COSTANTI MOSTRI ---
    SLIME_HP = 30  # HP base degli slime (aumentano con il numero di orde)
    DRAGON_HP = 50  # HP base dei draghi (aumentano con il numero di orde)
    SLIME_SPEED = 2.0  # Velocità (pixel per frame) degli slime
    DRAGON_SPEED = 1.2  # Velocità (pixel per frame) dei draghi
    SLIME_DAMAGE = 0.05  # danno per frame al tempio quando uno slime è adiacente
    DRAGON_DAMAGE = 0.07  # draghi fanno più danno per frame rispetto agli slime

    # -- costante shrine ---
    shrine_max_hp = 100

    # --- durata danno in game ---
    HIT_FLASH_DURATION = (
        8  # frame per cui l'effetto rosso rimane visibile sul nemico colpito
    )

    # --- coefficiente difficoltà crescente del gioco ---
    COEFF_DIF = 2  # Moltiplicatore base per la scalatura della difficoltà tra le wave

    # --- probabilità massimo di spawn del drago in percentuale
    prob_dragon_max = (
        0.7  # 70% di probabilità massima: anche in late game ci sono slime
    )

    # --- volume musica in game ---
    STANDARD_VOLUME = 0.5  # Volume di default (0.0 = muto, 1.0 = massimo)

    # --- SETTINGS MODIFICABILI DA UI ---
    # Lista centralizzata di tutti i parametri del gioco modificabili dal menu settings
    # L'ordine degli elementi deve corrispondere esattamente alle voci nella funzione disegna_settings()
    settings = [
        SPEED_WALK,  # [0]  Velocità camminata
        SPEED_RUN,  # [1]  Velocità corsa
        KNIFE_SPEED,  # [2]  Velocità coltelli
        KNIFE_DAMAGE,  # [3]  Danno coltello
        KNIFE_MAX_RANGE,  # [4]  Portata coltelli
        ORB_DAMAGE,  # [5]  Danno orb
        ORB_NUM,  # [6]  Numero di orb
        ORB_ORBIT_RADIUS,  # [7]  Raggio orbita orb
        ORB_SPEED,  # [8]  Velocità orb
        shrine_max_hp,  # [9]  HP massimi del tempio
        DRAGON_HP,  # [10] HP draghi
        DRAGON_DAMAGE,  # [11] Danno draghi al tempio
        DRAGON_SPEED,  # [12] Velocità draghi
        SLIME_HP,  # [13] HP slime
        SLIME_DAMAGE,  # [14] Danno slime al tempio
        SLIME_SPEED,  # [15] Velocità slime
        PAUSE_DURATION,  # [16] Pausa tra le orde in ms
        COEFF_DIF,  # [17] Coefficiente di crescita difficoltà
        prob_dragon_max,  # [18] Probabilità massima spawn draghi
        STANDARD_VOLUME,  # [19] Volume della musica
    ]

    # --- CARICAMENTO ASSET (una volta sola) ---
    # Gli asset vengono caricati qui fuori dal loop principale
    backstage = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "StageRettangolare.png"
    ).convert_alpha()
    backstage = pygame.transform.scale(backstage, (SCREEN_W, SCREEN_H))

    # shrine_75 viene caricato prima degli altri perché shrine_rect si calcola da esso
    shrine_75 = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "Tempio75hpRifilato.png"
    ).convert_alpha()
    shrine_75 = pygame.transform.scale(
        shrine_75, (int(shrine_75.get_width() * 0.5), int(shrine_75.get_height() * 0.5))
    )
    # get_rect(center=...) crea un Rect posizionato con il centro al centro dello schermo
    shrine_rect = shrine_75.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))

    # load_shrine_state riscala ogni immagine in modo che la larghezza sia identica a shrine_rect.width
    # così tutte le versioni del tempio si sovrappongono 'perfettamente' durante la visualizzazione
    shrine_100 = load_shrine_state(
        files("giocopaolettiamadio") / "materiali" / "Tempio1nosfondo.png", shrine_rect
    )
    shrine_50 = load_shrine_state(
        files("giocopaolettiamadio") / "materiali" / "Tempio50hpRifilato.png",
        shrine_rect,
    )
    shrine_25 = load_shrine_state(
        files("giocopaolettiamadio") / "materiali" / "Tempio25hpRifilato.png",
        shrine_rect,
    )
    shrine_0 = load_shrine_state(
        files("giocopaolettiamadio") / "materiali" / "Tempio0hpRifilato.png",
        shrine_rect,
    )

    lista_shrine = [shrine_100, shrine_75, shrine_50, shrine_25, shrine_0]

    # --- CARICAMENTO SAMURAI ---
    # get_samurai_frames carica e riscala al 50% l'intero set di animazione
    # frames per la posizione ferma
    frames_idle_right = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "Samurai-idle-v1.png",
        FRAME_SIZE_samurai,
    )

    # Per i frame verso sinistra non serve un file separato: si specchiano orizzontalmente quelli verso destra
    frames_idle_left = []
    for f in frames_idle_right:
        frame_flippato = pygame.transform.flip(
            f, True, False
        )  # pygame.transform.flip(superficie, flip_orizzontale, flip_verticale)
        frames_idle_left.append(frame_flippato)

    # frames per la camminata
    frames_walk_up = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiUpgiusto.png",
        FRAME_SIZE_samurai,
    )
    frames_walk_down = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiDowngiusto.png",
        FRAME_SIZE_samurai,
    )
    frames_walk_right = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiDxgiusto.png",
        FRAME_SIZE_samurai,
    )

    # Anche per camminata a sinistra: flip orizzontale di camminata a destra
    frames_walk_left = []
    for f in frames_walk_right:
        frame_flippato = pygame.transform.flip(f, True, False)
        frames_walk_left.append(frame_flippato)

    # frames per la corsa
    frames_run_up = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiRunUpgiusto.png",
        FRAME_SIZE_samurai,
    )
    frames_run_down = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiRunDowngiusto.png",
        FRAME_SIZE_samurai,
    )
    frames_run_right = get_samurai_frames(
        files("giocopaolettiamadio") / "materiali" / "SamuraiRunDxgiusto.png",
        FRAME_SIZE_samurai,
    )

    # Corsa a sinistra: flip orizzontale di corsa a destra
    frames_run_left = []
    for f in frames_run_right:
        frame_flippato = pygame.transform.flip(f, True, False)
        frames_run_left.append(frame_flippato)

    # --- CARICAMENTO NEMICI ---
    slime_sheet = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "SlimeSpriteSheet.png"
    ).convert_alpha()
    # Lo slime ha 1 riga e 4 colonne nello spritesheet, frame originali 32x32, scalati 2.5x = 80x80
    frames_slime = rescale_frames(load_frames(slime_sheet, 1, 4, 32, 32), 2.5)

    dragon_sheet = pygame.image.load(
        files("giocopaolettiamadio") / "materiali" / "Baby_Dragon_2D.png"
    ).convert_alpha()
    # Il drago ha 2 righe e 2 colonne nello spritesheet, frame 64x64, scalati 2.5x = 160x160
    frames_dragon_left = rescale_frames(load_frames(dragon_sheet, 2, 2, 64, 64), 2.5)
    # Il drago guarda a sinistra per default; per averlo a destra lo rovesciamo
    frames_dragon_right = []
    for f in frames_dragon_left:
        frame_flippato = pygame.transform.flip(f, True, False)
        frames_dragon_right.append(frame_flippato)

    font_health = pygame.font.Font(
        None, 36
    )  # Font medio per etichette HP e statistiche
    font_wave = pygame.font.Font(None, 72)  # Font grande per titoli e annunci di wave
    font_small = pygame.font.Font(
        None, 30
    )  # Font piccolo per testi secondari e classifica

    # LOOP ESTERNO: schermata iniziale → partita → game over → torna all'inizio
    # Questo while True permette di ricominciare una nuova partita senza riavviare il programma
    # ==================================================================================
    while True:
        # Avvia la musica del menu solo se non stava già suonando
        # Questo controllo evita di ricaricare/riavviare il file audio ogni volta che il loop esterno ripassa dall'inizio (es. dopo un game over)

        if musica_corrente != MUSICA_MENU:
            musica_corrente = MUSICA_MENU
            pygame.mixer.music.load(MUSICA_MENU)
            # settings[19] è il volume preimpostato, valore tra 0.0 e 1.0
            pygame.mixer.music.set_volume(settings[19])
            pygame.mixer.music.play(-1)  # -1 = loop infinito

        # ================== SCHERMATA INIZIALE ==================
        in_start_screen = True  # True quando si è nella schermata d'avvio
        mostra_classifica_start = False  # True quando l'overlay classifica è visibile
        mostra_top_start = False  # True se si mostra la Top 8, False per le ultime 8
        switch_rect_start = None  # Rect del pulsante switch (aggiornato ogni frame)
        mostra_istruzioni = False  # True quando l'overlay istruzioni è visibile
        mostra_settings = False  # True quando l'overlay settings è visibile
        settings_btn_rects = []  # Lista di coppie (r_minus, r_plus) per ogni parametro

        # --- loop schermata iniziale ---
        while in_start_screen:
            clock.tick(60)  # Limita a 60 FPS e restituisce ms dall'ultimo tick

            for event in pygame.event.get():
                # 1° tipologia di uscita: QUIT (X rossa)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # sys.exit() termina l'intero programma in modo pulito, qualunque sia il punto di esecuzione in cui viene chiamato
                    # chiude anche più cicli insieme
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # 2° tipologia di uscita: tasto ESC
                    if event.key == pygame.K_ESCAPE:
                        # ESC chiude gli overlay aperti uno alla volta, o esce dal gioco se nessuno è aperto
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
                    # se il mouse clicca su start, inizia il gioco
                    # mi assicuro che nessun menù sia aperto per l'avvio del gioco
                    if (
                        not mostra_classifica_start
                        and not mostra_istruzioni
                        and not mostra_settings
                        and START_BUTTON_RECT.collidepoint(event.pos)
                    ):
                        in_start_screen = False  # Esce dal loop della schermata iniziale e avvia la partita
                    # Ogni pulsante laterale toglie gli altri overlay e attiva/disattiva il proprio
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

                    # Gestisce i click sui pulsanti + e - nei settings
                    # Viene eseguita solo se il pannello settings è visibile e i rect sono stati creati
                    if mostra_settings and settings_btn_rects:
                        i = 0
                        for r_minus, r_plus in settings_btn_rects:
                            # step diverso per pausa tra le orde
                            if i == 16:
                                step = 100  # La pausa si modifica a passi di 100ms

                            # step diverso per velocità mostri e velocità incremento orde
                            elif i == 8 or i == 12 or i == 15 or i == 17:
                                step = 0.1  # Velocità con 1 decimale

                            # step diverso per danni mostri, probabilità e volume
                            elif i == 11 or i == 14 or i == 18 or i == 19:
                                step = 0.01  # Danni e probabilità con 2 decimali

                            else:
                                step = 1  # Tutti gli altri parametri interi

                            # se si preme il meno, diminuisce il setting delo step
                            if r_minus.collidepoint(event.pos):
                                if i == 18 or i == 19:
                                    # la musica può arrivare anche a zero(muto)
                                    # la prob dei draghi può esser nulla(solo slime)
                                    # round evita errori di rappresentazione decimale (numero massimo dicifre dopo la virgola)
                                    settings[i] = round(max(0, settings[i] - step), 2)
                                else:
                                    # per il resto, il valore minimo è lo step
                                    # round evita errori di rappresentazione decimale
                                    settings[i] = round(
                                        max(step, settings[i] - step), 2
                                    )

                            # se si preme il più, aumenta il setting dello step
                            if r_plus.collidepoint(event.pos):
                                if i == 18 or i == 19:
                                    # max valore per il volmue musica è 1
                                    # la prob dei draghi è al massimo 1(100%)
                                    # round evita errori di rappresentazione decimale
                                    settings[i] = round(min(1.0, settings[i] + step), 2)
                                else:
                                    # per il resto, non ci sono massimi
                                    # round evita errori di rappresentazione decimale
                                    settings[i] = round(settings[i] + step, 2)

                            # Aggiorna il volume in tempo reale mentre si modifica il parametro
                            pygame.mixer.music.set_volume(settings[19])
                            i += 1

                    if mostra_classifica_start:
                        # alla pressione del rettangolo
                        if switch_rect_start and switch_rect_start.collidepoint(
                            event.pos
                        ):
                            mostra_top_start = (
                                not mostra_top_start
                            )  # Alterna tra le due modalità di vista

            # --- DISEGNO FRAME SCHERMATA INIZIALE ---
            screen.blit(start_screen_img, (0, 0))  # Disegna sempre lo sfondo come base

            if mostra_classifica_start:
                # Overlay semitrasparente: Surface con canale alpha, colore nero a 180/255 di opacità
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                if mostra_top_start:
                    # mostro le migliori 8 partite
                    classifica_dati = carica_top_classifica(settings)

                else:
                    # mostro le ultime 8 partite
                    classifica_dati = carica_classifica(settings)

                # funzione per disegnare la classifica: restituisce il rettangolo per lo switch tra i due stati
                switch_rect_start = disegna_classifica(
                    screen,
                    font_wave,
                    font_health,
                    font_small,
                    SCREEN_W,
                    SCREEN_H,
                    classifica_dati,
                    mostra_top=mostra_top_start,
                    GameEnd=False,
                )

            if mostra_istruzioni:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                # funzione per disegno istruzioni
                disegna_istruzioni(
                    screen, font_wave, font_health, font_small, SCREEN_W, SCREEN_H
                )

            if mostra_settings:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                # disegna_settings restituisce i rect dei pulsanti, aggiornati ogni frame
                # in caso le dimensioni cambino (es. testo più lungo dopo modifica valore)
                settings_btn_rects = disegna_settings(
                    screen,
                    font_wave,
                    font_health,
                    font_small,
                    SCREEN_W,
                    SCREEN_H,
                    icon_plus,
                    icon_minus,
                    settings,
                )

            # --- disegno pulsante classifica ---
            # Effetto hover: cambia colore se il mouse è sopra il pulsante
            if CLASSIFICA_BTN_RECT.collidepoint(pygame.mouse.get_pos()):
                btn_color = (80, 80, 120)
            else:
                btn_color = (50, 50, 90)
            # disegno lo sfondo quadrato del pulsante
            pygame.draw.rect(screen, btn_color, CLASSIFICA_BTN_RECT, border_radius=8)
            # disegno il bordo di 2px del pulsante
            pygame.draw.rect(
                screen, (180, 180, 220), CLASSIFICA_BTN_RECT, 2, border_radius=8
            )
            # disegno l'icona del pulsante
            screen.blit(
                icon_img, (CLASSIFICA_BTN_RECT.x + 6, CLASSIFICA_BTN_RECT.y + 6)
            )

            # --- disegno pulsante istruzioni ---
            if INFO_BTN_RECT.collidepoint(pygame.mouse.get_pos()):
                btn_color_info = (80, 80, 120)
            else:
                btn_color_info = (50, 50, 90)
            pygame.draw.rect(screen, btn_color_info, INFO_BTN_RECT, border_radius=8)
            pygame.draw.rect(screen, (180, 180, 220), INFO_BTN_RECT, 2, border_radius=8)
            screen.blit(icon_img_info, (INFO_BTN_RECT.x + 6, INFO_BTN_RECT.y + 6))

            # --- disegno pulsante settings ---
            if SETTINGS_BTN_RECT.collidepoint(pygame.mouse.get_pos()):
                btn_color_set = (80, 80, 120)
            else:
                btn_color_set = (50, 50, 90)
            pygame.draw.rect(screen, btn_color_set, SETTINGS_BTN_RECT, border_radius=8)
            pygame.draw.rect(
                screen, (180, 180, 220), SETTINGS_BTN_RECT, 2, border_radius=8
            )
            screen.blit(
                icon_img_settings, (SETTINGS_BTN_RECT.x + 6, SETTINGS_BTN_RECT.y + 6)
            )

            pygame.display.flip()  # Invia il frame completamente costruito al monitor (double buffering)

        # Passaggio menu → gioco: carica e avvia la musica di gioco
        musica_corrente = MUSICA_GIOCO
        pygame.mixer.music.load(MUSICA_GIOCO)
        pygame.mixer.music.play(-1)

        # ================== INIT VARIABILI DI GIOCO ==================
        # La macchina a stati dell'onda gestisce 3 fasi in sequenza:
        # WAVE_SPAWN → nemici escono uno a uno dalla coda → WAVE_ACTIVE → si aspetta che muoiano tutti → WAVE_PAUSE → countdown → WAVE_SPAWN (wave successiva)
        wave_state = "WAVE_SPAWN"
        current_wave = 1
        # prepara la lista dei nemici della prima wave
        spawn_queue = build_spawn_queue(
            calcola_orda(current_wave, sets=settings),
            settings[13],
            settings[10],
            settings[15],
            settings[12],
        )
        spawn_timer = 0
        pause_timer = 0

        shrine_current_hp = settings[
            9
        ]  # Inizializza gli HP del tempio al valore massimo configurato
        px, py = (
            (SCREEN_W - 128) // 2,
            (SCREEN_H) // 2,
        )  # Posizione iniziale del samurai: centro schermo, un po' ribassato, proprio sulla porta del tempio
        side_pg = "R"  # Direzione iniziale: guarda a destra
        frame_index = 0.0  # Indice float dell'animazione corrente
        current_frames = (
            frames_idle_right  # Animazione di default: fermo  che guarda verso destra
        )

        orb_angle = 0.0  # Angolo corrente di rotazione delle orb (in radianti)
        orb_hit_cooldowns = []  # Lista di [id_nemico, frames_rimasti]: traccia i nemici in cooldown dopo un colpo di orb
        orb_positions = []  # Lista di (x, y): posizioni aggiornate ogni frame di ogni orb

        knives = []  # Lista di coltelli attivi: ogni coltello è [x, y, vx, vy, surf, hs, distanza_percorsa]
        knife_timer = (
            0  # Countdown di frame prima che si possa sparare un altro coltello
        )

        enemies = []  # Lista di nemici attivi in gioco (vedi struttura in spawn_one)
        running = True  # False : esce dal loop principale di gioco
        game_over = False  # True : passa al loop di game over

        # --- STATISTICHE PARTITA ---
        nemici_uccisi = 0  # Contatore nemici eliminati
        coltelli_sparati = 0  # Contatore coltelli lanciati
        tempo_inizio = pygame.time.get_ticks()  # Timestamp di inizio partita in ms

        # ================== LOOP PRINCIPALE ==================
        while running:
            # dt = millisecondi trascorsi dall'ultimo frame; con 60 FPS ideali è ~16ms
            # Viene usato per calcoli indipendenti dal framerate (es. velocità orb)
            dt = clock.tick(60)

            # ciclo degli eventi
            for event in pygame.event.get():
                # comadni di uscita dal gioco: x rossa in alto e ESC
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if not game_over:
                keys = pygame.key.get_pressed()
                is_walking = (
                    keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                )  # Camminata = SHIFT tenuto premuto
                # settings[0] è speed_walk, settings[1] è speed_run
                if is_walking:
                    speed = settings[0]
                else:
                    speed = settings[1]
                moved = False  # Flag per sapere se il personaggio si è mosso in questo frame

                # --- MOVIMENTO ---

                if (
                    keys[pygame.K_w] or keys[pygame.K_UP]
                ):  # se si preme il tasto w o la freccia direzionale verso l'alto
                    py -= speed  # asse y diminuisce andando verso l'alto in python
                    if is_walking:  # se viene utilizzata quella combinazione di tasti per camminare allora:
                        current_frames = frames_walk_up  # cammina verso alto
                    else:
                        current_frames = frames_run_up  # sennò corre
                    moved = True
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    py += speed  # asse y aumenta andando verso il basso in python
                    if is_walking:
                        current_frames = frames_walk_down
                    else:
                        current_frames = frames_run_down
                    moved = True
                elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    px -= speed  # asse x dimuisce andando verso sinistra in python
                    side_pg = "L"  # personaggio rivolto verso sinistra
                    if is_walking:  # se cammina verso sx si utilizzano i frame, impostati precedentemente, del personaggio che cammina a sx
                        current_frames = frames_walk_left
                    else:
                        current_frames = (
                            frames_run_left  # altrimenti corre normalmente verso destra
                        )
                    moved = True
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    px += speed  # asse x aumenta andando verso destra in python
                    side_pg = "R"  # personaggio rivolto verso destra
                    if is_walking:  # se cammina verso dx si utilizzano i frame, impostati precedentemente, del personaggio che cammmina a dx
                        current_frames = frames_walk_right
                    else:
                        current_frames = frames_run_right  # altrimenti corre normalmente verso destra
                    moved = True

                # Se non ci si muove, torna all'animazione idle nella direzione corrente
                if not moved:
                    # controllo verso del personaggio
                    if side_pg == "R":
                        current_frames = frames_idle_right
                    else:
                        current_frames = frames_idle_left

                # La corsa usa frame_index che avanza più velocemente (×1.5) per un'animazione più rapida
                anim_speed = ANIM_SPEED if is_walking else ANIM_SPEED * 1.5
                frame_index += anim_speed
                # Quando si supera l'ultimo frame, si ricomincia dal primo (animazione in loop)
                if frame_index >= len(current_frames):
                    frame_index = 0

                # Limita il personaggio dentro i bordi dello schermo
                # I valori (90, SCREEN_W-218, 75, SCREEN_H-218) tengono conto delle dimensioni dello sprite
                px = max(90, min(px, SCREEN_W - 218))
                py = max(75, min(py, SCREEN_H - 218))

                # Centro del personaggio (offset 64 perché lo sprite è 128x128)
                pg_cx = px + 64
                pg_cy = py + 64

                # --- LANCIO COLTELLI ---
                if knife_timer > 0:
                    knife_timer -= (
                        1  # Decrementa il cooldown ogni frame finché non è zero
                    )

                # se il tasto sinistro del mouse è in pressione, ed il cooldown è terminato, spara
                if pygame.mouse.get_pressed()[0] and knife_timer == 0:
                    knife_timer = KNIFE_COOLDOWN  # Reimposta il cooldown
                    # posizione del mouse
                    mx, my = pygame.mouse.get_pos()
                    # atan2 calcola l'angolo in radianti verso il cursore del mouse partendo dal personaggio
                    angle = math.atan2(my - pg_cy, mx - pg_cx)
                    # Aggiorna la direzione del personaggio in base a dove si mira
                    if mx < pg_cx:
                        side_pg = "L"
                    else:
                        side_pg = "R"
                    # Decomposizione del vettore velocità nelle componenti X e Y
                    vx = math.cos(angle) * settings[2]
                    vy = math.sin(angle) * settings[2]
                    surf = make_knife_surface(angle, KNIFE_LENGTH, KNIFE_WIDTH)
                    hs = (
                        surf.get_width() // 2
                    )  # Metà larghezza superficie per centrare il disegno
                    # Struttura coltello: [x, y, vx, vy, superficie, half_size, distanza_percorsa]
                    knives.append([pg_cx, pg_cy, vx, vy, surf, hs, 0])
                    coltelli_sparati += 1

                    # --- AGGIORNA ORB ---
                # calcolo angolazione della orb
                # L'angolo aumenta proporzionalmente al tempo reale (dt/1000 = secondi)
                # così la velocità di rotazione è indipendente dagli FPS
                orb_angle += settings[8] * (dt / 1000.0)
                orb_positions = []

                # settings[6] è il numero delle orb
                for i in range(settings[6]):
                    # dividiamo il cerchio in tanti angoli congruenti  quante sono le orbe
                    # 2π = un giro completo, diviso per il numero di orb = angolo tra ciascuna
                    angs_equi = 2 * math.pi / settings[6]
                    # per ogni orb diversa, aggiungo l'angolo congruente all'angolo attuale delle orb
                    # math.cos(angolo): Ci dice quanto dobbiamo spostarci a DESTRA o SINISTRA dal centro, in proporzione
                    orb_dist_x = math.cos(orb_angle + i * angs_equi) * settings[7]
                    # math.sin(angolo): Ci dice quanto dobbiamo spostarci in ALTO o BASSO dal centro, in proporzione
                    orb_dist_y = math.sin(orb_angle + i * angs_equi) * settings[7]
                    # *settings[7](raggio dell'orbita) moltiplica il valore trovato con sin e cos per il raggio, lo allunga
                    # così la orb ha sempre la stessa distanza settings[7] dal cnetro del pg
                    # aggiungiamo le coordinate rispetto al centro del personaggio, pg_cx e pg_cy
                    orb_positions.append((pg_cx + orb_dist_x, pg_cy + orb_dist_y))

                # lista dei cooldown: intervallo di tempo del danno delle orb su un nemico
                # se il nemico è nella lista, non può subire danno dalle orb
                # Rimuove dalla lista di cooldown i nemici il cui timer è scaduto (frames_rimasti <= 0)
                # Viene costruita una nuova lista con solo gli elementi ancora validi
                new_orb_hit_cooldowns = []
                for entry in orb_hit_cooldowns:
                    entry[1] -= 1  # Decrementa il timer di cooldown
                    if entry[1] > 0:
                        new_orb_hit_cooldowns.append(
                            entry
                        )  # Mantieni solo quelli ancora attivi
                orb_hit_cooldowns = new_orb_hit_cooldowns

                # --- AGGIORNA COLTELLI ---
                for k in (
                    knives.copy()
                ):  # .copy() evita modifiche alla lista mentre la si itera
                    k[0] += k[2]  # Aggiorna X: x = x + velocità_x
                    k[1] += k[3]  # Aggiorna Y: y = y + velocità_y
                    k[6] += settings[
                        2
                    ]  # Accumula distanza percorsa (≈ velocità per frame)
                    # Rimuove il coltello se è uscito dallo schermo o ha superato la portata massima (cioè settings[4])
                    if (
                        k[0] < -60
                        or k[0] > SCREEN_W + 60
                        or k[1] < -60
                        or k[1] > SCREEN_H + 60
                        or k[6] >= settings[4]
                    ):
                        knives.remove(k)

                # --- MACCHINA A STATI ORDE ---
                # Gestisce il ciclo di vita di ogni ondata attraverso 3 stati
                if wave_state == "WAVE_SPAWN":
                    spawn_timer += dt  # Accumula ms dall'ultimo spawn
                    if spawn_timer >= SPAWN_INTERVAL and spawn_queue:
                        spawn_timer = 0
                        spawn_one(
                            spawn_queue.pop(0), enemies, SCREEN_W, SCREEN_H
                        )  # pop(0) estrae il primo elemento della coda
                    if (
                        not spawn_queue
                    ):  # Coda esaurita → tutti i nemici sono stati spawnati
                        wave_state = "WAVE_ACTIVE"

                elif wave_state == "WAVE_ACTIVE":
                    if (
                        len(enemies) == 0
                    ):  # tutti i nemici eliminati allora inizia la pausa
                        wave_state = "WAVE_PAUSE"
                        pause_timer = 0

                elif wave_state == "WAVE_PAUSE":
                    pause_timer += dt
                    if (
                        pause_timer >= settings[16]
                    ):  # dopo tot intervallo di tempo impostato dai settings, la pausa è terminata e si prepara la wave successiva
                        current_wave += 1
                        spawn_queue = build_spawn_queue(
                            calcola_orda(current_wave, sets=settings),
                            settings[13],
                            settings[10],
                            settings[15],
                            settings[12],
                        )
                        spawn_timer = 0
                        wave_state = "WAVE_SPAWN"

                # --- DISEGNO SFONDO ---
                screen.blit(backstage, (0, 0))
                shrine_img = get_shrine_img(
                    shrine_current_hp, settings[9], lista_shrine
                )
                # allinea la base del tempio: tutte le versioni condividono la stessa Y del bordo inferiore
                # anche se hanno altezze diverse (versioni più danneggiate sono più basse)
                screen.blit(
                    shrine_img,
                    (
                        shrine_rect.x,
                        shrine_rect.y
                        + (shrine_75.get_height() - shrine_img.get_height()),
                    ),
                )

                # --- LOGICA NEMICI ---
                # Abbiamo prima disegnato lo sfondo e poi messo questa parte di logica perché
                # per ottimizzare, facciamo un solo ciclo di nemici, e quindi abbiamo messo insieme
                # le parti di logica e disegno dei mostri.
                # In questo ciclo ci sono anche le collisioni con gli oggetti (coltelli e orb)
                for enemy in enemies.copy():
                    # Calcola il centro del nemico (le coordinate enemy[0], enemy[1] sono il bordo superiore sinistro)
                    ecx = (
                        enemy[0] + enemy[4] / 2
                    )  # enemy[4] e enemy[5] sono altezza e larghezza del nemico
                    ecy = enemy[1] + enemy[5] / 2

                    # Vettore direzionale dal nemico al centro del tempio
                    dx = shrine_rect.centerx - ecx
                    dy = shrine_rect.centery - ecy
                    dist = math.hypot(dx, dy)  # distanza euclidea (= sqrt(dx²+dy²))

                    if dist > 60:
                        # Normalizza il vettore (dx/dist, dy/dist) per avere lunghezza 1,
                        # poi moltiplica per la velocità (settings[7]): il nemico si avvicina al tempio
                        enemy[0] += (dx / dist) * enemy[7]
                        enemy[1] += (dy / dist) * enemy[7]
                    else:
                        # Nemico adiacente al tempio: infligge danno continuamente ogni frame
                        if enemy[3] == "slime":
                            shrine_current_hp -= settings[
                                14
                            ]  # danno slime da impostazioni
                        else:
                            shrine_current_hp -= settings[
                                11
                            ]  # danno drago da impostazioni

                    # Avanza l'animazione del nemico (0.15 frame per game-frame)
                    enemy[6] += 0.15
                    if enemy[6] >= 4:
                        enemy[6] = 0  # Loop su 4 frame di animazione

                    # --- logica collisione con altri oggetti ---
                    # Collisione ORB
                    # Cerca se questo nemico è già in cooldown dopo un colpo di orb
                    eid = id(
                        enemy
                    )  # id() restituisce l'indirizzo di memoria dell'oggetto: identificatore univoco
                    gia_colpito = False
                    for entry in orb_hit_cooldowns:
                        if entry[0] == eid:
                            gia_colpito = True
                            break

                    if not gia_colpito:
                        for ox, oy in orb_positions:
                            # Controllo collision circolare: distanza tra centro orb e centro nemico < somma dei raggi
                            if (
                                math.hypot(ox - ecx, oy - ecy)
                                < ORB_RADIUS + max(enemy[4], enemy[5]) / 2
                            ):
                                enemy[2] -= settings[5]  # danno orb
                                enemy[8] = (
                                    HIT_FLASH_DURATION  # Attiva l'overlay rosso di danno
                                )
                                # inserimento nemico nella lista dei già colpiti
                                orb_hit_cooldowns.append([eid, ORB_DAMAGE_COOLDOWN])
                                break  # Un solo colpo per frame, anche se più orb si sovrappongono

                    # rettangolo di collisione dei nemici, la loro hitbox
                    enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[4], enemy[5])

                    # restringimento hitbox dello slime alle sue dimensioni reali(inflate con valori negativi)
                    # gli sprite dello slime sono molto più grandi di come appare sullo schermo, ha molti pixel senza sfondo
                    # move sposta il rettangolo qualche pixel un po' più in basso, per ricentrare lo slime
                    if enemy[3] == "slime":
                        enemy_rect = enemy_rect.inflate(-48, -58).move(0, 29)
                    else:
                        enemy_rect = enemy_rect.inflate(-50, -50)

                    # Collisione COLTELLI
                    for k in knives.copy():
                        # Crea un Rect quadrato centrato sulla posizione del coltello
                        knife_rect = pygame.Rect(
                            k[0] - k[5], k[1] - k[5], k[5] * 2, k[5] * 2
                        )
                        if enemy_rect.colliderect(knife_rect):
                            enemy[2] -= settings[3]  # danno coltelli
                            enemy[8] = HIT_FLASH_DURATION
                            if k in knives:
                                knives.remove(
                                    k
                                )  # il coltello sparisce dopo il primo impatto
                            break  # un coltello colpisce un solo nemico

                    # Rimuove il nemico se i suoi HP sono <= 0
                    if enemy[2] <= 0 and enemy in enemies:
                        enemies.remove(enemy)
                        nemici_uccisi += 1

                # Controllo game over
                if shrine_current_hp <= 0:
                    shrine_current_hp = 0  # Impedisce valori negativi nella barra HP
                    running = False
                    game_over = True
                    # Calcola la durata della partita in secondi per le statistiche
                    durata_sec = (pygame.time.get_ticks() - tempo_inizio) / 1000.0

                # --- DISEGNO COLTELLI ---
                for k in knives:
                    # La superficie del coltello è quadrata con il coltello al centro;
                    # si sottrae hs (half_size) per allineare il centro della superficie alla posizione
                    screen.blit(k[4], (int(k[0]) - k[5], int(k[1]) - k[5]))

                # --- DISEGNO NEMICI ---
                for e in enemies:
                    if e[3] == "slime":
                        img = frames_slime[
                            int(e[6])
                        ]  # Ciclo su 4 frame di animazione slime
                    else:
                        ecx_drag = e[0] + e[4] / 2  # centro X del drago corrente
                        # Il drago guarda verso il tempio: se è alla sua sinistra guarda a destra
                        if ecx_drag < shrine_rect.centerx:
                            img = frames_dragon_right[int(e[6])]
                        else:
                            img = frames_dragon_left[int(e[6])]

                    screen.blit(img, (e[0], e[1]))

                    if e[8] > 0:
                        e[8] -= 1  # Decrementa il contatore dell'overlay rosso
                        # Crea una copia della sprite e la tinge di rosso per indicare il danno subito
                        # BLEND_RGBA_MULT moltiplica ogni pixel per il colore fornito
                        # (255,0,0,120): rosso pieno ma con bassa opacità (120/255) per trasparenza
                        red_overlay = img.copy()
                        red_overlay.fill(
                            (255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT
                        )
                        screen.blit(red_overlay, (e[0], e[1]))

                # --- DISEGNO SAMURAI ---
                # int(frame_index) converte il float in intero per usarlo come indice di lista
                # % len(current_frames) previene IndexError se frame_index supera la lunghezza
                screen.blit(current_frames[int(frame_index)], (px, py))

                # --- DISEGNO ORB ---
                for ox, oy in orb_positions:
                    # Glow: cerchio semitrasparente più grande per effetto luminoso
                    # Viene creata una Surface apposita con alpha per non influenzare il resto
                    glow = pygame.Surface(
                        (ORB_RADIUS * 4, ORB_RADIUS * 4), pygame.SRCALPHA
                    )
                    pygame.draw.circle(
                        glow,
                        (255, 210, 0, 70),
                        (ORB_RADIUS * 2, ORB_RADIUS * 2),
                        ORB_RADIUS * 2,
                    )
                    screen.blit(
                        glow, (int(ox) - ORB_RADIUS * 2, int(oy) - ORB_RADIUS * 2)
                    )
                    # Cerchio principale: giallo pieno
                    # è questo il cerchio rispetto al quale si calcolano le collisioni
                    pygame.draw.circle(
                        screen, (255, 220, 0), (int(ox), int(oy)), ORB_RADIUS
                    )
                    # Piccolo cerchio bianco spostato in alto-sinistra per simulare il riflesso della luce
                    pygame.draw.circle(
                        screen,
                        (255, 255, 210),
                        (int(ox) - 3, int(oy) - 3),
                        ORB_RADIUS // 3,
                    )

            # --- UI ---
            # Barra HP del tempio: sfondo grigio + rettangolo colorato proporzionale agli HP attuali
            pygame.draw.rect(
                screen, (50, 50, 50), (SCREEN_W // 2 - 150, 30, 300, 20)
            )  # Sfondo barra
            pygame.draw.rect(
                screen,
                (0, 200, 255),
                (SCREEN_W // 2 - 150, 30, (shrine_current_hp / settings[9]) * 300, 20),
            )  # Riempimento proporzionale
            txt = font_health.render(
                f"SHRINE HP: {int(shrine_current_hp)}", True, (255, 255, 255)
            )
            screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 55))

            wave_txt = font_small.render(f"WAVE  {current_wave}", True, (255, 220, 80))
            screen.blit(wave_txt, (20, 20))

            # Mostra il contatore nemici solo durante la fase attiva (non durante spawn o pausa)
            if wave_state == "WAVE_ACTIVE":
                rem_txt = font_small.render(
                    f"Nemici: {len(enemies)}", True, (220, 220, 220)
                )
                screen.blit(rem_txt, (20, 48))

            # Countdown visivo al centro schermo durante la pausa tra le wave
            if wave_state == "WAVE_PAUSE":
                # Calcola i secondi rimanenti (arrotondato verso l'alto per non mostrare "0")
                seconds_left = max(1, int((settings[16] - pause_timer) / 1000) + 1)
                ann = font_wave.render(
                    f"WAVE  {current_wave + 1}  in  {seconds_left}...",
                    True,
                    (255, 230, 60),
                )
                screen.blit(
                    ann, (SCREEN_W // 2 - ann.get_width() // 2, SCREEN_H // 2 - 40)
                )

            pygame.display.flip()  # Aggiorna il display con tutto ciò che è stato disegnato

        # ================== GAME OVER: inserimento nickname ==================
        # variabili di inizializzazione
        nickname = ""
        classifica = []
        inserimento_ok = False  # diventa True dopo INVIO
        mostra_top_gameover = False
        switch_rect_go = None

        # ciclo del game_over
        while game_over:
            clock.tick(60)

            # calcolo durata della partita
            # queste variabii servono per la formattazione delle statistiche a schermo
            minuti = int(durata_sec // 60)
            secondi = int(durata_sec % 60)

            # ciclo degli eventi in modalità game_over
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # uscita#
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # uscita#
                        pygame.quit()
                        sys.exit()
                    if not inserimento_ok:
                        # --- fase di digitazione nickname ---
                        # se si preme invio, si salva la partita con il nickname attuale
                        if event.key == pygame.K_RETURN and nickname.strip():
                            # strip() controlla che il nickname non sia solo spazi
                            # salva e carica classifica
                            salva_partita(
                                nickname.strip(),
                                current_wave,
                                nemici_uccisi,
                                minuti,
                                secondi,
                                coltelli_sparati,
                                settings,
                            )
                            classifica = carica_classifica(settings)
                            inserimento_ok = True  # Passa alla schermata di visualizzazione classifica

                        # cancella in inserimento con il backspace
                        elif event.key == pygame.K_BACKSPACE:
                            nickname = nickname[
                                :-1
                            ]  # Rimuove l'ultimo carattere (slicing)

                        # negli altri casi, si tratta della digitazione del nome
                        else:
                            # Aggiunge il carattere al nickname se non supera 8 caratteri
                            # event.unicode contien il carattere testuale associato al tasto
                            # isprintable() filtra i tasti speciali (F1, Enter, ecc.) che non hanno carattere visibile
                            if len(nickname) <= 8 and event.unicode.isprintable():
                                nickname += event.unicode
                    else:
                        # --- fase di visualizzazione risultati ---
                        if event.key == pygame.K_ESCAPE:
                            # uscita#
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_SPACE:
                            game_over = False  # torna al while True esterno

                # Gestisce il click sul pulsante switch solo dopo l'inserimento del nickname
                # alterna tra "ultime 8 partite" e "top 8 per wave" e ricarica la classifica di conseguenza
                if event.type == pygame.MOUSEBUTTONDOWN and inserimento_ok:
                    if switch_rect_go and switch_rect_go.collidepoint(event.pos):
                        mostra_top_gameover = not mostra_top_gameover
                        if mostra_top_gameover:
                            classifica = carica_top_classifica(settings)
                        else:
                            classifica = carica_classifica(settings)

            # --- DISEGNO SFONDO ---
            # Mostra il campo di battaglia congelato al momento del game over
            screen.blit(backstage, (0, 0))
            shrine_img = get_shrine_img(shrine_current_hp, settings[9], lista_shrine)
            screen.blit(
                shrine_img,
                (
                    shrine_rect.x,
                    shrine_rect.y + (shrine_75.get_height() - shrine_img.get_height()),
                ),
            )
            screen.blit(current_frames[int(frame_index)], (px, py))

            # overlay scuro semitrasparente per far risaltare il testo sulla scena di gioco
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # Nero al 160/255 di opacità (~63%)
            screen.blit(overlay, (0, 0))

            cx = SCREEN_W // 2

            if not inserimento_ok:
                # --- SCHERMATA INSERIMENTO NICKNAME ---
                over_txt = font_wave.render("SHRINE DESTROYED!", True, (255, 50, 50))
                screen.blit(over_txt, (cx - over_txt.get_width() // 2, 80))

                stats = [
                    f"Wave raggiunta:   {current_wave}",
                    f"Nemici uccisi:    {nemici_uccisi}",
                    f"Durata partita:   {minuti:02d}:{secondi:02d}",
                    f"Coltelli lanciati: {coltelli_sparati}",
                ]

                # mostro a schermo in colonna le stats della partita
                i = 0
                for riga in stats:
                    s = font_health.render(riga, True, (220, 220, 180))
                    screen.blit(s, (cx - s.get_width() // 2, 200 + i * 44))
                    i += 1
                prompt = font_health.render(
                    "Inserisci il tuo nome e premi INVIO:", True, (255, 230, 80)
                )
                screen.blit(prompt, (cx - prompt.get_width() // 2, 420))

                # box nickname con cursore lampeggiante
                box_rect = pygame.Rect(cx - 180, 465, 360, 44)
                pygame.draw.rect(screen, (60, 60, 80), box_rect, border_radius=6)
                pygame.draw.rect(screen, (200, 200, 100), box_rect, 2, border_radius=6)
                # Il cursore lampeggia ogni 500ms: get_ticks()//500 cambia ogni mezzo secondo,
                # % 2 alterna tra 0 e 1, così il cursore è visibile quando è 0 e invisibile quando è 1
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    cursore = "|"
                else:
                    cursore = ""
                nick_surf = font_health.render(
                    nickname + cursore, True, (255, 255, 255)
                )
                screen.blit(nick_surf, (box_rect.x + 10, box_rect.y + 8))

            else:
                # --- SCHERMATA CLASSIFICA ---
                # disegna_classifica restituisce il rect del pulsante switch (aggiornato ogni frame)
                switch_rect_go = disegna_classifica(
                    screen,
                    font_wave,
                    font_health,
                    font_small,
                    SCREEN_W,
                    SCREEN_H,
                    classifica,
                    nickname,
                    mostra_top_gameover,
                    GameEnd=True,
                )

                # statistiche ultima partita (colonna sinistra)
                tua_txt = font_health.render("La tua partita:", True, (180, 220, 255))
                screen.blit(tua_txt, (70, 130))
                stats = [
                    f"Nickname: {nickname.strip()}",
                    f"Wave raggiunta: {current_wave}",
                    f"Nemici uccisi: {nemici_uccisi}",
                    f"Durata: {minuti:02d}:{secondi:02d}",
                    f"Coltelli lanciati: {coltelli_sparati}",
                ]

                # disegno le stats a sinistra, una sotto l'altra
                i = 0
                for riga in stats:
                    s = font_small.render(riga, True, (210, 210, 210))
                    screen.blit(s, (70, 165 + i * 32))
                    i += 1

            # agiorno lo schermo
            pygame.display.flip()

        # game_over == False → il while True esterno riparte dalla schermata iniziale


# --- avvio del codice dal file in scrittura di python ---
if __name__ == "__main__":
    main()
