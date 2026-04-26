# Piano Struttura `octofiestaspotifyapi`

## Obiettivo

Portare `octo-fiesta-spotify-api` a una struttura Python coerente con `navi-fetch`, creando il namespace `octofiestaspotifyapi` e gli stessi layer architetturali principali, ma orientati a una API Spotify generica che poi verra' usata estendendo `octo-fiesta` per integrarsi con Navidrome.

- ricerca contenuti Spotify
- dettaglio singola traccia
- dettaglio album
- dettaglio artista
- download traccia tramite `spotiflac`
- accesso Spotify via browser automation

Il piano copre la struttura, il wiring dei layer, l'allineamento del file `AGENTS.md` dal repository di riferimento e la surface API prevista. Non prevede ancora implementazione completa delle integrazioni.

## Riferimenti Analizzati

### Repository di riferimento: `navi-fetch`

Elementi strutturali emersi:

- package root `navifetch/`
- file di collaborazione `AGENTS.md`
- entrypoint `navifetch/api.py`
- dependency packaging con `pyproject.toml` e `requirements.txt`
- container applicativo `navifetch/container/default_container.py`
- layer separati:
  - `client/`
  - `controller/`
  - `provider/`
  - `service/`
  - `strategy/`
  - `logger/`
  - `model/`
  - `mapper/`

Pattern architetturali rilevanti:

- `api.py` crea `FastAPI`, risolve il controller dal container e include il router
- `DefaultContainer` centralizza env, logging, directory runtime e binding DI
- il controller espone endpoint sottili e delega ai service
- `ProxyService` instrada verso use case specifici
- provider e strategy servono a scegliere come aggregare o risolvere sorgenti esterne

### Dominio funzionale: `octo-fiesta`

Endpoint/use case del dominio sorgente da cui prendere ispirazione per futura integrazione con `octo-fiesta`:

- `rest/search3`: ricerca aggregata
- `rest/getSong`: dettaglio traccia
- `rest/getAlbum`: dettaglio album
- `rest/getArtist`: dettaglio artista
- `rest/stream`: streaming/download on demand
- opzionale futuro: `rest/getTranscodeDecision`

Capacita' di dominio osservate:

- distinzione tra libreria locale e contenuto esterno
- metadata provider dedicato
- download service dedicato
- parsing/normalizzazione ID esterni
- orchestrazione di download + persistenza + successivo accesso locale

## Decisione Architetturale

Creare un package Python nuovo `octofiestaspotifyapi/` che replichi la forma di `navi-fetch`, ma con una specializzazione Spotify singolo-provider invece di una piattaforma multi-provider generica.

Questo significa:

- mantenere gli stessi layer anche se alcuni all'inizio avranno un solo adapter concreto
- evitare di comprimere tutto in pochi file, per non perdere l'allineamento con il repo di riferimento
- predisporre subito l'estensione futura ad altri provider o modalita' di retrieval
- tenere l'API esterna indipendente da Subsonic/Navidrome, cosi' `octo-fiesta` potra' consumarla come backend Spotify separato

## Struttura Target Proposta

```text
octo-fiesta-spotify-api/
├── AGENTS.md
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── octofiestaspotifyapi/
│   ├── __init__.py
│   ├── api.py
│   ├── container/
│   │   ├── __init__.py
│   │   └── default_container.py
│   ├── controller/
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   └── spotify_controller.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── browser/
│   │   │   ├── __init__.py
│   │   │   └── spotify_browser_client.py
│   │   └── download/
│   │       ├── __init__.py
│   │       └── spotiflac_client.py
│   ├── service/
│   │   ├── __init__.py
│   │   ├── spotify_search_service.py
│   │   ├── spotify_track_service.py
│   │   ├── spotify_album_service.py
│   │   ├── spotify_artist_service.py
│   │   ├── spotify_download_service.py
│   │   ├── spotify_proxy_service.py
│   │   └── local_library_service.py
│   ├── provider/
│   │   ├── __init__.py
│   │   ├── spotify_metadata_provider.py
│   │   └── spotify_download_provider.py
│   ├── strategy/
│   │   ├── __init__.py
│   │   └── download_selection_strategy.py
│   ├── mapper/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── spotify_response_mapper.py
│   │   └── domain/
│   │       ├── __init__.py
│   │       └── spotify_metadata_mapper.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── search.py
│   │   │   ├── track.py
│   │   │   ├── album.py
│   │   │   ├── artist.py
│   │   │   └── download.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── song.py
│   │   │   ├── album.py
│   │   │   ├── artist.py
│   │   │   └── download_job.py
│   │   └── external/
│   │       ├── __init__.py
│   │       └── spotify.py
│   └── logger/
│       ├── __init__.py
│       ├── base_logger.py
│       ├── app_logger.py
│       ├── api_logger.py
│       ├── spotify_client_logger.py
│       ├── download_logger.py
│       └── browser_logger.py
└── var/
    ├── log/
    ├── downloads/
    └── tmp/
```

## Responsabilita' Dei Layer

### `api`

- bootstrap FastAPI
- crea app e registra router dal container
- entrypoint `uvicorn octofiestaspotifyapi.api:app`

### `container`

- carica `.env`
- centralizza configurazione runtime
- inizializza cartelle runtime (`var/log`, `var/downloads`, `var/tmp`)
- crea logger, client, provider e service
- esegue il binding delle dipendenze

Nota:

- il container dovra' istanziare logger distinti per area funzionale, non un solo logger globale

### `controller`

- espone endpoint HTTP
- valida input con modelli Pydantic
- non contiene logica Spotify o logica di download

Endpoint iniziali da prevedere:

- `GET /`
- `GET /health`
- `GET /spotify/search`
- `GET /spotify/tracks/{track_id}`
- `GET /spotify/albums/{album_id}`
- `GET /spotify/artists/{artist_id}`
- `POST /spotify/tracks/{track_id}/download`

Nota: questi endpoint sono volutamente espliciti e indipendenti dal contratto Subsonic di `octo-fiesta`. L'idea e' usare questa API come backend Spotify dedicato, che `octo-fiesta` potra' poi consumare per integrarsi con Navidrome senza mescolare le responsabilita'.

### `client`

#### `client/browser/spotify_browser_client.py`

- incapsula accesso via browser automation a Spotify Web
- gestisce sessione, navigazione, selettori e timeout
- restituisce dati grezzi o DTO esterni, non modelli API finali
- usa `spotify_client_logger` per loggare richieste logiche, URL/route visitate, timing, response parsing ed errori

#### `client/download/spotiflac_client.py`

- incapsula invocazione di `spotiflac`
- gestisce command execution, path output, timeout, exit code e stderr
- non decide le policy di business
- usa `download_logger` per comando eseguito, output, exit status e failure reason

### `provider`

- astrazione leggera tra service e implementazioni concrete
- utile anche con un solo provider iniziale, per mantenere allineamento a `navi-fetch`

Provider iniziali:

- `spotify_metadata_provider.py`: ricerca e dettaglio traccia
- `spotify_download_provider.py`: download tramite `spotiflac`

### `service`

- contiene la logica applicativa principale
- orchestra client, provider, mapper e storage locale

Service iniziali:

- `spotify_search_service.py`: ricerca Spotify
- `spotify_track_service.py`: dettaglio traccia/album/artista minimo necessario
- `spotify_album_service.py`: dettaglio album e lista tracce album
- `spotify_artist_service.py`: dettaglio artista e album associati se disponibili
- `spotify_download_service.py`: download, naming file, stato job, controlli idempotenza
- `spotify_proxy_service.py`: entrypoint applicativo comune per controller
- `local_library_service.py`: verifica presenza locale, path finali, eventuale metadata locale

### `strategy`

- all'inizio puo' essere minimale
- serve per evitare hardcode futuro su come scegliere sorgente o modalita' di download

Uso iniziale realistico:

- `download_selection_strategy.py` per decidere fra download gia' presente, retry, refresh o nuova esecuzione

### `mapper`

- converte dati browser/raw in modelli dominio
- converte modelli dominio in payload API coerenti

### `model`

- `api/`: request/response Pydantic esposti dall'API
- `domain/`: oggetti applicativi stabili indipendenti dal trasporto
- `external/`: shape dei dati grezzi Spotify/spotiflac/browser

### `logger`

- stesso pattern di `navi-fetch`
- configurazione centralizzata root logger + file log
- ogni logger scrive su un file diverso sotto `var/log`

Proposta logger iniziali:

- `app_logger.py`: bootstrap applicazione e startup generale su `var/log/app.log`
- `api_logger.py`: request lifecycle, validation e risposta controller su `var/log/api.log`
- `spotify_client_logger.py`: chiamate browser/client Spotify e relative risposte su `var/log/spotify-client.log`
- `download_logger.py`: download `spotiflac`, path file, exit code e retry su `var/log/download.log`
- `browser_logger.py`: sessione browser, login, navigazione e selettori su `var/log/browser.log`

Regole operative del layer logger:

- nessun client o service usa `print`
- ogni componente riceve il logger corretto dal container
- il client Spotify deve loggare sia la chiamata effettuata sia l'esito della risposta o del parsing
- i log sensibili devono essere sanitizzati prima della scrittura

## Surface API Pianificata

### 1. Ricerca

Endpoint:

- `GET /spotify/search?q=<query>&limit=<n>`

Flow:

1. controller valida input
2. `spotify_proxy_service` delega a `spotify_search_service`
3. il service usa `spotify_metadata_provider`
4. il provider usa `spotify_browser_client`
5. il mapper costruisce `Song`/`Album`/`Artist`
6. `spotify_response_mapper` produce la response API

### 2. Dettaglio traccia

Endpoint:

- `GET /spotify/tracks/{track_id}`

Flow:

1. controller valida `track_id`
2. `spotify_track_service` recupera metadata dal provider
3. mapper converte in `model.domain.song`
4. response mapper serializza output

### 3. Dettaglio album

Endpoint:

- `GET /spotify/albums/{album_id}`

Flow:

1. controller valida `album_id`
2. `spotify_album_service` recupera metadata album dal provider
3. mapper converte in `model.domain.album`
4. response mapper serializza output con eventuale lista tracce

### 4. Dettaglio artista

Endpoint:

- `GET /spotify/artists/{artist_id}`

Flow:

1. controller valida `artist_id`
2. `spotify_artist_service` recupera metadata artista dal provider
3. mapper converte in `model.domain.artist`
4. response mapper serializza output con eventuali album principali

### 5. Download traccia

Endpoint:

- `POST /spotify/tracks/{track_id}/download`

Flow:

1. controller valida `track_id`
2. `spotify_download_service` verifica se il file esiste gia'
3. `spotify_download_provider` invoca `spotiflac`
4. `local_library_service` normalizza output path e persistenza locale
5. response mapper restituisce stato job/path/metadata minimo

## Configurazione Da Prevedere

Seguendo il pattern di `navi-fetch`, il container dovrebbe inizializzare almeno queste env:

- `APP_NAME=octofiestaspotifyapi`
- `DEBUG=0`
- `API_HOST=127.0.0.1`
- `API_PORT=8000`
- `API_HOST_PORT=8000`
- `API_CONTAINER_PORT=8000`
- `LOG_DIR=var/log`
- `DOWNLOAD_DIR=var/downloads`
- `TEMP_DIR=var/tmp`
- `SPOTIFY_BROWSER_ENABLED=1`
- `SPOTIFY_BROWSER_TIMEOUT_SECONDS=30`
- `SPOTIFLAC_ENABLED=1`
- `SPOTIFLAC_BINARY=spotiflac`
- `SPOTIFLAC_OUTPUT_DIR=var/downloads`
- `SPOTIFLAC_TIMEOUT_SECONDS=600`
- `SPOTIFY_SESSION_STORAGE_PATH=var/tmp/spotify-session`
- `APP_LOG_FILE=var/log/app.log`
- `API_LOG_FILE=var/log/api.log`
- `SPOTIFY_CLIENT_LOG_FILE=var/log/spotify-client.log`
- `DOWNLOAD_LOG_FILE=var/log/download.log`
- `BROWSER_LOG_FILE=var/log/browser.log`

## Allineamento `AGENTS.md`

Per restare in linea con `navi-fetch`, il piano include anche il recupero del file `AGENTS.md` nel root del repository target.

Scopo:

- mantenere lo stesso contesto operativo per agenti e contributi automatici
- evitare divergenze procedurali tra i due repository

Nota operativa:

- in esecuzione va prima letto `AGENTS.md` di `navi-fetch`
- va poi copiato o adattato minimamente solo se contiene riferimenti troppo specifici al package `navifetch`

Configurazioni da decidere in implementazione:

- se la sessione browser va autenticata con cookie persistiti, profilo locale o login runtime
- se `spotiflac` deve essere processo locale o sidecar/container dedicato
- naming finale file/cartelle per artista/album/traccia

## Dipendenze Previste

Da allineare a `navi-fetch` dove possibile:

- `fastapi`
- `uvicorn`
- `pydantic`
- `python-dotenv`
- `injector`
- `httpx` solo se serve per ancillary HTTP
- `playwright` oppure `camoufox` se il browser client seguira' quel pattern

Possibili dipendenze ulteriori, da confermare in implementazione:

- wrapper o integrazione shell per `spotiflac`
- libreria tagging audio solo se vorrai post-processing file/metadata

## Phasing Proposto

### Fase 1. Bootstrap repository

Obiettivo:

- creare package `octofiestaspotifyapi`
- portare `AGENTS.md` da `navi-fetch`
- aggiungere `pyproject.toml`, `requirements.txt`, `.env.example`
- creare `api.py`, `container`, `logger`
- predisporre Docker e compose nello stesso stile di `navi-fetch`

Deliverable:

- app FastAPI avviabile
- healthcheck funzionante
- dependency wiring base pronto
- file log distinti gia' predisposti sotto `var/log`

### Fase 2. Skeleton dei layer applicativi

Obiettivo:

- introdurre `controller`, `service`, `provider`, `client`, `model`, `mapper`, `strategy`
- definire interfacce minime e classi concrete vuote ma cablate

Deliverable:

- endpoint placeholder documentati
- wiring end-to-end senza logica completa

### Fase 3. Metadata via browser Spotify

Obiettivo:

- implementare browser client per ricerca e dettaglio traccia
- mappare risultati in modelli dominio

Deliverable:

- `GET /spotify/search`
- `GET /spotify/tracks/{track_id}`
- `GET /spotify/albums/{album_id}`
- `GET /spotify/artists/{artist_id}`

### Fase 4. Download tramite `spotiflac`

Obiettivo:

- integrare `spotiflac`
- definire strategia idempotenza, timeout, naming e cartelle

Deliverable:

- `POST /spotify/tracks/{track_id}/download`
- stato download coerente e logging chiaro

### Fase 5. Hardening operativo

Obiettivo:

- error handling consistente
- test base su controller/service/mapper
- configurazione runtime e documentazione
- verifica che logging applicativo e logging Spotify client siano completi e separati

Deliverable:

- smoke test API
- guida setup locale
- gestione failure browser/download

## Tradeoff Principali

### Replica stretta di `navi-fetch` vs adattamento al dominio Spotify

Scelta proposta:

- replicare la struttura e i layer
- non replicare meccanicamente i nomi di use case di Navidrome/Subsonic dove non servono

Motivo:

- il valore e' nella forma architetturale condivisa, non nel copiare endpoint non pertinenti

### Provider layer con un solo provider

Scelta proposta:

- mantenerlo comunque

Motivo:

- preserva l'allineamento col riferimento
- evita rifattorizzazione precoce quando entreranno altri backend o modalita' di accesso

### Browser scraping come client, non come service

Scelta proposta:

- browser automation dentro `client/browser`

Motivo:

- il service deve orchestrare, non conoscere selettori, sessioni o dettagli Playwright

### `spotiflac` come client locale, non come provider diretto

Scelta proposta:

- incapsulare l'esecuzione shell in `client/download/spotiflac_client.py`
- mantenere nel provider/service la logica di business

Motivo:

- migliore testabilita'
- isolamento chiaro tra infrastruttura e orchestrazione

## Rischi Da Gestire

- fragilita' dei selettori/browser automation su Spotify Web
- gestione autenticazione/sessione Spotify
- dipendenza da tool esterno `spotiflac` e relativo runtime
- definizione del contratto output download: stream immediato, file path o job async
- eventuale mismatch tra metadata Spotify e file realmente scaricato

## Raccomandazione Finale

Procedere con una prima implementazione strutturale che allinei il repo a `navi-fetch` fino a Fase 2, ma modellando da subito i tre use case reali:

- search
- get track
- get album
- get artist
- download

Questo ti lascia un'ossatura coerente col riferimento e riduce il rischio di dover rifare package layout e wiring quando inizierai a integrare browser Spotify e `spotiflac`.
