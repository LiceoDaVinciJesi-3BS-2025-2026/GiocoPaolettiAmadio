# ⚔️ Crimson Guard

<p align="center">
  <img src="https://github.com/user-attachments/assets/8fa645e7-ea08-4f12-ac9d-fe467cd67a80" width="600" alt="Crimson Guard Logo" />
</p>

In questo gioco, vestirete i panni di un **samurai** con il compito di difendere il tempio centrale da orde di mostri. 
Correte, lanciate coltelli e sfruttate le orb rotanti per sopravvivere il più a lungo possibile!

---

## 🎮 Gameplay & Caratteristiche

### Difendi il Tempio
Proteggi il cuore della mappa dall'attacco nemico. Se il tempio viene distrutto, il gioco finisce.
<p align="center">
  <img src="https://github.com/user-attachments/assets/e17147df-7eeb-4ab0-ac73-1b8cce6b788f" width="500" alt="Gameplay Screen" />
</p>

### Scala la Classifica
Sfidate i vostri record: mostri uccisi, precisione nel lancio dei coltelli e tempo di sopravvivenza. La classifica tiene traccia di tutta la tua storia.
<p align="center">
  <img src="https://github.com/user-attachments/assets/24c2f040-35a5-4a56-999b-2b53a2b7c194" width="500" alt="Classifica Screen" />
</p>

### Personalizzazione Totale
Rendete ogni partita unica modificando i **Settings**. Puoi affrontare un'invasione di slime o proteggerti con 20 sfere letali!
<p align="center">
  <img src="https://github.com/user-attachments/assets/a87a5fec-bfcb-4915-a8b1-257ed9d6a494" width="500" alt="Impostazioni Screen" />
</p>

---

## 🚀 Come iniziare

1. **Fork & Clone**: Fai un fork del progetto e clonalo sul tuo PC.
2. **Navigazione**: Apri il prompt dei comandi e spostati nella cartella del progetto.
3. **Avvio**: Digita il seguente comando per giocare:
   ```bash
   uv run crimsonguard

## Come contribuire
Se volete partecipare anche voi allo sviluppo del gioco, fate un fork della repository, poi dopo aver apportato le modifiche inviate la pull request.  
In ogni caso, per contattarci scrivete ai seguenti indirizzi email:
- leopaoletti09@gmail.com
- sebastianoamadio09@gmail.com



## Crediti
Creatori del gioco: L. Paoletti, A. Sebastiano  
Collaboratore/rifinitore/direttore/capo supremo: A. Diamantini

In aggiunta, ringraziamo anche Reqxel, Elthen's Pixel Art Shop e TotusLotus da itch.io per i loro magnifici asset gratuiti dei mostri.
Di seguito i link per i loro shops e per gli sprite da noi utilizzati:
- [elthen shop](https://elthen.itch.io)
- [sprite degli slime](https://elthen.itch.io/2d-pixel-art-small-slime-sprites)
- [reqxel](https://reqxel.itch.io/)
- [sprite del drago](https://reqxel.itch.io/monster-2d-32)
- [TotusLotus](https://totuslotus.itch.io/)
- [pulsanti](https://totuslotus.itch.io/pixel-ui-buttons)

Nella realizzazione del gioco, abbiamo utilizzato i seguenti software:
- Thonny
- Uv
- CapCut

Inoltre, abbiamo impiegato i seguenti strumenti di Intelligenza Artificiale:
- [Google Gemini](https://gemini.google.com)
- [Claude.ai](https://claude.ai)
- [Chatgpt](https://chatgpt.com/)
- [AdobeImage](https://www.adobe.com/it/express/feature/image/editor)
- [Pixlr](https://pixlr.com/it/image-generator)
- [AutoSprite](https://www.autosprite.io/app)
- [Ludo.ai](https://app.ludo.ai)
- [Use.ai](https://use.ai/it)
- [Deevid](https://deevid.ai/it)
- [Clideo](https://clideo.com/it)
- [Artlist](https://artlist.io/ai)
- [Leonardo.ai](https://leonardo.ai/)


<hr>

# Organizzazione del lavoro

Abbiamo così proceduto nello scriviere il codice del gioco:

- S.A. ha generato e modificato le pixel art del samurai con AutoSprite e Ludo.ai
- L.P. ha scaricato da itch.io gli sheet per i draghi, gli slime e i pulsanti UI 
- L.P. ha generato l'immagine iniziale per lo sfondo dell'arena da Leonardo.ai
- S.A. ha poi rimodificato e raffinato l'immagine dello sfondo con Use.ai
- S.A. ha creato la schermata iniziale da Pixlr
- S.A. ha creato i vari stili del tempio con Use.ai e Artlist
- S.A. ha creato la musica e la GIF pubblicitaria del gioco in cima a questa pagina con Clideo e Deevid
- S.A  ha redatto l'intestazione dei file di gioco  
- L.P. ha eseguito gli import dei moduli python e apportato le modifche necessarie al pyproject.toml
- S.A. ha fatto le seguenti funzioni, con l'ausilio dell'AI Google Gemini e Claude.ai:
    1. load_frames 
    2. rescale_frames 
    3. get_samurai_frames 
    4. get_samurai_hp 
    5. make_knife_surface 
    6. get_shrine_hp 
          
- L.P. ha fatto le funzioni, con l'ausilio di Claude.ai e ChatGpt: 
    1. di gestione del sistema orde, ovvero: spawn_one, calcola_orda, build_spawn_queue 
    2. riguardo salvataggi, classifiche e settings: chiave_modalita, salva_partita, carica_classifica, carica_top_classifica, disegna_classifica, disegna_istruzioni e disegna_settings 

- S.A. si è occupato del comparto audio e del pygame.mixer supervisionando parte del suo codice con claude.ai 
- L.P. ha programmato i pulsanti della UI nella home, le costanti iniziali, i settings 
- S.A. si è occupato del caricamento e del disegno dei frames del samurai, dello shrine, dello sfondo, della home, dei nemici 
- L.P. ha creato tutti font e le scritte del gioco, della home, del game_over e del post-game
- L.P., con la revisione di claude.ai, ha fatto la gestione degli input e degli eventi nella UI
- S.A. ha fatto il rettangolo d'avvio di start del gioco
- L.P si è occupato della gestione del tempo e dei frames con clock.tick
- S.A. con Claude.ai e ChatGpt ha programmato il movimento del personaggio giocante e l'attacco del lancio dei coltelli
- L.P. con Claude.ai ha fatto le orbs rotanti e il sistema di orde e la logica dei nemici
- L.P. con claude.ai ha scritto il codice per il game_over e per le schermate di inserimento del nickname e di classifica
- L.P. e S.A. hanno commentato le rispettive righe di codice scritte da ognuno
- L.P. ha scritto il file_resources per il caricamento dei file per i materiali di gioco
- S.A. e L.P. hanno collaborato insieme per redarre il ReadMe del progetto, prendendo livero spunto da esempi online
- S.A. e L.P. hanno scelto di comune accordo la License del gioco
