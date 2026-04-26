# Piano Implementazione Logica Ricerca Spotify

## Obiettivo

Implementare la logica per recuperare e restituire i payload JSON raw di Spotify intercettando le response di rete del browser, senza trasformarli.

Use case richiesti:

- search: aprire `https://open.spotify.com/search/{query}` e restituire il JSON della response `https://api-partner.spotify.com/pathfinder/v2/query` che contiene `data.searchV2`
- track: aprire `https://open.spotify.com/intl-it/track/{track_id}` e restituire il JSON della response `https://api-partner.spotify.com/pathfinder/v2/query` che contiene `data.trackUnion`
- album: aprire `https://open.spotify.com/intl-it/album/{album_id}` e restituire il JSON della response `https://api-partner.spotify.com/pathfinder/v2/query` che contiene `data.albumUnion`
- artist: aprire `https://open.spotify.com/intl-it/artist/{artist_id}` e restituire il JSON della response `https://api-partner.spotify.com/pathfinder/v2/query` che contiene `data.artistUnion`

Il comportamento desiderato e' semplice: catturare la response giusta e ritornarla cosi' com'e'.

## Stato Attuale

Il repository ha gia' lo skeleton necessario:

- endpoint controller per `search`, `track`, `album`, `artist`
- `SpotifyBrowserClient` placeholder
- `SpotifyMetadataProvider` placeholder
- service separati per i quattro use case
- logger dedicato `spotify_client_logger`
- container con wiring DI gia' presente

Questo permette di implementare la logica quasi tutta nel layer `client/browser`, mantenendo service e provider sottili.

## Decisione Architetturale

La logica principale va concentrata in `octofiestaspotifyapi/client/browser/spotify_browser_client.py`.

Ruoli proposti:

- `SpotifyBrowserClient`: apre la pagina Spotify, osserva le response di rete, filtra quella corretta, legge il body JSON e lo restituisce raw
- `SpotifyMetadataProvider`: espone metodi dedicati a search/track/album/artist delegando al browser client
- `SpotifySearchService`, `SpotifyTrackService`, `SpotifyAlbumService`, `SpotifyArtistService`: pass-through quasi totale
- `SpotifyProxyService`: orchestration minima tra controller e servizi
- `SpotifyController`: nessuna logica Spotify, solo input/output HTTP

Scelta chiave:

- non mappare il payload in modelli dominio per questi endpoint
- ritornare direttamente il JSON Spotify intercettato

Motivo:

- e' esattamente il requisito richiesto
- riduce superficie di bug
- evita di congelare un modello dominio prima di capire l'uso reale dei payload dentro `octo-fiesta`

## Comportamento Funzionale Atteso

### 1. Search

Input API:

- endpoint attuale `GET /spotify/search?q=<query>&limit=<n>`

Flow:

1. normalizzare `q` in formato URL search Spotify sostituendo gli spazi con `+`
2. aprire `https://open.spotify.com/search/{query}`
3. attendere le response della pagina
4. identificare la response `api-partner.spotify.com/pathfinder/v2/query`
5. leggere il JSON della response
6. verificare che il body contenga `data.searchV2`
7. restituire quel JSON raw al chiamante

### 2. Track

Input API:

- endpoint attuale `GET /spotify/tracks/{track_id}`

Flow:

1. aprire `https://open.spotify.com/intl-it/track/{track_id}`
2. attendere le response della pagina
3. filtrare le response `api-partner.spotify.com/pathfinder/v2/query`
4. leggere il JSON della response
5. scegliere quella che contiene `data.trackUnion`
6. restituire quel JSON raw

### 3. Album

Input API:

- endpoint attuale `GET /spotify/albums/{album_id}`

Flow:

1. aprire `https://open.spotify.com/intl-it/album/{album_id}`
2. attendere le response della pagina
3. filtrare le response `api-partner.spotify.com/pathfinder/v2/query`
4. leggere il JSON della response
5. scegliere quella che contiene `data.albumUnion`
6. restituire quel JSON raw

### 4. Artist

Input API:

- endpoint attuale `GET /spotify/artists/{artist_id}`

Flow:

1. aprire `https://open.spotify.com/intl-it/artist/{artist_id}`
2. attendere le response della pagina
3. filtrare le response `api-partner.spotify.com/pathfinder/v2/query`
4. leggere il JSON della response
5. scegliere quella che contiene `data.artistUnion`
6. restituire quel JSON raw

## Design Tecnico Proposto

### `SpotifyBrowserClient`

Metodi da introdurre:

- `search(query: str) -> dict`
- `get_track(track_id: str) -> dict`
- `get_album(album_id: str) -> dict`
- `get_artist(artist_id: str) -> dict`

Helper interni proposti:

- `_open_page()`
- `_capture_matching_response(page, target_url_predicate, body_predicate, timeout_ms)`
- `_safe_json_from_response(response)`
- `_build_search_url(query: str) -> str`

Responsabilita' dell'helper `_capture_matching_response(...)`:

- sottoscriversi agli eventi response di Playwright
- salvare candidate response rilevanti
- per ogni candidate provare a leggere il JSON una sola volta
- applicare i predicati su URL e body
- risolvere appena trova il match giusto
- se non trova nulla entro timeout, alzare un'eccezione di dominio/client chiara

### Strategia di cattura response

Per evitare logica fragile, ogni use case dovrebbe dichiarare due filtri:

- `url predicate`: controlla se l'URL merita analisi
- `body predicate`: controlla se il JSON e' quello voluto

Tabella filtri:

- search:
  - URL contiene `api-partner.spotify.com/pathfinder/v2/query`
  - body contiene `data.searchV2`
- track:
  - URL contiene `api-partner.spotify.com/pathfinder/v2/query`
  - body contiene `data.trackUnion`
- album:
  - URL contiene `api-partner.spotify.com/pathfinder/v2/query`
  - body contiene `data.albumUnion`
- artist:
  - URL contiene `api-partner.spotify.com/pathfinder/v2/query`
  - body contiene `data.artistUnion`

### Gestione browser/sessione

Usare Playwright con persistent context nella cartella gia' prevista:

- `SPOTIFY_SESSION_STORAGE_PATH`

Scelta proposta:

- aprire un browser context persistente riutilizzabile
- creare una nuova page per richiesta
- chiudere la page a fine chiamata
- mantenere il context per riuso sessione/cookie

Tradeoff:

- piu' veloce e stabile di login nuovo per ogni request
- richiede gestione attenta di startup/shutdown del browser client

## Layer Changes Pianificati

### `client/browser/spotify_browser_client.py`

Implementazione principale:

- bootstrap Playwright/browser/context
- navigation alla pagina Spotify corretta
- capture delle response
- ritorno `dict` raw
- logging dettagliato su URL osservati, match trovati, timeout, parse failure

### `provider/spotify_metadata_provider.py`

Metodi da introdurre:

- `search(query: str) -> dict`
- `get_track(track_id: str) -> dict`
- `get_album(album_id: str) -> dict`
- `get_artist(artist_id: str) -> dict`

Ruolo:

- puro adapter tra service e browser client

### `service/spotify_search_service.py`

- delega a provider e restituisce `dict`

### `service/spotify_track_service.py`

- delega a provider e restituisce `dict`

### `service/spotify_album_service.py`

- delega a provider e restituisce `dict`

### `service/spotify_artist_service.py`

- delega a provider e restituisce `dict`

### `service/spotify_proxy_service.py`

- usare davvero i service gia' iniettati invece di tornare placeholder `not_implemented`

### `controller/spotify_controller.py`

Scelta proposta:

- mantenere gli endpoint attuali
- ritornare direttamente il `dict` raw ricevuto dal proxy/service

Decisione su `limit`:

- il parametro `limit` non verra' usato in questa implementazione
- l'endpoint di ricerca restera' centrato solo su `q`
- se il parametro rimane temporaneamente nella signature per compatibilita' con lo skeleton attuale, verra' ignorato esplicitamente e documentato nei log/debug
- nella rifinitura successiva verra' rimosso dall'endpoint per allineare il contratto al comportamento reale

## Error Handling Pianificato

Errori da gestire esplicitamente:

- browser non disponibile o Playwright non inizializzato
- timeout senza response matchante
- response trovata ma body non parsabile come JSON
- pagina Spotify caricata ma nessuna chiamata conforme ai predicati
- response HTTP Spotify non `2xx`

Traduzione errori suggerita:

- timeout/match non trovato -> `504` o `502` lato API, da decidere una volta implementata l'eccezione
- parsing error -> `502`
- startup browser/sessione non valida -> `500`

Scelta consigliata:

- esporre inizialmente errori uniformi come `502 Bad Gateway` per failure di upstream Spotify
- mantenere il dettaglio completo nei log, non nella response pubblica

## Logging Pianificato

Il `spotify_client_logger` deve loggare almeno:

- URL Spotify aperto
- tempo totale di attesa
- numero di response osservate
- URL candidate valutati
- URL finale matchato
- eventuali parse failure JSON
- timeout con tipo di use case (`search`, `track`, `album`, `artist`)

Il `browser_logger` deve loggare almeno:

- apertura/chiusura browser context
- nuova page creata
- eventuali errori Playwright/browser

## Test E Verifica Pianificati

### Verifica manuale minima

1. `GET /health` continua a rispondere `200`
2. `GET /spotify/search?q=vasco+rossi` ritorna un payload con `data.searchV2`
3. `GET /spotify/tracks/{track_id}` ritorna il JSON metadata della track
4. `GET /spotify/albums/{album_id}` ritorna un payload con `data.albumUnion`
5. `GET /spotify/artists/{artist_id}` ritorna un payload con `data.artistUnion`

### Test automatizzabili utili

- unit test sui predicati URL/body
- unit test su helper di query normalization
- unit test sul comportamento quando nessuna response matcha
- unit test su provider/service pass-through

Nota:

- test E2E veri dipenderanno dalla stabilita' del network/browser e sono piu' costosi; vanno dopo l'implementazione base

## Fasi Di Implementazione

### Fase 1. Browser client funzionante per network capture

Obiettivo:

- implementare Playwright lifecycle
- implementare navigazione pagina
- implementare cattura response matchante generica

Deliverable:

- helper riusabile per catturare il JSON corretto da una pagina Spotify

### Fase 2. Wiring search/track/album/artist

Obiettivo:

- implementare metodi provider e service
- eliminare placeholder `not_implemented` nel proxy

Deliverable:

- quattro endpoint metadata funzionanti

### Fase 3. Hardening

Obiettivo:

- migliorare error handling
- migliorare logging
- sistemare semantica endpoint `search` rispetto a `limit`

Deliverable:

- comportamento piu' robusto su timeout, JSON invalidi e no-match

## Decisioni Operative

### 1. `limit` sull'endpoint search

Decisione:

- `limit` non verra' applicato lato server
- il payload search verra' restituito raw senza filtraggio o trimming

### 2. `intl-it` hardcoded

Decisione:

- track, album e artist useranno esplicitamente URL `https://open.spotify.com/intl-it/...`
- il locale non verra' ancora parametrizzato

### 3. `pathfinder/v2/query` multipli sulla stessa pagina

Decisione:

- il browser client ispezionera' tutte le candidate response `pathfinder/v2/query`
- verra' scelta la prima response il cui body soddisfa il predicato richiesto:
  - `data.searchV2`
  - `data.trackUnion`
  - `data.albumUnion`
  - `data.artistUnion`

### 4. Sessione anonima vs autenticata

Decisione:

- il browser usera' un persistent context in `SPOTIFY_SESSION_STORAGE_PATH`
- la sessione verra' considerata parte del runtime locale del servizio
- non verra' implementato in questa fase alcun login automatico
- se servono cookie/sessione validi, saranno caricati dal profilo persistito esistente

### 5. Gestione errore upstream

Decisione:

- tutte le failure di cattura, timeout o parse del payload Spotify saranno esposte come errore uniforme di tipo upstream
- lato HTTP verra' usato `502 Bad Gateway`
- il dettaglio tecnico completo restera' solo nei log

## Raccomandazione Finale

La via definita per questa implementazione e':

- implementare tutta la logica di discovery nel `SpotifyBrowserClient`
- usare predicati URL + body per selezionare la response giusta
- ritornare il JSON raw senza mapping
- lasciare provider e service come pass-through sottili
- usare `intl-it` per track/album/artist
- usare persistent browser context senza login automatico
- esporre gli errori Spotify come `502`

Questo minimizza il codice, resta allineato alla struttura del progetto e prepara bene il passo successivo: riuso di questi payload dentro `octo-fiesta`.
