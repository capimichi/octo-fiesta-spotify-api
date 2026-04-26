from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from octofiestaspotifyapi.container.default_container import DefaultContainer
from octofiestaspotifyapi.controller.spotify_controller import SpotifyController # To be created

default_container: DefaultContainer = DefaultContainer.getInstance()

app = FastAPI(
    title="Octo-Fiesta Spotify API",
    description="Spotify API for Octo-Fiesta",
    version="0.1.0",
)

# Placeholder for controller initialization - will be updated in Fase 2
spotify_controller: SpotifyController = default_container.get(SpotifyController)
app.include_router(spotify_controller.router)


if __name__ == "__main__":
    uvicorn.run(
        "octofiestaspotifyapi.api:app",
        host=default_container.get_var("api_host"),
        port=default_container.get_var("api_port"),
        reload=False,
    )